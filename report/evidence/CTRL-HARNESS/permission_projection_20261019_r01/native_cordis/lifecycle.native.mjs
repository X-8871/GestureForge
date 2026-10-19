// tests/in-process-permission-lifecycle.test.ts
import assert from "node:assert/strict";
import test from "node:test";
import { Context, Service } from "file:///D:/DSH/resources/app.asar/dsh/node_modules/@deepseek-ai/cordis/lib/index.js";

// src/permission-gateway/types.ts
var PermissionGatewayError = class extends Error {
  constructor(code, message, details) {
    super(message);
    this.code = code;
    this.details = details;
    this.name = "PermissionGatewayError";
  }
  definitive = true;
  retryable = false;
};

// src/permission-gateway/in-process-permission-provider.ts
var InProcessPermissionProvider = class {
  constructor(resolveSession, presets) {
    this.resolveSession = resolveSession;
    this.presets = presets;
  }
  async readCurrent(sessionId) {
    const session = await this.requireSession(sessionId);
    return this.requirePresets(sessionId).current(session);
  }
  async select(sessionId, preset) {
    const session = await this.requireSession(sessionId);
    try {
      this.requirePresets(sessionId).set(session, preset);
    } catch (error) {
      if (error instanceof PermissionGatewayError) throw error;
      throw new PermissionGatewayError(
        "PERMISSION_DENIED",
        `Harness rejected permission preset ${preset}: ${error instanceof Error ? error.message : String(error)}`,
        { sessionId, expected: preset }
      );
    }
    return { accepted: true };
  }
  requirePresets(sessionId) {
    const presets = typeof this.presets === "function" ? this.presets() : this.presets;
    if (presets === void 0) {
      throw new PermissionGatewayError(
        "PERMISSION_UNAVAILABLE",
        "Harness native permission service is unavailable; task prompt was not submitted",
        { sessionId }
      );
    }
    return presets;
  }
  async requireSession(sessionId) {
    const session = await this.resolveSession(sessionId);
    if (session === void 0) {
      throw new PermissionGatewayError(
        "PERMISSION_UNAVAILABLE",
        `Harness session ${sessionId} is not live in the injected session store`,
        { sessionId }
      );
    }
    return session;
  }
};

// src/permission-gateway/permission-gateway-facade.ts
var permissionPresets = /* @__PURE__ */ new Set([
  "read-only",
  "workspace-write",
  "danger-full-access"
]);
var PermissionGatewayFacade = class {
  constructor(provider) {
    this.provider = provider;
  }
  async current(sessionId) {
    const value = await this.provider.readCurrent(sessionId);
    if (!isPermissionPreset(value)) {
      throw new PermissionGatewayError(
        "PERMISSION_UNAVAILABLE",
        `Harness did not report the current permission preset for ${sessionId}`,
        { sessionId, actual: value }
      );
    }
    return value;
  }
  async select(sessionId, preset) {
    const result = await this.provider.select(sessionId, preset);
    if (!result.accepted) {
      throw new PermissionGatewayError(
        "PERMISSION_DENIED",
        `Harness did not accept permission preset ${preset}`,
        { sessionId, expected: preset }
      );
    }
    return this.confirm(sessionId, preset);
  }
  async confirm(sessionId, expected) {
    const actual = await this.current(sessionId);
    if (actual !== expected) {
      throw new PermissionGatewayError(
        "PERMISSION_DENIED",
        `Harness did not confirm permission preset ${expected}; task prompt was not submitted`,
        { sessionId, expected, actual }
      );
    }
    return actual;
  }
};
function isPermissionPreset(value) {
  return typeof value === "string" && permissionPresets.has(value);
}

// tests/in-process-permission-lifecycle.test.ts
test("\u9759\u6001 preset port \u4ECD\u517C\u5BB9\u65E2\u6709\u8C03\u7528", async () => {
  const session = { preset: "read-only" };
  const calls = [];
  const provider = new InProcessPermissionProvider(
    () => session,
    {
      current(value) {
        calls.push("current");
        return value.preset;
      },
      set(value, preset) {
        calls.push(`set:${preset}`);
        value.preset = preset;
      }
    }
  );
  assert.equal(await provider.readCurrent("session-static"), "read-only");
  assert.deepEqual(await provider.select("session-static", "workspace-write"), { accepted: true });
  assert.deepEqual(calls, ["current", "set:workspace-write"]);
  assert.equal(session.preset, "workspace-write");
});
test("Cordis service \u5378\u8F7D\u548C\u66FF\u6362\u540E\u52A8\u6001 resolver \u4F7F\u7528\u65B0\u5B9E\u4F8B", async () => {
  const session = { preset: "read-only" };
  const calls = [];
  const ctx = new Context();
  const oldFiber = await ctx.plugin(installPermissionPresets("old", calls));
  const oldService = ctx.get("permissionPresets");
  const provider = cordisProvider(ctx, () => session);
  assert.equal(await provider.readCurrent("session-replaced"), "read-only");
  await oldFiber.dispose();
  assert.throws(() => oldService.set(session, "workspace-write"), /projection not registered/u);
  const newFiber = await ctx.plugin(installPermissionPresets("new", calls));
  try {
    assert.deepEqual(await provider.select("session-replaced", "workspace-write"), { accepted: true });
    assert.deepEqual(calls, ["old:current", "new:set:workspace-write"]);
    assert.equal(session.preset, "workspace-write");
  } finally {
    await newFiber.dispose();
  }
});
test("dynamic service \u5378\u8F7D\u540E\u4E0D\u56DE\u9000\u5230\u65E7\u5B9E\u4F8B", async () => {
  const calls = [];
  const ctx = new Context();
  const fiber = await ctx.plugin(installPermissionPresets("old", calls));
  const provider = cordisProvider(ctx, () => ({ preset: "read-only" }));
  assert.equal(await provider.readCurrent("session-no-service"), "read-only");
  await fiber.dispose();
  await assert.rejects(provider.readCurrent("session-no-service"), unavailable);
  await assert.rejects(provider.select("session-no-service", "workspace-write"), unavailable);
  assert.deepEqual(calls, ["old:current"]);
});
test("resolveSession \u7B49\u5F85\u671F\u95F4\u66FF\u6362 Cordis service \u540E current \u8BFB\u53D6\u65B0\u5B9E\u4F8B", async () => {
  const calls = [];
  const ctx = new Context();
  const oldFiber = await ctx.plugin(installPermissionPresets("old", calls));
  const oldService = ctx.get("permissionPresets");
  let resolveSession;
  let signalStarted;
  const started = new Promise((resolve) => {
    signalStarted = resolve;
  });
  const pendingSession = new Promise((resolve) => {
    resolveSession = resolve;
  });
  const provider = cordisProvider(ctx, () => {
    signalStarted();
    return pendingSession;
  });
  const reading = provider.readCurrent("session-race");
  await started;
  await oldFiber.dispose();
  assert.throws(() => oldService.set({ preset: "read-only" }, "workspace-write"), /projection not registered/u);
  const newFiber = await ctx.plugin(installPermissionPresets("new", calls));
  try {
    resolveSession({ preset: "read-only" });
    assert.equal(await reading, "read-only");
    assert.deepEqual(calls, ["new:current"]);
  } finally {
    await newFiber.dispose();
  }
});
test("native set \u62D2\u7EDD\u4FDD\u6301 PERMISSION_DENIED \u4E14\u4E0D\u91CD\u8BD5\u5176\u4ED6\u6743\u9650", async () => {
  const attempted = [];
  const provider = new InProcessPermissionProvider(
    () => ({ preset: "read-only" }),
    {
      current: () => "read-only",
      set(_session, preset) {
        attempted.push(preset);
        throw new Error("native policy denied");
      }
    }
  );
  const gateway = new PermissionGatewayFacade(provider);
  await assert.rejects(gateway.select("session-denied", "workspace-write"), (error) => {
    assert(error instanceof PermissionGatewayError);
    assert.equal(error.code, "PERMISSION_DENIED");
    assert.deepEqual(error.details, { sessionId: "session-denied", expected: "workspace-write" });
    return true;
  });
  assert.deepEqual(attempted, ["workspace-write"]);
});
function cordisProvider(ctx, resolveSession) {
  return new InProcessPermissionProvider(
    resolveSession,
    () => ctx.get("permissionPresets")
  );
}
function installPermissionPresets(label, calls) {
  return (ctx) => {
    const service = new TraceablePermissionPresets(ctx, label, calls);
    return () => service.unregisterProjection();
  };
}
var TraceablePermissionPresets = class extends Service {
  constructor(ctx, label, calls) {
    super(ctx, "permissionPresets");
    this.label = label;
    this.calls = calls;
  }
  registered = true;
  current(session) {
    this.assertRegistered();
    this.calls.push(`${this.label}:current`);
    return session.preset;
  }
  set(session, preset) {
    this.assertRegistered();
    this.calls.push(`${this.label}:set:${preset}`);
    session.preset = preset;
  }
  unregisterProjection() {
    this.registered = false;
  }
  assertRegistered() {
    if (!this.registered) throw new Error("projection not registered");
  }
};
function unavailable(error) {
  assert(error instanceof PermissionGatewayError);
  assert.equal(error.code, "PERMISSION_UNAVAILABLE");
  return true;
}
