import assert from 'node:assert/strict'
import test from 'node:test'
import type { TypertGatewayPort, TypertInvokeRequest } from '../src/harness-gateway/typert-harness-gateway.js'
import {
  createNativeGatewayPeerAdapter,
  type NativePeerScope,
} from '../src/harness-plugin/native-gateway-peer.js'

test('旧网关运行时没有 createPeer 时保留原请求路径', async () => {
  const requests: TypertInvokeRequest[] = []
  const gateway: TypertGatewayPort = {
    async invoke(request) { requests.push(request); return { ok: true } },
    async stream(request) { requests.push(request); return emptyStream() },
  }
  const adapter = createNativeGatewayPeerAdapter(gateway, {}, false)
  const request: TypertInvokeRequest = { namespace: 'workspace', method: 'list', args: {} }

  assert.equal(adapter.gateway, gateway)
  assert.deepEqual(await adapter.gateway.invoke(request), { ok: true })
  assert.equal(requests[0], request)
  await adapter.dispose()
})

test('原生 createPeer 存在而 opt-in 关闭时明确拒绝且不创建 owner Peer', () => {
  let createCalls = 0
  const connection = {
    createPeer() { createCalls += 1; return makePeer() },
  }

  assert.throws(
    () => createNativeGatewayPeerAdapter(createNativeGateway(), connection, false),
    /HARNESS_NATIVE_OWNER_PEER_OPT_IN_REQUIRED/iu,
  )
  assert.equal(createCalls, 0)
})

test('原生 connection 创建独立 owner Peer，invoke 与 stream 共用并覆盖调用者注入的 peer', async () => {
  const controller = new AbortController()
  let createdPeer: NativePeerScope | undefined
  let createCalls = 0
  let browserPeerReads = 0
  const connection = {
    get browserPeer() { browserPeerReads += 1; throw new Error('browserPeer must not be read') },
    createPeer(options: { principal: { kind: 'owner' }; interactions: 'none' }) {
      createCalls += 1
      assert.deepEqual(options, { principal: { kind: 'owner' }, interactions: 'none' })
      createdPeer = makePeer(controller)
      return createdPeer
    },
  }
  const nativeGateway = createNativeGateway()
  const adapter = createNativeGatewayPeerAdapter(nativeGateway, connection, true)
  const callerPeer = { signal: new AbortController().signal, principal: { kind: 'untrusted' } }
  const invokeSignal = new AbortController().signal
  const streamSignal = new AbortController().signal
  const invokeRequest: TypertInvokeRequest = {
    namespace: 'workspace', method: 'list', args: { keep: 'same' }, signal: invokeSignal, peer: callerPeer,
  }
  const streamRequest: TypertInvokeRequest = {
    namespace: 'session', method: 'follow', args: { cursor: 7 }, signal: streamSignal, peer: callerPeer,
  }

  assert.deepEqual(await adapter.gateway.invoke(invokeRequest), { accepted: true })
  const stream = await adapter.gateway.stream(streamRequest)
  assert.deepEqual(await stream[Symbol.asyncIterator]().next(), { done: true, value: undefined })
  assert.equal(createCalls, 1)
  assert.equal(browserPeerReads, 0)
  assert.equal(nativeGateway.requests[0]?.peer, createdPeer)
  assert.equal(nativeGateway.requests[0]?.peer === callerPeer, false)
  assert.equal(nativeGateway.requests[0]?.signal, invokeSignal)
  assert.deepEqual(nativeGateway.requests[0], { ...invokeRequest, peer: createdPeer })
  assert.equal(nativeGateway.requests[1]?.peer, createdPeer)
  assert.equal(nativeGateway.requests[1]?.signal, streamSignal)
  assert.deepEqual(nativeGateway.requests[1], { ...streamRequest, peer: createdPeer })

  await adapter.dispose()
  assert.equal(controller.signal.aborted, true)
  assert.equal(browserPeerReads, 0)
})

test('native-like gateway reproduces missing-peer failure before adapter and accepts the real created Peer after', async () => {
  const nativeGateway = createNativeGateway()
  const request: TypertInvokeRequest = { namespace: 'workspace', method: 'list', args: {} }

  await assert.rejects(nativeGateway.invoke(request), /Cannot read properties of undefined \(reading 'signal'\)/u)
  const adapter = createNativeGatewayPeerAdapter(nativeGateway, {
    createPeer: () => makePeer(),
  }, true)
  assert.deepEqual(await adapter.gateway.invoke(request), { accepted: true })
  await adapter.dispose()
})

test('disposed owner Peer blocks future invoke and stream, releases only itself, and never cancels a session', async () => {
  const controller = new AbortController()
  let ownDisposeCalls = 0
  let browserPeerReads = 0
  let cancelSessionCalls = 0
  let gatewayCalls = 0
  const peer: NativePeerScope = {
    principal: { kind: 'owner' },
    signal: controller.signal,
    async dispose() { ownDisposeCalls += 1; controller.abort() },
  }
  const gateway: TypertGatewayPort & { cancelSession(): Promise<void> } = {
    async invoke(request) { gatewayCalls += 1; assertNativePeer(request); return { accepted: true } },
    async stream(request) { gatewayCalls += 1; assertNativePeer(request); return emptyStream() },
    async cancelSession() { cancelSessionCalls += 1 },
  }
  const connection = {
    get browserPeer() { browserPeerReads += 1; return makePeer() },
    createPeer: () => peer,
  }
  const adapter = createNativeGatewayPeerAdapter(gateway, connection, true)
  const request: TypertInvokeRequest = { namespace: 'session', method: 'list', args: {} }
  await adapter.gateway.invoke(request)
  assert.equal(gatewayCalls, 1)

  await adapter.dispose()
  await adapter.dispose()
  await assert.rejects(adapter.gateway.invoke(request), /HARNESS_NATIVE_OWNER_PEER_DISPOSED/iu)
  await assert.rejects(adapter.gateway.stream(request), /HARNESS_NATIVE_OWNER_PEER_DISPOSED/iu)

  assert.equal(ownDisposeCalls, 1)
  assert.equal(browserPeerReads, 0)
  assert.equal(cancelSessionCalls, 0)
  assert.equal(gatewayCalls, 1)
})

test('createPeer errors are sanitized and do not expose credential-like details', async () => {
  const sentinel = 'secret-token-should-not-escape'
  const adapter = createNativeGatewayPeerAdapter(createNativeGateway(), {
    createPeer() { throw new Error(`native failure ${sentinel}`) },
  }, true)

  await assert.rejects(adapter.gateway.invoke({ namespace: 'settings', method: 'describe', args: {} }), error => {
    assert.match((error as Error).message, /HARNESS_NATIVE_OWNER_PEER_CREATE_FAILED/iu)
    assert.equal((error as Error).message.includes(sentinel), false)
    return true
  })
  await adapter.dispose()
})

test('显式批准 owner Peer 但缺少原生工厂时拒绝，不降级到旧路径', () => {
  for (const connection of [undefined, {}, { createPeer: undefined }]) {
    assert.throws(() => createNativeGatewayPeerAdapter(createNativeGateway(), connection, true),
      /HARNESS_NATIVE_OWNER_PEER_UNAVAILABLE/u)
  }
})

test('未使用的适配器先释放后不再创建 Peer', async () => {
  let calls = 0
  const adapter = createNativeGatewayPeerAdapter(createNativeGateway(), {
    createPeer() { calls += 1; return makePeer() },
  }, true)
  await adapter.dispose()
  await assert.rejects(adapter.gateway.invoke({ namespace: 'session', method: 'list', args: {} }),
    /HARNESS_NATIVE_OWNER_PEER_DISPOSED/u)
  assert.equal(calls, 0)
})

test('原生 Peer 被外部生命周期释放后不能继续调用网关', async () => {
  const controller = new AbortController()
  const nativeGateway = createNativeGateway()
  const adapter = createNativeGatewayPeerAdapter(nativeGateway, { createPeer: () => makePeer(controller) }, true)
  await adapter.gateway.invoke({ namespace: 'session', method: 'list', args: {} })
  controller.abort()
  await assert.rejects(adapter.gateway.stream({ namespace: 'session', method: 'follow', args: {} }),
    /HARNESS_NATIVE_OWNER_PEER_DISPOSED/u)
  assert.equal(nativeGateway.requests.length, 1)
  await adapter.dispose()
})

function createNativeGateway(): TypertGatewayPort & { requests: TypertInvokeRequest[] } {
  const requests: TypertInvokeRequest[] = []
  return {
    requests,
    async invoke(request) {
      requests.push(request)
      assertNativePeer(request)
      return { accepted: true }
    },
    async stream(request) {
      requests.push(request)
      assertNativePeer(request)
      return emptyStream()
    },
  }
}

function assertNativePeer(request: TypertInvokeRequest): asserts request is TypertInvokeRequest & { peer: NativePeerScope } {
  if (request.peer === undefined) throw new TypeError("Cannot read properties of undefined (reading 'signal')")
  const peer = request.peer as NativePeerScope
  if (peer.signal.aborted) throw new Error('native peer is disposed')
  if (peer.principal.kind !== 'owner') throw new Error('native peer principal is not owner')
}

function makePeer(controller = new AbortController()): NativePeerScope {
  return {
    ctx: {},
    principal: { kind: 'owner' },
    signal: controller.signal,
    async dispose() { controller.abort() },
  } as NativePeerScope
}

function emptyStream(): AsyncIterable<unknown> {
  return { async *[Symbol.asyncIterator]() {} }
}
