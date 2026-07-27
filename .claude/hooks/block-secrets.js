#!/usr/bin/env node
/**
 * PreToolUse: block edits to secret / credential paths.
 * Reads JSON stdin from Claude Code when available; also checks argv/env.
 */
const fs = require("fs");

const SECRET_RE =
  /(^|[\\/])(\.env([.\\/].*)?|credentials\.json|\.credentials[\\/]|secrets?\.(json|ya?ml|toml)|id_rsa|\.pem$|moltbook.*credentials|hf_token)/i;

function collectPaths(input) {
  const paths = new Set();
  const walk = (v) => {
    if (!v) return;
    if (typeof v === "string") {
      if (v.length < 512 && (v.includes("/") || v.includes("\\") || v.includes("."))) {
        paths.add(v);
      }
      return;
    }
    if (Array.isArray(v)) return v.forEach(walk);
    if (typeof v === "object") {
      for (const [k, val] of Object.entries(v)) {
        if (/path|file|target|uri/i.test(k) && typeof val === "string") paths.add(val);
        else walk(val);
      }
    }
  };
  walk(input);
  for (const a of process.argv.slice(2)) paths.add(a);
  if (process.env.CLAUDE_FILE) paths.add(process.env.CLAUDE_FILE);
  if (process.env.CLAUDE_TOOL_INPUT_FILE_PATH) paths.add(process.env.CLAUDE_TOOL_INPUT_FILE_PATH);
  return [...paths];
}

function main() {
  let raw = "";
  try {
    if (!process.stdin.isTTY) {
      raw = fs.readFileSync(0, "utf8");
    }
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

  const paths = collectPaths(payload);
  const hits = paths.filter((p) => SECRET_RE.test(p.replace(/\\/g, "/")));

  if (hits.length) {
    console.error(
      "[hook:block-secrets] Refusing edit of secret path(s):\n" +
        hits.map((h) => "  - " + h).join("\n") +
        "\nUse .env.example / docs only; never commit real tokens.",
    );
    process.exit(2);
  }
  process.exit(0);
}

main();
