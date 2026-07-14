#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const readline = require("node:readline/promises");

const CLIENTS = new Set(["claude-code", "claude-desktop", "cursor", "vscode", "generic"]);

function parseArgs(argv) {
  const args = {
    client: undefined,
    instance: process.env.LIONGARD_INSTANCE,
    token: process.env.LIONGARD_MCP_TOKEN,
    scope: "user",
    project: false,
    print: false,
    write: false,
    dryRun: false,
    backup: false,
    nonInteractive: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      i += 1;
      if (i >= argv.length) throw new Error(`Missing value for ${arg}`);
      return argv[i];
    };

    if (arg === "--client") args.client = next();
    else if (arg === "--instance") args.instance = next();
    else if (arg === "--token") args.token = next();
    else if (arg === "--scope") args.scope = next();
    else if (arg === "--project") args.project = true;
    else if (arg === "--print") args.print = true;
    else if (arg === "--write") args.write = true;
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--backup") args.backup = true;
    else if (arg === "--non-interactive") args.nonInteractive = true;
    else if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!args.client) args.client = "generic";
  if (!CLIENTS.has(args.client)) {
    throw new Error(`Unsupported --client '${args.client}'. Use: ${[...CLIENTS].join(", ")}`);
  }
  if (!["user", "local", "project"].includes(args.scope)) {
    throw new Error("--scope must be user, local, or project");
  }
  if (!args.print && !args.write) args.print = true;
  return args;
}

function printHelp() {
  console.log(`Usage:
  node scripts/liongard-mcp-config.js --client <client> [options]

Clients:
  claude-code, claude-desktop, cursor, vscode, generic

Options:
  --instance <host>       acme or acme.app.liongard.com
  --token <token>         <accessKeyId>:<accessKeySecret>
  --scope <scope>         claude-code scope: user, local, project
  --project               write project config (.cursor/mcp.json or .vscode/mcp.json) instead of user config
  --print                 print generated config/command (default when --write is not set)
  --write                 write supported client config
  --dry-run               show target path and output without writing
  --backup                create timestamped backup before writing
  --non-interactive       fail instead of prompting for missing values

Environment:
  LIONGARD_INSTANCE
  LIONGARD_MCP_TOKEN`);
}

async function promptIfNeeded(args) {
  if (args.instance && args.token) return args;
  if (args.nonInteractive) {
    throw new Error("Missing --instance or --token in non-interactive mode");
  }

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    if (!args.instance) {
      args.instance = await rl.question("Liongard instance hostname (e.g. acme.app.liongard.com): ");
    }
    if (!args.token) {
      args.token = await rl.question("Liongard MCP token (<accessKeyId>:<accessKeySecret>): ");
    }
  } finally {
    rl.close();
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

function redactToken(token) {
  const [id] = token.split(":");
  return `${id}:***`;
}

function serverConfig(host, token) {
  return {
    type: "http",
    url: `https://${host}/api/mcp`,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

function printedConfig(client, host, token, scope) {
  const server = serverConfig(host, token);
  if (client === "claude-code") {
    return `claude mcp add --scope ${scope} --transport http liongard "${server.url}" --header "Authorization: Bearer ${token}"`;
  }
  if (client === "vscode") {
    return JSON.stringify({ servers: { liongard: server } }, null, 2);
  }
  if (client === "generic") {
    return JSON.stringify({ name: "liongard", ...server }, null, 2);
  }
  return JSON.stringify({ mcpServers: { liongard: server } }, null, 2);
}

function targetPath(client, project) {
  if (client === "cursor") {
    return project
      ? path.join(process.cwd(), ".cursor", "mcp.json")
      : path.join(os.homedir(), ".cursor", "mcp.json");
  }
  if (client === "claude-desktop") {
    if (process.platform === "darwin") {
      return path.join(os.homedir(), "Library", "Application Support", "Claude", "claude_desktop_config.json");
    }
    if (process.platform === "win32") {
      return path.join(process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"), "Claude", "claude_desktop_config.json");
    }
    return path.join(process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config"), "Claude", "claude_desktop_config.json");
  }
  if (client === "vscode") {
    if (project) {
      return path.join(process.cwd(), ".vscode", "mcp.json");
    }
    if (process.platform === "darwin") {
      return path.join(os.homedir(), "Library", "Application Support", "Code", "User", "mcp.json");
    }
    if (process.platform === "win32") {
      return path.join(process.env.APPDATA || path.join(os.homedir(), "AppData", "Roaming"), "Code", "User", "mcp.json");
    }
    return path.join(process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config"), "Code", "User", "mcp.json");
  }
  return undefined;
}

function readJsonIfExists(file) {
  if (!fs.existsSync(file)) return {};
  const raw = fs.readFileSync(file, "utf8").trim();
  if (!raw) return {};
  return JSON.parse(raw);
}

function mergeConfig(existing, client, host, token) {
  const next = { ...existing };
  const server = serverConfig(host, token);
  if (client === "vscode") {
    next.servers = { ...(next.servers || {}), liongard: server };
  } else {
    next.mcpServers = { ...(next.mcpServers || {}), liongard: server };
  }
  return next;
}

function writeConfig(file, client, host, token, options) {
  const existing = readJsonIfExists(file);
  const next = mergeConfig(existing, client, host, token);
  const output = `${JSON.stringify(next, null, 2)}\n`;
  if (options.dryRun) {
    console.log(`Would write ${file}`);
    console.log(output);
    return;
  }
  fs.mkdirSync(path.dirname(file), { recursive: true });
  if (options.backup && fs.existsSync(file)) {
    const backupFile = `${file}.${new Date().toISOString().replace(/[:.]/g, "-")}.bak`;
    fs.copyFileSync(file, backupFile);
    console.log(`Backup written: ${backupFile}`);
  }
  fs.writeFileSync(file, output, { mode: 0o600 });
  console.log(`Wrote ${file}`);
}

async function main() {
  const args = await promptIfNeeded(parseArgs(process.argv.slice(2)));
  const host = normalizeInstance(args.instance);
  const token = validateToken(args.token);

  if (args.print || args.dryRun) {
    console.log(printedConfig(args.client, host, token, args.scope));
    console.error(`Note: output contains your access token (${redactToken(token)}) — treat it like a password.`);
  }

  if (args.client === "claude-code") {
    if (args.print || args.dryRun) {
      console.error("Run the printed claude mcp add command yourself; it will enter your shell history, so clear it afterwards if your history policy requires.");
    }
    return;
  }

  if (args.write || args.dryRun) {
    const file = targetPath(args.client, args.project);
    if (!file) throw new Error(`--write is not supported for client ${args.client}`);
    writeConfig(file, args.client, host, token, args);
  }
}

main().catch((error) => {
  console.error(`Error: ${error.message}`);
  process.exit(1);
});
