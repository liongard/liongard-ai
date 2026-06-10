#!/usr/bin/env node
"use strict";

function parseArgs(argv) {
  const args = {
    instance: process.env.LIONGARD_INSTANCE,
    token: process.env.LIONGARD_MCP_TOKEN,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      i += 1;
      if (i >= argv.length) throw new Error(`Missing value for ${arg}`);
      return argv[i];
    };
    if (arg === "--instance") args.instance = next();
    else if (arg === "--token") args.token = next();
    else if (arg === "-h" || arg === "--help") {
      console.log("Usage: node scripts/liongard-mcp-smoke-test.js --instance <host> --token <accessKeyId>:<secret>");
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return args;
}

function normalizeInstance(value) {
  const trimmed = String(value || "").trim();
  if (!trimmed) throw new Error("Instance is required");
  if (trimmed.includes("://") || trimmed.includes("/")) {
    throw new Error("Enter only the hostname or subdomain, not a URL with scheme/path");
  }
  return trimmed.includes(".") ? trimmed : `${trimmed}.app.liongard.com`;
}

function validateToken(token) {
  const trimmed = String(token || "").trim();
  if (!trimmed.includes(":") || !trimmed.startsWith("lg_mcp_")) {
    throw new Error("Token must look like <accessKeyId>:<accessKeySecret> and start with lg_mcp_");
  }
  return trimmed;
}

async function rpc(url, token, body, sessionId) {
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json,text/event-stream",
    Authorization: `Bearer ${token}`,
  };
  if (sessionId) headers["Mcp-Session-Id"] = sessionId;
  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const text = await response.text();
  let json;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { raw: text.slice(0, 500) };
  }
  return {
    status: response.status,
    sessionId: response.headers.get("mcp-session-id") || sessionId,
    json,
  };
}

function assertOk(label, result) {
  if (result.status < 200 || result.status >= 300 || result.json?.error) {
    throw new Error(`${label} failed: HTTP ${result.status} ${JSON.stringify(result.json)}`);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const host = normalizeInstance(args.instance);
  const token = validateToken(args.token);
  const url = `https://${host}/api/mcp`;

  console.log(`Testing ${url}`);

  const init = await rpc(url, token, {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2025-11-25",
      capabilities: {},
      clientInfo: { name: "liongard-ai-smoke-test", version: "0.1.0" },
    },
  });
  assertOk("initialize", init);
  console.log("initialize: OK");

  const tools = await rpc(url, token, {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/list",
    params: {},
  }, init.sessionId);
  assertOk("tools/list", tools);
  const toolCount = tools.json?.result?.tools?.length ?? 0;
  console.log(`tools/list: OK (${toolCount} tools on first page)`);

  const prompts = await rpc(url, token, {
    jsonrpc: "2.0",
    id: 3,
    method: "prompts/list",
    params: {},
  }, init.sessionId);
  assertOk("prompts/list", prompts);
  const promptCount = prompts.json?.result?.prompts?.length ?? 0;
  console.log(`prompts/list: OK (${promptCount} prompts on first page)`);

  const count = await rpc(url, token, {
    jsonrpc: "2.0",
    id: 4,
    method: "tools/call",
    params: {
      name: "liongard_environment",
      arguments: { operation: "COUNT" },
    },
  }, init.sessionId);
  assertOk("liongard_environment COUNT", count);
  console.log("liongard_environment COUNT: OK");
}

main().catch((error) => {
  console.error(`Smoke test failed: ${error.message}`);
  process.exit(1);
});
