import { isAbsolute, resolve } from 'node:path'

interface NativeProfileContext {
  name?: unknown
  home?: unknown
}

/** 依据公开的 Cordis profileContext 创建独立环境快照。 */
export function resolveHarnessProfileEnvironment(
  baseEnvironment: NodeJS.ProcessEnv,
  nativeContext: unknown,
): NodeJS.ProcessEnv {
  const environment = { ...baseEnvironment }
  if (nativeContext === undefined) {
    const explicitProfile = environment.DSH_PROFILE
    if (explicitProfile === undefined || explicitProfile.length === 0 || explicitProfile !== explicitProfile.trim()) {
      throw new Error('DSH profileContext is unavailable and DSH_PROFILE is not explicitly set')
    }
    return environment
  }

  if (typeof nativeContext !== 'object' || nativeContext === null || Array.isArray(nativeContext)) {
    throw new Error('DSH profileContext must provide a non-empty name and an absolute home path')
  }

  const profileContext = nativeContext as NativeProfileContext
  const name = profileContext.name
  const home = profileContext.home
  if (typeof name !== 'string' || name.length === 0 || name !== name.trim()
    || typeof home !== 'string' || home.length === 0 || home !== home.trim() || !isAbsolute(home)) {
    throw new Error('DSH profileContext must provide a non-empty name and an absolute home path')
  }

  environment.DSH_PROFILE = name
  environment.DSH_HOME = resolve(home)
  return environment
}
