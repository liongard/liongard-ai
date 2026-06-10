#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const errors = [];

function read(file) {
  return fs.readFileSync(path.join(ROOT, file), "utf8");
}

function exists(file) {
  return fs.existsSync(path.join(ROOT, file));
}

function walk(dir, files = []) {
  const abs = path.join(ROOT, dir);
  if (!fs.existsSync(abs)) return files;
  for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
    const rel = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(rel, files);
    else files.push(rel);
  }
  return files;
}

function fail(message) {
  errors.push(message);
}

function parseJson(file) {
  try {
    return JSON.parse(read(file));
  } catch (error) {
    fail(`${file}: invalid JSON (${error.message})`);
    return undefined;
  }
}

function frontmatter(file) {
  const content = read(file);
  if (!content.startsWith("---\n")) return undefined;
  const end = content.indexOf("\n---", 4);
  if (end === -1) return undefined;
  const raw = content.slice(4, end).trim();
  const result = {};
  for (const line of raw.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (match) result[match[1]] = match[2].replace(/^"|"$/g, "");
  }
  return result;
}

function validateMarketplace() {
  const marketplaceFile = ".claude-plugin/marketplace.json";
  if (!exists(marketplaceFile)) {
    fail("Missing .claude-plugin/marketplace.json");
    return;
  }
  const marketplace = parseJson(marketplaceFile);
  if (!marketplace) return;
  if (!marketplace.name) fail(`${marketplaceFile}: missing name`);
  if (!Array.isArray(marketplace.plugins) || marketplace.plugins.length === 0) {
    fail(`${marketplaceFile}: plugins must be a non-empty array`);
    return;
  }
  for (const plugin of marketplace.plugins) {
    if (!plugin.name) fail(`${marketplaceFile}: plugin missing name`);
    if (!plugin.source) fail(`${marketplaceFile}: plugin ${plugin.name || "(unknown)"} missing source`);
    if (typeof plugin.source === "string") {
      const source = plugin.source.replace(/^\.\//, "");
      if (source.includes("..")) fail(`${marketplaceFile}: plugin source must not traverse parents`);
      if (!exists(path.join(source, ".claude-plugin", "plugin.json"))) {
        fail(`${marketplaceFile}: plugin source ${plugin.source} has no .claude-plugin/plugin.json`);
      }
    }
  }
}

function validatePlugin() {
  const pluginFile = "plugins/liongard/.claude-plugin/plugin.json";
  if (!exists(pluginFile)) {
    fail(`Missing ${pluginFile}`);
    return;
  }
  const plugin = parseJson(pluginFile);
  if (!plugin) return;
  if (plugin.name !== "liongard") fail(`${pluginFile}: expected name "liongard"`);
  for (const dir of ["commands", "skills"]) {
    if (!exists(`plugins/liongard/${dir}`)) fail(`plugins/liongard: missing ${dir}/`);
  }
}

function validateFrontmatter() {
  const componentFiles = [
    ...walk("plugins/liongard/commands").filter((f) => f.endsWith(".md")),
    ...walk("plugins/liongard/agents").filter((f) => f.endsWith(".md")),
    ...walk("plugins/liongard/skills").filter((f) => f.endsWith("SKILL.md")),
    ...walk(".claude/commands").filter((f) => f.endsWith(".md")),
    ...walk(".claude/skills").filter((f) => f.endsWith("SKILL.md")),
  ];
  for (const file of componentFiles) {
    const fm = frontmatter(file);
    if (!fm) {
      fail(`${file}: missing YAML frontmatter`);
      continue;
    }
    if (file.includes("/skills/") || file.includes("/agents/") || file.includes("plugins/liongard/commands")) {
      if (!fm.name) fail(`${file}: missing frontmatter name`);
    }
    if (!fm.description) fail(`${file}: missing frontmatter description`);
  }
}

function validateDocs() {
  const required = [
    "docs/harnesses.md",
    "docs/capability-status.md",
    "docs/tools-reference.md",
    "docs/authentication.md",
  ];
  for (const file of required) {
    if (!exists(file)) fail(`Missing ${file}`);
  }
  const allDocs = walk(".").filter((file) => file.endsWith(".md"));
  const joined = allDocs.map((file) => `${file}\n${read(file)}`).join("\n");
  const workflowDocs = allDocs
    .filter((file) => file.includes("/commands/") || file.includes("/skills/") || file.includes("/agents/"))
    .map((file) => `${file}\n${read(file)}`)
    .join("\n");
  for (const stale of ["investigate_alert", "system-overview", "change-report"]) {
    if (workflowDocs.includes(stale)) fail(`Stale legacy prompt/tool reference found in workflow docs: ${stale}`);
  }
  if (!joined.includes("liongard_agents")) fail("Docs/skills should mention liongard_agents");
  if (/OAuth is (supported|recommended|the default)|OAuth.*recommended setup/i.test(joined)) {
    fail("Docs appear to overstate OAuth support; keep OAuth experimental/client-dependent");
  }
}

function validateSecrets() {
  const files = walk(".").filter((file) => {
    if (file.includes("node_modules")) return false;
    if (file.includes(".git/")) return false;
    return [".md", ".json", ".js", ".sh", ".ps1", ".example"].some((suffix) => file.endsWith(suffix));
  });
  const tokenPattern = /lg_mcp_(?!example)(?!<)(?!\.\.\.)[A-Za-z0-9_-]{8,}:[A-Za-z0-9_./+=-]{8,}/;
  for (const file of files) {
    const content = read(file);
    if (tokenPattern.test(content)) fail(`${file}: possible committed MCP token`);
  }
}

validateMarketplace();
validatePlugin();
validateFrontmatter();
validateDocs();
validateSecrets();

if (errors.length) {
  console.error("Validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("Validation OK");
