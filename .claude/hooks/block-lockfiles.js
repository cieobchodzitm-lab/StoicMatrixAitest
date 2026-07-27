#!/usr/bin/env node
/**
 * PreToolUse: block direct edits to package lockfiles.
 */
const fs = require("fs");

const LOCK_RE =
  /(^|[\\/])(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|Pipfile\.lock|composer\.lock)$/i;

function collectPaths(input) {
  const paths = new Set();
  const walk = (v) => {
    if (!v) return;
    if (typeof v === "string") {
      if (v.length < 512) paths.add(v);
      return;
    }
    if (Array.isArray(v)) return v.forEach(walk);
    if (typeof v === "object") {
      for (const [k, val] of Object.entries(v)) {
        if (/path|file|target/i.test(k) && typeof val === "string") paths.add(val);
        else walk(val);
      }
    }
  };
  walk(input);
  for (const a of process.argv.slice(2)) paths.add(a);
  if (process.env.CLAUDE_FILE) paths.add(process.env.CLAUDE_FILE);
  return [...paths];
}

let raw = "";
try {
  if (!process.stdin.isTTY) raw = fs.readFileSync(0, "utf8");
} catch {
  /* ignore */
}

let payload = {};
if (raw.trim()) {
  try {
    payload = JSON.parse(raw);
  } catch {
    payload = { text: raw };
  }
}

const hits = collectPaths(payload).filter((p) => LOCK_RE.test(p.replace(/\\/g, "/")));
if (hits.length) {
  console.error(
    "[hook:block-lockfiles] Do not hand-edit lockfiles:\n" +
      hits.map((h) => "  - " + h).join("\n") +
      "\nUse npm/pnpm/yarn/pip tooling instead.",
  );
  process.exit(2);
}
process.exit(0);
