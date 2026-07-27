#!/usr/bin/env node
/**
 * PostToolUse: light feedback after TS/JS edits (non-blocking advice).
 * Exits 0 always so Claude is not hard-stopped; prints hints to stderr.
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

function collectPaths(input) {
  const paths = new Set();
  const walk = (v) => {
    if (!v) return;
    if (typeof v === "string" && /\.(ts|tsx|js|jsx|mjs|cjs)$/i.test(v)) paths.add(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (typeof v === "object") {
      for (const [k, val] of Object.entries(v)) {
        if (/path|file|target/i.test(k) && typeof val === "string") walk(val);
        else walk(val);
      }
    }
  };
  walk(input);
  if (process.env.CLAUDE_FILE) walk(process.env.CLAUDE_FILE);
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
    payload = {};
  }
}

const files = collectPaths(payload).filter((f) => fs.existsSync(f));
const rootTs = files.filter(
  (f) => f.includes(`${path.sep}src${path.sep}`) || f.startsWith("src/") || f.startsWith("src\\"),
);

if (rootTs.length && fs.existsSync("eslint.config.js")) {
  try {
    execSync(`npx eslint --max-warnings 0 ${rootTs.map((f) => `"${f}"`).join(" ")}`, {
      stdio: ["ignore", "pipe", "pipe"],
      timeout: 60000,
    });
    console.error("[hook:post-edit-lint] eslint ok:", rootTs.join(", "));
  } catch (e) {
    const out = (e.stdout || e.stderr || "").toString().slice(0, 2000);
    console.error("[hook:post-edit-lint] eslint issues (non-blocking):\n" + out);
  }
}

process.exit(0);
