import assert from 'node:assert/strict'
import test from 'node:test'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { resolveConfig } from '../src/config.js'
import {
  preflightHarnessProfile,
  REQUIRED_HARNESS_SERVICES,
  resolveHarnessProfileEnvironment,
} from '../src/harness-plugin/index.js'
import { resolveRelayRuntimePaths } from '../src/relay-runtime/path-resolver.js'

const dshHome = resolve(tmpdir(), 'dsh-profile-context-home')
const otherHome = resolve(tmpdir(), 'dsh-profile-context-other-home')
const descriptor = resolve(dshHome, 'plugins', 'dsh-relay', 'desktop', 'relay-endpoint.json')

test('native Desktop profileContext supplies profile and home when DSH_PROFILE is absent', () => {
  const baseEnvironment: NodeJS.ProcessEnv = {
    DSH_RELAY_ENDPOINT_DESCRIPTOR: descriptor,
    DSH_RELAY_AUTO_START: 'false',
  }
  const environment = resolveHarnessProfileEnvironment(baseEnvironment, {
    name: 'desktop',
    home: dshHome,
    dir: resolve(dshHome, 'profiles', 'desktop'),
    token: 'native-token-sentinel',
    endpointDescriptorFile: 'native-descriptor-sentinel',
  })
  const paths = resolveRelayRuntimePaths({
    mode: 'embedded',
    env: environment,
    hostIdentity: 'http://127.0.0.1:3080/',
  })

  assert.equal(paths.profile, 'desktop')
  assert.equal(paths.dshHome, dshHome)
  assert.equal(paths.endpointDescriptorFile, descriptor)
  assert.equal(baseEnvironment.DSH_PROFILE, undefined)
  assert.equal(baseEnvironment.DSH_HOME, undefined)
  assert.equal(environment.token, undefined)
  assert.equal(environment.endpointDescriptorFile, undefined)
  assert.equal(JSON.stringify(environment).includes('native-token-sentinel'), false)
  assert.equal(JSON.stringify(environment).includes('native-descriptor-sentinel'), false)
})

test('native profileContext takes precedence over conflicting environment values without mutation', () => {
  const baseEnvironment: NodeJS.ProcessEnv = {
    DSH_PROFILE: 'web',
    DSH_HOME: otherHome,
    DSH_RELAY_ENDPOINT_DESCRIPTOR: descriptor,
  }
  const environment = resolveHarnessProfileEnvironment(baseEnvironment, { name: 'desktop', home: dshHome })
  const paths = resolveRelayRuntimePaths({ mode: 'embedded', env: environment })

  assert.equal(paths.profile, 'desktop')
  assert.equal(paths.dshHome, dshHome)
  assert.equal(baseEnvironment.DSH_PROFILE, 'web')
  assert.equal(baseEnvironment.DSH_HOME, otherHome)
})

test('the same local profile environment resolves runtime paths and relay configuration', () => {
  const environment = resolveHarnessProfileEnvironment({
    DSH_RELAY_ENDPOINT_DESCRIPTOR: descriptor,
  }, { name: 'desktop', home: dshHome })
  const paths = resolveRelayRuntimePaths({ mode: 'embedded', env: environment })
  const relayConfig = resolveConfig({ ...environment, DSH_RELAY_STATE_FILE: paths.stateFile })

  assert.equal(paths.profile, 'desktop')
  assert.equal(relayConfig.stateFile, paths.stateFile)
})

test('Desktop stays blocked without opt-in and is ready only with all required services', () => {
  const environment = resolveHarnessProfileEnvironment({}, { name: 'desktop', home: dshHome })
  const paths = resolveRelayRuntimePaths({ mode: 'embedded', env: environment })

  assert.equal(preflightHarnessProfile({
    profile: paths.profile,
    availableServices: REQUIRED_HARNESS_SERVICES,
  }).code, 'HARNESS_DESKTOP_PROFILE_EXPERIMENTAL_OPT_IN_REQUIRED')
  assert.equal(preflightHarnessProfile({
    profile: paths.profile,
    availableServices: REQUIRED_HARNESS_SERVICES,
    experimentalDesktopOptIn: true,
  }).ready, true)
  assert.equal(preflightHarnessProfile({
    profile: paths.profile,
    availableServices: REQUIRED_HARNESS_SERVICES.filter(service => service !== 'webServer'),
    experimentalDesktopOptIn: true,
  }).code, 'HARNESS_SERVICES_MISSING')
})

test('missing native context retains existing web behavior and unknown profiles remain blocked', () => {
  const webEnvironment = resolveHarnessProfileEnvironment({
    DSH_PROFILE: 'web',
    DSH_HOME: dshHome,
  }, undefined)
  const webPaths = resolveRelayRuntimePaths({ mode: 'embedded', env: webEnvironment })
  assert.equal(webPaths.profile, 'web')
  assert.equal(webPaths.dshHome, dshHome)
  assert.equal(preflightHarnessProfile({
    profile: webPaths.profile,
    availableServices: REQUIRED_HARNESS_SERVICES,
  }).ready, true)

  const unknownEnvironment = resolveHarnessProfileEnvironment({ DSH_PROFILE: 'web' }, {
    name: 'desktop-preview',
    home: dshHome,
  })
  const unknownPaths = resolveRelayRuntimePaths({ mode: 'embedded', env: unknownEnvironment })
  assert.equal(unknownPaths.profile, 'desktop-preview')
  assert.equal(preflightHarnessProfile({
    profile: unknownPaths.profile,
    availableServices: REQUIRED_HARNESS_SERVICES,
    experimentalDesktopOptIn: true,
  }).code, 'HARNESS_WEB_PROFILE_REQUIRED')
})

test('missing native context without an explicit profile fails closed instead of defaulting to web', () => {
  assert.throws(
    () => resolveHarnessProfileEnvironment({}, undefined),
    /profileContext is unavailable and DSH_PROFILE is not explicitly set/iu,
  )
})

test('malformed native context fails closed without exposing token or descriptor values', () => {
  assert.throws(() => resolveHarnessProfileEnvironment({ DSH_PROFILE: 'web' }, {
    name: 'desktop',
    home: 'relative-home',
    token: 'private-token-sentinel',
    endpointDescriptorFile: 'private-descriptor-sentinel',
  }), error => {
    if (!(error instanceof Error)) return false
    assert.equal(error.message.includes('private-token-sentinel'), false)
    assert.equal(error.message.includes('private-descriptor-sentinel'), false)
    return true
  })
})
