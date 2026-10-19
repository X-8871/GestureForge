import {
  PermissionGatewayError,
  type PermissionPreset,
  type PermissionProvider,
  type PermissionSelectionResult,
} from './types.js'

/** Structural view of Harness's native PermissionPresetService. */
export interface InProcessPermissionPresetPort<TSession> {
  current(session: TSession): string
  set(session: TSession, preset: string): void
}

/**
 * Native permission provider over `ctx.sessions` and `ctx.permissionPresets`.
 * The provider appends Harness permission events directly and never sends a
 * slash command or another chat message.
 */
export class InProcessPermissionProvider<TSession> implements PermissionProvider {
  constructor(
    private readonly resolveSession: (sessionId: string) => TSession | undefined | Promise<TSession | undefined>,
    private readonly presets: InProcessPermissionPresetPort<TSession> | (() => InProcessPermissionPresetPort<TSession> | undefined),
  ) {}

  async readCurrent(sessionId: string): Promise<unknown> {
    const session = await this.requireSession(sessionId)
    return this.requirePresets(sessionId).current(session)
  }

  async select(sessionId: string, preset: PermissionPreset): Promise<PermissionSelectionResult> {
    const session = await this.requireSession(sessionId)
    try {
      this.requirePresets(sessionId).set(session, preset)
    } catch (error: unknown) {
      if (error instanceof PermissionGatewayError) throw error
      throw new PermissionGatewayError(
        'PERMISSION_DENIED',
        `Harness rejected permission preset ${preset}: ${error instanceof Error ? error.message : String(error)}`,
        { sessionId, expected: preset },
      )
    }
    return { accepted: true }
  }

  private requirePresets(sessionId: string): InProcessPermissionPresetPort<TSession> {
    // 原生服务可能随配置重载替换，操作时取当前实例，不能继续持有已卸载的权限服务。
    const presets = typeof this.presets === 'function' ? this.presets() : this.presets
    if (presets === undefined) {
      throw new PermissionGatewayError(
        'PERMISSION_UNAVAILABLE',
        'Harness native permission service is unavailable; task prompt was not submitted',
        { sessionId },
      )
    }
    return presets
  }

  private async requireSession(sessionId: string): Promise<TSession> {
    const session = await this.resolveSession(sessionId)
    if (session === undefined) {
      throw new PermissionGatewayError(
        'PERMISSION_UNAVAILABLE',
        `Harness session ${sessionId} is not live in the injected session store`,
        { sessionId },
      )
    }
    return session
  }
}
