export const REQUIRED_HARNESS_SERVICES = [
  'agents',
  'typertGateway',
  'webServer',
  'sessions',
  'sessionController',
  'workspaceController',
  'settingsController',
  'agentPresets',
  'permissionPresets',
] as const

export interface HarnessProfileProbe {
  profile: string
  availableServices: readonly string[]
  experimentalDesktopOptIn?: boolean
}

export interface HarnessProfilePreflight {
  ready: boolean
  code: 'READY' | 'HARNESS_WEB_PROFILE_REQUIRED' | 'HARNESS_DESKTOP_PROFILE_EXPERIMENTAL_OPT_IN_REQUIRED' | 'HARNESS_SERVICES_MISSING'
  missingServices: string[]
  message: string
}

/**
 * Fail before profile mutation when the target cannot host the Relay bundle.
 * @param probe - Profile and service facts collected by setup/doctor.
 * @returns Machine-readable preflight result.
 */
export function preflightHarnessProfile(probe: HarnessProfileProbe): HarnessProfilePreflight {
  if (probe.profile === 'desktop' && probe.experimentalDesktopOptIn !== true) {
    return {
      ready: false,
      code: 'HARNESS_DESKTOP_PROFILE_EXPERIMENTAL_OPT_IN_REQUIRED',
      missingServices: [],
      message: 'DSH Relay desktop profile is experimental and requires explicit experimentalDesktopOptIn=true',
    }
  }
  if (probe.profile !== 'web' && probe.profile !== 'desktop') {
    return {
      ready: false,
      code: 'HARNESS_WEB_PROFILE_REQUIRED',
      missingServices: [],
      message: `DSH Relay requires the Harness web profile; received ${probe.profile}`,
    }
  }
  const available = new Set(probe.availableServices)
  const missingServices = REQUIRED_HARNESS_SERVICES.filter(service => !available.has(service))
  if (missingServices.length > 0) {
    return {
      ready: false,
      code: 'HARNESS_SERVICES_MISSING',
      missingServices,
      message: `Harness ${probe.profile} profile is missing required services: ${missingServices.join(', ')}`,
    }
  }
  return {
    ready: true,
    code: 'READY',
    missingServices: [],
    message: probe.profile === 'web'
      ? 'Harness web profile can host DSH Relay'
      : 'Harness desktop profile passed experimental preflight; protocol compatibility is unverified',
  }
}
