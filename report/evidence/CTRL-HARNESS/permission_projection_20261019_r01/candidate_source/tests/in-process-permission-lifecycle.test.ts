import assert from 'node:assert/strict'
import test from 'node:test'
import { Context, Service } from '@deepseek-ai/cordis'
import {
  InProcessPermissionProvider,
  PermissionGatewayError,
  PermissionGatewayFacade,
  type InProcessPermissionPresetPort,
  type PermissionPreset,
} from '../src/permission-gateway/index.js'

interface Session {
  preset: PermissionPreset
}

test('静态 preset port 仍兼容既有调用', async () => {
  const session: Session = { preset: 'read-only' }
  const calls: string[] = []
  const provider = new InProcessPermissionProvider<Session>(
    () => session,
    {
      current(value) {
        calls.push('current')
        return value.preset
      },
      set(value, preset) {
        calls.push(`set:${preset}`)
        value.preset = preset as PermissionPreset
      },
    },
  )

  assert.equal(await provider.readCurrent('session-static'), 'read-only')
  assert.deepEqual(await provider.select('session-static', 'workspace-write'), { accepted: true })
  assert.deepEqual(calls, ['current', 'set:workspace-write'])
  assert.equal(session.preset, 'workspace-write')
})

test('Cordis service 卸载和替换后动态 resolver 使用新实例', async () => {
  const session: Session = { preset: 'read-only' }
  const calls: string[] = []
  const ctx = new Context()
  const oldFiber = await ctx.plugin(installPermissionPresets('old', calls))
  const oldService = ctx.get('permissionPresets') as TraceablePermissionPresets
  const provider = cordisProvider(ctx, () => session)

  assert.equal(await provider.readCurrent('session-replaced'), 'read-only')
  await oldFiber.dispose()
  assert.throws(() => oldService.set(session, 'workspace-write'), /projection not registered/u)

  const newFiber = await ctx.plugin(installPermissionPresets('new', calls))
  try {
    assert.deepEqual(await provider.select('session-replaced', 'workspace-write'), { accepted: true })
    assert.deepEqual(calls, ['old:current', 'new:set:workspace-write'])
    assert.equal(session.preset, 'workspace-write')
  } finally {
    await newFiber.dispose()
  }
})

test('dynamic service 卸载后不回退到旧实例', async () => {
  const calls: string[] = []
  const ctx = new Context()
  const fiber = await ctx.plugin(installPermissionPresets('old', calls))
  const provider = cordisProvider(ctx, () => ({ preset: 'read-only' }))

  assert.equal(await provider.readCurrent('session-no-service'), 'read-only')
  await fiber.dispose()
  await assert.rejects(provider.readCurrent('session-no-service'), unavailable)
  await assert.rejects(provider.select('session-no-service', 'workspace-write'), unavailable)
  assert.deepEqual(calls, ['old:current'])
})

test('resolveSession 等待期间替换 Cordis service 后 current 读取新实例', async () => {
  const calls: string[] = []
  const ctx = new Context()
  const oldFiber = await ctx.plugin(installPermissionPresets('old', calls))
  const oldService = ctx.get('permissionPresets') as TraceablePermissionPresets
  let resolveSession!: (session: Session) => void
  let signalStarted!: () => void
  const started = new Promise<void>(resolve => { signalStarted = resolve })
  const pendingSession = new Promise<Session>(resolve => { resolveSession = resolve })
  const provider = cordisProvider(ctx, () => {
    signalStarted()
    return pendingSession
  })

  const reading = provider.readCurrent('session-race')
  await started
  await oldFiber.dispose()
  assert.throws(() => oldService.set({ preset: 'read-only' }, 'workspace-write'), /projection not registered/u)
  const newFiber = await ctx.plugin(installPermissionPresets('new', calls))
  try {
    resolveSession({ preset: 'read-only' })
    assert.equal(await reading, 'read-only')
    assert.deepEqual(calls, ['new:current'])
  } finally {
    await newFiber.dispose()
  }
})

test('native set 拒绝保持 PERMISSION_DENIED 且不重试其他权限', async () => {
  const attempted: string[] = []
  const provider = new InProcessPermissionProvider<Session>(
    () => ({ preset: 'read-only' }),
    {
      current: () => 'read-only',
      set(_session, preset) {
        attempted.push(preset)
        throw new Error('native policy denied')
      },
    },
  )
  const gateway = new PermissionGatewayFacade(provider)

  await assert.rejects(gateway.select('session-denied', 'workspace-write'), (error: unknown) => {
    assert(error instanceof PermissionGatewayError)
    assert.equal(error.code, 'PERMISSION_DENIED')
    assert.deepEqual(error.details, { sessionId: 'session-denied', expected: 'workspace-write' })
    return true
  })
  assert.deepEqual(attempted, ['workspace-write'])
})

function cordisProvider(
  ctx: Context,
  resolveSession: (sessionId: string) => Session | undefined | Promise<Session | undefined>,
): InProcessPermissionProvider<Session> {
  return new InProcessPermissionProvider(
    resolveSession,
    () => ctx.get('permissionPresets') as InProcessPermissionPresetPort<Session> | undefined,
  )
}

function installPermissionPresets(label: string, calls: string[]) {
  return (ctx: Context) => {
    const service = new TraceablePermissionPresets(ctx, label, calls)
    return () => service.unregisterProjection()
  }
}

class TraceablePermissionPresets extends Service {
  private registered = true

  constructor(ctx: Context, private readonly label: string, private readonly calls: string[]) {
    super(ctx, 'permissionPresets')
  }

  current(session: Session): PermissionPreset {
    this.assertRegistered()
    this.calls.push(`${this.label}:current`)
    return session.preset
  }

  set(session: Session, preset: string): void {
    this.assertRegistered()
    this.calls.push(`${this.label}:set:${preset}`)
    session.preset = preset as PermissionPreset
  }

  unregisterProjection(): void {
    this.registered = false
  }

  private assertRegistered(): void {
    if (!this.registered) throw new Error('projection not registered')
  }
}

function unavailable(error: unknown): boolean {
  assert(error instanceof PermissionGatewayError)
  assert.equal(error.code, 'PERMISSION_UNAVAILABLE')
  return true
}
