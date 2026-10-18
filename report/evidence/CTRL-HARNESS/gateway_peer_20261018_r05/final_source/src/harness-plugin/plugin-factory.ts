import type { HarnessGatewayFacade } from '../harness-gateway/index.js'
import type { PermissionGatewayFacade } from '../permission-gateway/index.js'
import { HARNESS_PLUGIN_NAME } from '../product-identity/index.js'
import {
  createHarnessConfigSchema,
  resolveHarnessPluginConfig,
  type HarnessPluginConfig,
  type HarnessSchemaFactory,
} from './config.js'

export const name = HARNESS_PLUGIN_NAME
export const inject = [
  'agents',
  'connection',
  'typertGateway',
  'webServer',
  'sessions',
  'sessionController',
  'workspaceController',
  'settingsController',
  'agentPresets',
  'permissionPresets',
] as const

export interface HarnessPluginContext {
  connection?: unknown
  typertGateway: unknown
  webServer: unknown
  sessions: unknown
  sessionController: unknown
  workspaceController: unknown
  settingsController: unknown
  agentPresets: unknown
  permissionPresets: unknown
  effect(
    install: () => Promise<() => Promise<void>> | AsyncIterable<() => void | Promise<void>, void, void>,
    label?: string,
  ): unknown
}

export interface EmbeddedRelayAdapters {
  gateway: HarnessGatewayFacade
  permissions: PermissionGatewayFacade
  dispose?(): void | Promise<void>
}

/** Authority teardown deliberately excludes submitted Harness runs. */
export interface EmbeddedRelayAuthority {
  disposeInfrastructure(options: { drainTimeoutMs: number }): Promise<void>
}

export interface HarnessPluginRuntime<TContext extends HarnessPluginContext> {
  schema: HarnessSchemaFactory
  createAdapters(ctx: TContext, config: HarnessPluginConfig): EmbeddedRelayAdapters
  startAuthority(
    ctx: TContext,
    config: HarnessPluginConfig,
    adapters: EmbeddedRelayAdapters,
    options: { signal: AbortSignal },
  ): Promise<EmbeddedRelayAuthority>
}

export interface HarnessPluginDefinition<TContext extends HarnessPluginContext> {
  name: typeof name
  inject: typeof inject
  Config: unknown
  apply(ctx: TContext, config: Partial<HarnessPluginConfig>): void
}

/**
 * Assemble the tree-external Cordis plugin around peer-backed Harness adapters.
 * @param runtime - Thin entry bindings for Schemastery, the Typert Gateway and MCP routing.
 * @returns Conventional Cordis name/inject/Config/apply exports.
 */
export function createHarnessPlugin<TContext extends HarnessPluginContext>(
  runtime: HarnessPluginRuntime<TContext>,
): HarnessPluginDefinition<TContext> {
  return {
    name,
    inject,
    Config: createHarnessConfigSchema(runtime.schema),
    apply(ctx, rawConfig) {
      const config = resolveHarnessPluginConfig(rawConfig)
      const adapters = runtime.createAdapters(ctx, config)
      ctx.effect(async function* () {
        const controller = new AbortController()
        yield () => controller.abort()
        let authority: EmbeddedRelayAuthority
        try {
          authority = await runtime.startAuthority(ctx, config, adapters, { signal: controller.signal })
        } catch (error: unknown) {
          try {
            await adapters.dispose?.()
          } catch {
            // 启动错误优先保留，适配器清理失败不附带潜在敏感数据。
          }
          throw error
        }
        yield async () => {
          let cleanupError: unknown
          try {
            await authority.disposeInfrastructure({ drainTimeoutMs: config.drainTimeoutMs })
          } catch (error: unknown) {
            cleanupError = error
          }
          try {
            await adapters.dispose?.()
          } catch (error: unknown) {
            cleanupError ??= error
          }
          if (cleanupError !== undefined) throw cleanupError
        }
      }, 'harness-relay-mcp.embedded-authority')
    },
  }
}
