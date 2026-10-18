import assert from 'node:assert/strict'
import test from 'node:test'
import { HarnessGatewayFacade, type HarnessGatewayProvider } from '../src/harness-gateway/index.js'
import {
  resolveHarnessPluginConfig,
  createHarnessPlugin,
  preflightHarnessProfile,
  REQUIRED_HARNESS_SERVICES,
  type HarnessPluginConfig,
  type HarnessPluginContext,
  type HarnessSchemaFactory,
} from '../src/harness-plugin/index.js'
import { PermissionGatewayFacade, type PermissionProvider } from '../src/permission-gateway/index.js'

test('Cordis plugin factory exposes native injects and disposes infrastructure without cancelling runs', async () => {
  const schema = new RecordingSchemaFactory()
  const lifecycle: string[] = []
  let installer: (() => Promise<() => Promise<void>> | AsyncIterable<() => void | Promise<void>, void, void>) | undefined
  const ctx: HarnessPluginContext = {
    typertGateway: {},
    webServer: {},
    sessions: {},
    sessionController: {},
    workspaceController: {},
    settingsController: {},
    agentPresets: {},
    permissionPresets: {},
    effect(install) {
      installer = install
      return () => {}
    },
  }
  const gateway = new HarnessGatewayFacade(new Proxy({}, {
    get: () => async () => { throw new Error('not used') },
  }) as HarnessGatewayProvider)
  const permissions = new PermissionGatewayFacade(new Proxy({}, {
    get: () => async () => { throw new Error('not used') },
  }) as PermissionProvider)
  const plugin = createHarnessPlugin({
    schema,
    createAdapters: () => ({ gateway, permissions }),
    async startAuthority() {
      lifecycle.push('started')
      return {
        async disposeInfrastructure({ drainTimeoutMs }) {
          lifecycle.push(`disposed:${drainTimeoutMs}`)
        },
      }
    },
  })

  assert.equal(plugin.name, 'harness-relay-mcp')
  assert.deepEqual(plugin.inject, [
    'agents',
    'typertGateway',
    'webServer',
    'sessions',
    'sessionController',
    'workspaceController',
    'settingsController',
    'agentPresets',
    'permissionPresets',
  ])
  assert.equal(schema.fields.includes('token'), false)
  assert.deepEqual(schema.fields, [
    'route',
    'stateDirectory',
    'tokenFile',
    'experimentalDesktopOptIn',
    'requestBodyLimitBytes',
    'maxConcurrency',
    'rateLimitPerMinute',
    'drainTimeoutMs',
  ])
  assert.equal((schema.shape.experimentalDesktopOptIn as ChainSchema).defaultValue, false)
  assert.equal(resolveHarnessPluginConfig({}).experimentalDesktopOptIn, false)
  assert.equal(resolveHarnessPluginConfig({ experimentalDesktopOptIn: false }).experimentalDesktopOptIn, false)
  assert.equal(resolveHarnessPluginConfig({ experimentalDesktopOptIn: true }).experimentalDesktopOptIn, true)

  plugin.apply(ctx, { drainTimeoutMs: 750 })
  assert(installer !== undefined)
  const effect = installer()
  assert(Symbol.asyncIterator in effect)
  const iterator = effect[Symbol.asyncIterator]()
  const cancel = await iterator.next()
  assert.equal(cancel.done, false)
  const dispose = await iterator.next()
  assert.equal(dispose.done, false)
  await dispose.value()
  assert.deepEqual(lifecycle, ['started', 'disposed:750'])
})

test('desktop opt-in rejects explicitly supplied non-boolean runtime values', () => {
  const invalidValues: unknown[] = ['true', 'false', 1, null, {}, []]
  for (const value of invalidValues) {
    const input = { experimentalDesktopOptIn: value } as unknown as Partial<HarnessPluginConfig>
    assert.throws(
      () => resolveHarnessPluginConfig(input),
      /experimentalDesktopOptIn must be a boolean/iu,
    )
  }
})

test('Cordis plugin factory exposes an abort disposer before authority startup settles', async () => {
  let installer: (() => Promise<() => Promise<void>> | AsyncIterable<() => void | Promise<void>, void, void>) | undefined
  const ctx: HarnessPluginContext = {
    typertGateway: {}, webServer: {}, sessions: {}, sessionController: {},
    workspaceController: {}, settingsController: {}, agentPresets: {}, permissionPresets: {},
    effect(install) { installer = install; return () => {} },
  }
  const gateway = new HarnessGatewayFacade(new Proxy({}, {
    get: () => async () => { throw new Error('not used') },
  }) as HarnessGatewayProvider)
  const permissions = new PermissionGatewayFacade(new Proxy({}, {
    get: () => async () => { throw new Error('not used') },
  }) as PermissionProvider)
  const plugin = createHarnessPlugin({
    schema: new RecordingSchemaFactory(),
    createAdapters: () => ({ gateway, permissions }),
    async startAuthority(_ctx, _config, _adapters, { signal }) {
      await new Promise<void>((_resolve, reject) => {
        signal.addEventListener('abort', () => reject(new Error('startup cancelled')), { once: true })
      })
      throw new Error('unreachable')
    },
  })
  plugin.apply(ctx, {})
  assert(installer !== undefined)
  const effect = installer()
  assert(Symbol.asyncIterator in effect)
  const iterator = effect[Symbol.asyncIterator]()
  const cancel = await iterator.next()
  assert.equal(cancel.done, false)
  const pendingStartup = iterator.next()
  await cancel.value()
  await assert.rejects(pendingStartup, /startup cancelled/iu)
})

test('headless profile preflight blocks before profile mutation', () => {
  assert.deepEqual(preflightHarnessProfile({ profile: 'headless', availableServices: [] }), {
    ready: false,
    code: 'HARNESS_WEB_PROFILE_REQUIRED',
    missingServices: [],
    message: 'DSH Relay requires the Harness web profile; received headless',
  })
  assert.deepEqual(preflightHarnessProfile({
    profile: 'web',
    availableServices: [
      'agents', 'typertGateway', 'sessions', 'sessionController', 'workspaceController',
      'settingsController', 'agentPresets', 'permissionPresets',
    ],
  }), {
    ready: false,
    code: 'HARNESS_SERVICES_MISSING',
    missingServices: ['webServer'],
    message: 'Harness web profile is missing required services: webServer',
  })
  assert.equal(preflightHarnessProfile({
    profile: 'web',
    availableServices: [
      'agents', 'typertGateway', 'webServer', 'sessions', 'sessionController', 'workspaceController',
      'settingsController', 'agentPresets', 'permissionPresets',
    ],
  }).ready, true)
})

test('desktop profile requires explicit experimental opt-in and every Harness service', () => {
  const allServices = [
    'agents', 'typertGateway', 'webServer', 'sessions', 'sessionController', 'workspaceController',
    'settingsController', 'agentPresets', 'permissionPresets',
  ]
  assert.deepEqual(preflightHarnessProfile({ profile: 'desktop', availableServices: allServices }), {
    ready: false,
    code: 'HARNESS_DESKTOP_PROFILE_EXPERIMENTAL_OPT_IN_REQUIRED',
    missingServices: [],
    message: 'DSH Relay desktop profile is experimental and requires explicit experimentalDesktopOptIn=true',
  })
  assert.deepEqual(preflightHarnessProfile({
    profile: 'desktop',
    availableServices: allServices,
    experimentalDesktopOptIn: true,
  }), {
    ready: true,
    code: 'READY',
    missingServices: [],
    message: 'Harness desktop profile passed experimental preflight; protocol compatibility is unverified',
  })
  assert.deepEqual(preflightHarnessProfile({
    profile: 'desktop',
    availableServices: allServices.filter(service => service !== 'webServer'),
    experimentalDesktopOptIn: true,
  }), {
    ready: false,
    code: 'HARNESS_SERVICES_MISSING',
    missingServices: ['webServer'],
    message: 'Harness desktop profile is missing required services: webServer',
  })
})

test('desktop opt-in does not permit headless or unknown profiles', () => {
  const probe = { availableServices: REQUIRED_HARNESS_SERVICES, experimentalDesktopOptIn: true }
  assert.equal(preflightHarnessProfile({ ...probe, profile: 'headless' }).code, 'HARNESS_WEB_PROFILE_REQUIRED')
  assert.equal(preflightHarnessProfile({ ...probe, profile: 'desktop-preview' }).code, 'HARNESS_WEB_PROFILE_REQUIRED')
})

class RecordingSchemaFactory implements HarnessSchemaFactory {
  readonly fields: string[] = []
  shape: Record<string, unknown> = {}

  string(): ChainSchema {
    return new ChainSchema()
  }

  natural(): ChainSchema {
    return new ChainSchema()
  }

  boolean(): ChainSchema {
    return new ChainSchema()
  }

  object(shape: Record<string, unknown>): unknown {
    this.shape = shape
    this.fields.push(...Object.keys(shape))
    return shape
  }
}

class ChainSchema {
  defaultValue: string | number | boolean | undefined
  default(value: string | number | boolean): ChainSchema { this.defaultValue = value; return this }
  min(_value: number): ChainSchema { return this }
  max(_value: number): ChainSchema { return this }
}
