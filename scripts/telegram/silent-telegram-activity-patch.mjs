#!/usr/bin/env node
/**
 * silent-telegram-activity-patch.mjs
 *
 * Makes pi-telegram's thinking/tool activity messages arrive on Telegram with
 * disable_notification: true, so a turn produces exactly ONE notification sound:
 * the final assistant reply. Activity stays fully visible, it just stops pinging.
 *
 * Idempotent. Re-run after every pi-telegram update.
 *
 * Usage:  node silent-telegram-activity-patch.mjs [--dry-run] [--path <dist file>]
 */
import { existsSync, readFileSync, writeFileSync, copyFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const pathArg = args.indexOf("--path") >= 0 ? args[args.indexOf("--path") + 1] : undefined;

const candidates = [
  pathArg,
  process.env.PI_TELEGRAM_ACTIVITY_DIST,
  join(homedir(), ".pi/agent/npm/node_modules/@llblab/pi-telegram/dist/lib/activity-verbosity.js"),
  join(homedir(), ".local/lib/node_modules/@llblab/pi-telegram/dist/lib/activity-verbosity.js"),
  join(homedir(), ".npm-global/lib/node_modules/@llblab/pi-telegram/dist/lib/activity-verbosity.js"),
  join(homedir(), "AppData/Roaming/npm/node_modules/@llblab/pi-telegram/dist/lib/activity-verbosity.js"),
].filter(Boolean);

const target = candidates.find((p) => existsSync(p));
if (!target) {
  console.error("FAIL: pi-telegram dist/lib/activity-verbosity.js not found. Pass --path <file>.");
  process.exit(2);
}

const REASONING_SEND = `                const sent = await deps.sendMessage({
                    chat_id: target.chatId,
                    ...(target.threadId === undefined
                        ? {}
                        : { message_thread_id: target.threadId }),
                    text: body,`;

const REASONING_SEND_PATCHED = `                const sent = await deps.sendMessage({
                    chat_id: target.chatId,
                    disable_notification: true,
                    ...(target.threadId === undefined
                        ? {}
                        : { message_thread_id: target.threadId }),
                    text: body,`;

const TOOL_BODY = `            const body = {
                chat_id: target.chatId,
                ...(target.threadId === undefined
                    ? {}
                    : { message_thread_id: target.threadId }),
            };`;

const TOOL_BODY_PATCHED = `            const body = {
                chat_id: target.chatId,
                disable_notification: true,
                ...(target.threadId === undefined
                    ? {}
                    : { message_thread_id: target.threadId }),
            };`;

let source = readFileSync(target, "utf8");
const silentSends = (source.match(/disable_notification: true/g) ?? []).length;

console.log("file:", target);
console.log("silent activity sends already present:", silentSends);

if (silentSends >= 2) {
  console.log("RESULT: already patched (thinking + tools silent). Nothing to do.");
  process.exit(0);
}

const aCount = source.split(REASONING_SEND).length - 1;
const bCount = source.split(TOOL_BODY).length - 1;
console.log("anchor A (thinking send) matches:", aCount);
console.log("anchor B (tool send) matches:", bCount);

if (aCount !== 1 || bCount !== 1) {
  console.error("FAIL: upstream shape changed (anchors did not match exactly once). Not writing.");
  process.exit(3);
}

source = source.replace(REASONING_SEND, REASONING_SEND_PATCHED).replace(TOOL_BODY, TOOL_BODY_PATCHED);

if (dryRun) {
  console.log("DRY RUN: would write patched file (2 silent activity sends).");
  process.exit(0);
}

const backup = `${target}.pi-silent-orig`;
if (!existsSync(backup)) {
  copyFileSync(target, backup);
  console.log("backup written:", backup);
}
writeFileSync(target, source);
console.log("RESULT: patched. Thinking + tool activity messages now send with disable_notification: true.");
