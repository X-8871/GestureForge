import type { TypertGatewayPort } from '../harness-gateway/index.js'

export interface NativeOwnerPrincipal {
  readonly kind: 'owner'
}

export interface NativePeerScope {
  readonly principal: NativeOwnerPrincipal
  readonly signal: AbortSignal
  dispose(): void | Promise<void>
}

export interface NativeConnectionPort {
  createPeer?: (options: {
    readonly principal: NativeOwnerPrincipal
    readonly interactions: 'none'
  }) => NativePeerScope
}

export interface NativeGatewayPeerAdapter {
  readonly gateway: TypertGatewayPort
  dispose(): Promise<void>
}

/** 为网关请求绑定独立的原生 Peer，并只释放本适配器创建的 Peer。 */
export function createNativeGatewayPeerAdapter(
  gateway: TypertGatewayPort,
  connectionValue: unknown,
  experimentalOwnerPeerOptIn: boolean,
): NativeGatewayPeerAdapter {
  const connection = asRecord(connectionValue)
  const createPeer = connection?.createPeer

  if (createPeer === undefined) {
    if (experimentalOwnerPeerOptIn) {
      throw new Error('HARNESS_NATIVE_OWNER_PEER_UNAVAILABLE: connection.createPeer is required for the explicit owner Peer opt-in')
    }
    return createLegacyGatewayAdapter(gateway)
  }
  if (typeof createPeer !== 'function') {
    throw new Error('HARNESS_NATIVE_OWNER_PEER_INVALID: connection.createPeer is not callable')
  }
  if (!experimentalOwnerPeerOptIn) {
    throw new Error(
      'HARNESS_NATIVE_OWNER_PEER_OPT_IN_REQUIRED: set experimentalOwnerPeerOptIn=true to enable the native owner Peer',
    )
  }

  let peer: NativePeerScope | undefined
  let disposed = false

  const getPeer = (): NativePeerScope => {
    if (disposed) throw new Error('HARNESS_NATIVE_OWNER_PEER_DISPOSED: the Relay-owned Peer has been disposed')
    if (peer !== undefined) {
      assertPeerLive(peer)
      return peer
    }

    let created: unknown
    try {
      created = Reflect.apply(createPeer, connection, [
        { principal: { kind: 'owner' }, interactions: 'none' },
      ])
    } catch {
      throw new Error('HARNESS_NATIVE_OWNER_PEER_CREATE_FAILED: the native connection could not create a Peer')
    }
    if (!isNativeOwnerPeer(created)) {
      disposeInvalidPeer(created)
      throw new Error('HARNESS_NATIVE_OWNER_PEER_INVALID: connection.createPeer returned an invalid owner Peer')
    }
    peer = created
    assertPeerLive(peer)
    return peer
  }

  return {
    gateway: {
      async invoke(request) {
        return gateway.invoke({ ...request, peer: getPeer() })
      },
      async stream(request) {
        return gateway.stream({ ...request, peer: getPeer() })
      },
    },
    async dispose() {
      if (disposed) return
      disposed = true
      const ownedPeer = peer
      peer = undefined
      if (ownedPeer === undefined) return
      try {
        await ownedPeer.dispose()
      } catch {
        throw new Error('HARNESS_NATIVE_OWNER_PEER_DISPOSE_FAILED: the Relay-owned Peer could not be disposed')
      }
    },
  }
}

function createLegacyGatewayAdapter(gateway: TypertGatewayPort): NativeGatewayPeerAdapter {
  return {
    gateway,
    async dispose() {},
  }
}

function assertPeerLive(peer: NativePeerScope): void {
  if (peer.signal.aborted) {
    throw new Error('HARNESS_NATIVE_OWNER_PEER_DISPOSED: the Relay-owned Peer has been disposed')
  }
  if (peer.principal.kind !== 'owner') {
    throw new Error('HARNESS_NATIVE_OWNER_PEER_INVALID: the Relay-owned Peer is not an owner Peer')
  }
}

function isNativeOwnerPeer(value: unknown): value is NativePeerScope {
  try {
    const peer = asRecord(value)
    const principal = asRecord(peer?.principal)
    const signal = asRecord(peer?.signal)
    return principal?.kind === 'owner'
      && typeof signal?.aborted === 'boolean'
      && typeof peer?.dispose === 'function'
  } catch {
    return false
  }
}

function disposeInvalidPeer(value: unknown): void {
  try {
    const dispose = asRecord(value)?.dispose
    if (typeof dispose === 'function') {
      void Promise.resolve(Reflect.apply(dispose, value, [])).catch(() => {})
    }
  } catch {
    // 无效对象的清理错误不应覆盖结构校验错误或泄漏原生错误内容。
  }
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' && value !== null ? value as Record<string, unknown> : undefined
}
