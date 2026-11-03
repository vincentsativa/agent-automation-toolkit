#!/usr/bin/env node
/**
 * silent-telegram-activity-test.mjs
 *
 * Functional test for the silent-activity patch: drives the REAL patched
 * pi-telegram activity runtime with fake transport, feeds it a thinking frame
 * and a tool call, and asserts every activity message body carries
 * disable_notification: true.
 *
 * Also asserts the module still emits activity (silence must not mean nothing
 * is sent), and that the patch did not touch any other dist file.
 *
 * Usage: node silent-telegram-activity-test.mjs [--path <dist dir root>]
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const rootArg = args.indexOf("--path") >= 0 ? args[args.indexOf("--path") + 1] : undefined;

const candidates = [
  rootArg,
  process.env.PI_TELEGRAM_DIST,
  join(homedir(), ".pi/agent/npm/node_modules/@llblab/pi-telegram/dist"),
  join(homedir(), ".local/lib/node_modules/@llblab/pi-telegram/dist"),
  join(homedir(), ".npm-global/lib/node_modules/@llblab/pi-telegram/dist"),
  join(homedir(), "AppData/Roaming/npm/node_modules/@llblab/pi-telegram/dist"),
].filter(Boolean);

const dist = candidates.find((p) => p && existsSync(join(p, "lib/activity-verbosity.js")));
if (!dist) {
  console.error("FAIL: pi-telegram dist not found. Pass --path <dist>.");
  process.exit(2);
}

const mod = await import(pathToFileURL(join(dist, "lib/activity-verbosity.js")).href);

const sent = [];
const edited = [];
const target = { chatId: 12345, threadId: 7 };
const authority = { live: true };
let nextId = 100;

const runtime = mod.createTelegramActivityVerbosityRuntime({
  getActivityMode: () => "verbose",
  resolveTarget: () => target,
  captureAuthority: () => authority,
  isAuthorityActive: (a) => Boolean(a && a.live),
  sendMessage: async (body) => {
    sent.push({ kind: "sendMessage", body });
    return { message_id: nextId++ };
  },
  sendRichMessage: async (body) => {
    sent.push({ kind: "sendRichMessage", body });
    return { message_id: nextId++ };
  },
  editMessageText: async (body) => {
    edited.push({ kind: "editMessageText", body });
    return "edited";
  },
  setReasoningTimeout: (cb) => {
    const t = setTimeout(cb, 0);
    t.unref?.();
    return t;
  },
  recordFailure: (op, _e, err) => {
    console.error("FAIL: activity failure during test:", op, err?.message ?? err);
    process.exitCode = 1;
  },
});

const envelope = (n, extra) => ({
  activityId: "act-test",
  sequence: n,
  source: "telegram",
  target,
  timestamp: Date.now(),
  ...extra,
});

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

runtime.accept(envelope(1, { type: "agent-start" }));
runtime.accept(envelope(2, { type: "reasoning-delta", contentIndex: 0, delta: "Reading the patched send path and checking the body fields." }));
await wait(60);
runtime.accept(envelope(3, { type: "reasoning-delta", contentIndex: 0, delta: " Second frame with more reasoning text." }));
await wait(60);
runtime.accept(envelope(4, { type: "reasoning-end", contentIndex: 0, text: "Reading the patched send path and checking the body fields. Second frame with more reasoning text." }));
runtime.accept(envelope(5, { type: "tool-start", toolCallId: "t1", toolName: "bash", args: { cmd: "uptime" } }));
runtime.accept(envelope(6, { type: "tool-end", toolCallId: "t1", toolName: "bash", result: { stdout: "ok" }, isError: false }));
await wait(60);
runtime.accept(envelope(7, { type: "agent-settled" }));
await runtime.waitForIdle();
await wait(30);
runtime.stop();

const sends = sent;
const silent = sends.filter((s) => s.body && s.body.disable_notification === true);
const loud = sends.filter((s) => !s.body || s.body.disable_notification !== true);

console.log("activity messages sent:", sends.length, "| silent:", silent.length, "| would ping:", loud.length);
for (const s of sends) {
  const label = s.kind === "sendMessage"
    ? String(s.body.text ?? "").slice(0, 58).replace(/\s+/g, " ")
    : `rich:${JSON.stringify(s.body.rich_message?.blocks?.[0]?.type ?? "?")}`;
  console.log(`  - ${s.kind}  disable_notification=${s.body.disable_notification === true}  ${label}`);
}
console.log("activity edits (never notify by design):", edited.length);

const checks = [];
checks.push(["activity still emits messages", sends.length >= 2]);
checks.push(["thinking frame sent", sends.some((s) => s.kind === "sendMessage" && String(s.body.text ?? "").includes("Reading the patched"))]);
checks.push(["tool row sent", sends.some((s) => s.kind === "sendRichMessage" || String(s.body.text ?? "").toLowerCase().includes("bash"))]);
checks.push(["every activity send is silent", loud.length === 0 && silent.length === sends.length]);

// The patch must be confined to activity-verbosity.js: the only other
// disable_notification uses upstream are the two routing.js forward copies.
const libs = readdirSync(join(dist, "lib")).filter((f) => f.endsWith(".js"));
const holders = libs.filter((f) => readFileSync(join(dist, "lib", f), "utf8").includes("disable_notification"));
console.log("dist files containing disable_notification:", holders.join(", "));
checks.push(["patch confined to activity-verbosity.js", holders.includes("activity-verbosity.js") && holders.every((f) => f === "activity-verbosity.js" || f === "routing.js")]);

let ok = true;
for (const [name, pass] of checks) {
  console.log(`${pass ? "PASS" : "FAIL"}  ${name}`);
  if (!pass) ok = false;
}
console.log(ok ? "RESULT: PASS" : "RESULT: FAIL");
process.exit(ok ? 0 : 1);
