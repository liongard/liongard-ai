#!/usr/bin/env python3
"""Compile canonical Liongard recipes into Microsoft Copilot knowledge packages.

Modes:
  (default)     Build copilot/generated/ from canonical sources.
  --check       Rebuild into a temp dir and fail if copilot/generated/ is stale
                or invalid (use in CI / pre-commit).
  --validate    Validate the committed copilot/generated/ tree only.

Determinism: output contains no timestamps and no commit hashes inside compiled
files, so --check does not go stale on every commit. Traceability is per-file
(source SHA-256) plus manifest.sourceCommit (ignored by --check).

Requires: Python 3.9+, PyYAML.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / "copilot" / "build.config.json"
TEMPLATES = ROOT / "copilot" / "templates"
DOCS = ROOT / "copilot" / "docs"
GENERATED = ROOT / "copilot" / "generated"
GENERATOR_VERSION = "0.1.0-poc"
MANIFEST_VOLATILE = {"sourceCommit"}

REQUIRED_HEADINGS = [
    "## 1. When to use",
    "## 2. Required inputs",
    "## 3. Liongard MCP tools",
    "## 4. Preflight questions",
    "## 5. MSP profile",
    "## 6. Execution steps",
    "## 7. QA rules",
    "## 8. Output contract",
    "## 9. Source traceability",
]
FORBIDDEN_PATH = re.compile(
    r"(?<![\w/])(?:\.\./)*(?:reference|templates|config|primitives|personas|recipes)/[\w./-]+"
)


# ───────────────────────── helpers ─────────────────────────
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_cfg() -> dict:
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def library_version() -> str:
    try:
        return json.loads((ROOT / "plugins/liongard/.claude-plugin/plugin.json").read_text())["version"]
    except Exception:
        return "unknown"


def split_frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 4:].lstrip("\n")
    return fm, body


def split_sections(body: str):
    """Return (preamble, [(heading, text)]) split on level-2 headings, fence-aware."""
    preamble, sections, cur, in_fence = [], [], None, False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^## (.+?)\s*$", line)
        if m:
            if cur:
                sections.append(cur)
            cur = [m.group(1), []]
            continue
        (cur[1] if cur else preamble).append(line)
    if cur:
        sections.append(cur)
    return "\n".join(preamble).strip("\n"), [(h, "\n".join(t).strip("\n")) for h, t in sections]


def category_of(rel: str) -> str:
    return rel.split("/")[1]


def title_of(body: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", body, re.M)
    return m.group(1).strip() if m else fallback


def one_line(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


# ───────────────────────── recipe index ─────────────────────────
def build_index():
    """Index every recipe by file stem so 'Pairs with' references can be rewritten."""
    idx = {}
    for p in sorted((ROOT / "recipes").rglob("*.md")):
        if p.name in {"README.md", "AGENTS.md"}:
            continue
        try:
            fm, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if fm.get("name"):
            idx[p.stem] = fm["name"]
    return idx


# ───────────────────────── text normalization ─────────────────────────
class Norm:
    def __init__(self, cfg, index):
        self.cfg, self.index = cfg, index
        self.tool_hits = {}
        self.unmapped_paths = set()

    def tools(self, text: str) -> str:
        for old, new in self.cfg["toolMap"].items():
            if old.startswith("comment"):
                continue
            n = len(re.findall(rf"\b{re.escape(old)}\b", text))
            if n:
                self.tool_hits[old] = self.tool_hits.get(old, 0) + n
                text = re.sub(rf"\b{re.escape(old)}\b", new, text)
        return text

    def paths(self, text: str) -> str:
        rewrites = self.cfg["pathRewrites"]
        # markdown links: [label](path) -> label
        text = re.sub(r"\[([^\]]+)\]\((?:\.\./)*(?:reference|templates|config|primitives|personas|recipes)/[^)]*\)", r"\1", text)
        # known paths (longest first), with or without backticks
        for src in sorted(rewrites, key=len, reverse=True):
            text = re.sub(r"`?(?:\.\./)*" + re.escape(src) + r"`?", rewrites[src], text)

        def generic(m):
            path = m.group(0)
            stem = Path(path).stem
            if path.startswith("recipes/") and stem in self.index:
                return f"the recipe `{self.index[stem]}`"
            self.unmapped_paths.add(path)
            return f"the library document \"{Path(path).name}\" (not bundled)"

        text = FORBIDDEN_PATH.sub(generic, text)
        # sibling recipe filenames in backticks: `all-backups.md` -> the recipe `system-type-all-backups`
        def sib(m):
            stem = m.group(1)
            return f"the recipe `{self.index[stem]}`" if stem in self.index else m.group(0)

        return re.sub(r"`([a-z0-9-]+)\.md`", sib, text)


# ───────────────────────── agent-guide extraction ─────────────────────────
def agent_guide_sections():
    text = (ROOT / "recipes" / "AGENTS.md").read_text(encoding="utf-8")
    _, secs = split_sections(text)
    out = {}
    for h, t in secs:
        m = re.match(r"(\d+)\.", h)
        if m:
            out[int(m.group(1))] = (h, t)
    return out


def qa_digest():
    """Digest of canonical QA categories: heading + first paragraph each (full text lives in the reference doc)."""
    text = (ROOT / "reference" / "qa-retry-pattern.md").read_text(encoding="utf-8")
    lines, items, cur, in_fence = text.splitlines(), [], None, False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^### (Category \d+.*)$", line)
        if m:
            cur = [m.group(1), []]
            items.append(cur)
            continue
        if re.match(r"^## ", line):
            cur = None
        if cur is not None:
            cur[1].append(line)
    out = []
    for head, body in items:
        para = []
        for l in body:
            if l.strip() == "" and para:
                break
            if l.strip() and not l.startswith("```"):
                para.append(l.strip())
        out.append(f"- **{head}** - {one_line(' '.join(para))}")
    return "\n".join(out)


# ───────────────────────── metric primitives ─────────────────────────
_PRIM = None


def load_primitives():
    global _PRIM
    if _PRIM is None:
        _PRIM = {}
        for f in sorted((ROOT / "primitives" / "metrics").glob("*.yaml")):
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            for pr in d.get("primitives") or []:
                _PRIM[pr["@id"]] = pr
    return _PRIM


def op_encode(q: str) -> str:
    """Copilot knowledge ingestion collapses '==' (and can mangle '&&'); encode them as words in run cards."""
    return str(q).replace("==", " EQ_OP ").replace("&&", " AND_OP ").replace("||", " OR_OP ").replace("  ", " ")


OP_NOTE = ("> Operator words in queries: before sending any `jmesPathQuery`, replace each EQ_OP with two equals characters in a row "
           "each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row; change nothing else. (Knowledge storage corrupts those symbols.)")


def encode_operators(text: str) -> str:
    """Copilot knowledge ingestion collapses '==' to '=' and can mangle '&&'. Encode both as words in every
    generated knowledge document and add the restore note once, right after the first line."""
    if "==" not in text and "&&" not in text and " || " not in text and "EQ_OP" not in text and "AND_OP" not in text:
        return text
    text = text.replace("==", " EQ_OP ").replace("&&", " AND_OP ").replace(" || ", " OR_OP ")
    text = re.sub(r"(?<=\S)  +(?=\S)", " ", text)
    if "Operator words in queries" in text or "Operator words in fallback queries" in text:
        return text
    head, _, rest = text.partition("\n")
    return f"{head}\n\n{OP_NOTE}\n{rest}"


def code(s: str) -> str:
    s = str(s)
    return f"`` {s} ``" if "`" in s else f"`{s}`"


def render_primitives(ids, warn, recipe, title, inline=False):
    """Return (plan_markdown, vendor_docs). The plan stays in the recipe; the per-vendor primitive lists
    become small retrieval-oriented metric reference documents (name, markdown)."""
    prims, groups = load_primitives(), {}
    for i in ids:
        pr = prims.get(i)
        if not pr:
            warn.append({"recipe": recipe, "problem": f"primitive not found: {i}"})
            continue
        ev = pr.get("evaluates") or {}
        groups.setdefault((ev.get("inspectorSlug", "cross-cutting"), ev.get("inspectorId")), []).append(pr)
    total = sum(len(v) for v in groups.values())
    if inline:
        rules = [
            "1. **Find the system.** `liongard_launchpoint LIST` for the environment and this recipe's inspector (ID in the table). If none exists, say so and stop.",
            "2. **Fetch, do not compute.** For every primitive below that has a `metricId`, call `liongard_metric EVALUATE` with `metricId`, `systemId` and `environmentId` (no `jmesPathQuery`). This returns the value Liongard already stored for the latest inspection, so no query is written or evaluated. Only if a primitive has no `metricId`, evaluate its exact JMESPath query. If a stored-metric call returns an error, retry once, then use the listed query.",
            "3. **Only the listed primitives.** Run exactly the primitives in this list, once per system, no more and no fewer. Never invent a primitive, a JMESPath path, or a sequence number; never run `liongard_metric LIST` to discover extra metrics; never test other dataprint paths. Use the sequence ids (P001...) and `@id` exactly as written on that metric's own `fallback query` line.",
            "4. **No data.** A primitive that returns null or an error after one retry is reported as \"No data\" in the coverage table. It is not a finding, not a control to verify, and not a pass. Do not turn it into a Manual Verification item unless the recipe says the control matters and no other primitive covers it.",
            "5. **Logging.** One verification-log row per primitive per system (sequence id, `@id`, `metricId`, actual result shape such as string, integer, array(n), object, or null). Never use generic placeholders like \"value / array / count\".",
            "6. **Coverage.** Report primitives executed / required (they must be equal), plus how many returned data and how many returned no data. Respect each field gotcha.",
        ]
    else:
        rules = [
            "1. **Applicability.** Use `liongard_launchpoint LIST` to find systems per inspector (inspector ID in the table). "
            "A vendor applies only if at least one system of that inspector exists in the environment. List every other vendor "
            "in the coverage table as \"no system deployed\".",
            "2. **Completeness.** For every system of an applicable vendor, evaluate EVERY primitive in that vendor's metric reference "
            "document with `liongard_metric EVALUATE` (`jmesPathQuery` = the query, plus `systemId` and `environmentId`). Do not sample, "
            "prioritize or skip primitives. Run stale or faulted systems too (their latest dataprint) and label their results stale. "
            "Do not stop after discovery and do not ask the user whether to proceed: finish every primitive, then report.",
            "3. **Nulls and errors.** Retry a null or error once. If it persists, record it and continue. Never infer a value, and never "
            "state a control is unavailable unless its primitive was run and returned null or an error.",
            "4. **Logging.** One verification-log row per primitive per system, with the sequence id (P001...), the primitive `@id`, and the result shape. Do not group rows.",
            "5. **Coverage.** Before rendering, build the metric coverage table: vendor | systems | primitives executed / required | nulls | errors. "
            "Executed must equal required for every applicable vendor; list any gap under Manual Verification Needed. Report findings from every "
            "primitive that has a `compliant when` rule or a gotcha-defined condition.",
            "6. Respect each field gotcha.",
        ]
    plan = [
        "### Metric primitives (deterministic execution plan)", "",
        f"This recipe declares {total} validated metric primitives across {len(groups)} inspectors. They are required measurements, not suggestions. "
        + ("The full list follows this section in this same document. Execute by these rules, every run:" if inline else "Each vendor's primitives are in its own knowledge document named in the table below: search for that exact document name and open it before "
        "evaluating that vendor. Execute by these rules, every run:"), "",
        *rules, "",
        *(["| Vendor (inspector) | Inspector ID | Primitives | Sequence ids |", "|---|---|---|---|"] if inline else ["| Vendor (inspector) | Inspector ID | Primitives | Sequence ids | Metric reference document |", "|---|---|---|---|---|"]),
    ]
    inline_blocks = []
    docs, seq, plan_vendors = [], 0, []
    for (slug, iid), items in sorted(groups.items(), key=lambda kv: kv[0][0]):
        first = seq + 1
        pv = {"inspectorSlug": slug, "inspectorId": iid, "primitives": []}
        body = []
        for pr in sorted(items, key=lambda x: x["@id"]):
            seq += 1
            pv["primitives"].append({"seq": f"P{seq:03d}", "id": pr["@id"], "query": pr.get("jmesPath", ""), "resultType": pr.get("resultType"), "compliantWhen": pr.get("compliantWhen"), "fieldGotcha": pr.get("fieldGotcha"), "metricUuid": pr.get("liongardMetricUuid")})
            mid = pr.get("liongardMetricId")
            line = f"- **`{pr['@id']}`** [P{seq:03d}] - {one_line(pr.get('name', ''))}. {one_line(pr.get('description', ''))}\n  - " + (f"metricId: {mid} | " if mid else "metricId: none (use query) | ") + f"query: {code(pr.get('jmesPath', ''))}"
            rt = pr.get("resultType")
            if rt:
                line += f" | result: {rt}" + (f" ({pr['resultUnit']})" if pr.get("resultUnit") else "")
            if pr.get("compliantWhen"):
                line += f"\n  - compliant when: {one_line(str(pr['compliantWhen']))}"
            if pr.get("fieldGotcha"):
                line += f"\n  - gotcha: {one_line(str(pr['fieldGotcha']))}"
            if pr.get("status"):
                line += f"\n  - status: {pr['status']}"
            body.append(line)
        docname = f"metrics-{recipe}-{slug.removesuffix('-inspector')}"
        plan.append(f"| {slug} | {iid or '-'} | {len(items)} | P{first:03d}-P{seq:03d} |" if inline else f"| {slug} | {iid or '-'} | {len(items)} | P{first:03d}-P{seq:03d} | `{docname}` |")
        if inline:
            inline_blocks.append(f"#### Primitives: {slug}" + (f" (inspector ID {iid})" if iid else "") + "\n\n" + "\n".join(body))
        md = (
            f"# {docname} - Metric reference ({slug})\n\n"
            f"Required metric primitives for the recipe `{recipe}` ({title}), inspector `{slug}`"
            + (f" (ID {iid})" if iid else "") + f". {len(items)} primitives, sequence ids P{first:03d}-P{seq:03d}. "
            "For every system of this inspector, evaluate EVERY primitive below with `liongard_metric EVALUATE` "
            "(`jmesPathQuery`, `systemId`, `environmentId`), retry a null or error once, and log one row per primitive per system. "
            "Respect each gotcha.\n\n" + "\n".join(body) + "\n"
        )
        if not inline:
            docs.append((docname, slug, len(items), md))
        plan_vendors.append(pv)
    if inline:
        plan.extend(["", *inline_blocks])
    return "\n".join(plan), docs, plan_vendors


RUN_CARD_HEADINGS = ["## 1. When to use", "## 2. Run steps", "## 3. Metrics to fetch", "## 4. Report", "## 5. Source traceability"]


def metric_parts(name, rows, size=6):
    """Group metric lines under self-identifying headings so each retrieval chunk can be searched by id range."""
    out = []
    for i in range(0, len(rows), size):
        lo, hi = i + 1, min(i + size, len(rows))
        out.append(f"### {name} metrics P{lo:03d}-P{hi:03d}\n\n" + "\n".join(rows[i:i + size]))
    return "\n\n".join(out)


def build_run_card(fm, name, title, cat, rel, raw, parts, plan_vendors, when, cfg):
    """Compact single-system document: one retrieval-sized card (steps, metric table, report spec)."""
    prims = load_primitives()
    custom = {}
    for h, t in parts["customize"]:
        m = re.search(r"```ya?ml\n(.*?)```", t, re.S)
        if m:
            try:
                custom = yaml.safe_load(m.group(1)) or {}
            except Exception:
                custom = {}
    pv = plan_vendors[0] if plan_vendors else {"inspectorSlug": "?", "inspectorId": None, "primitives": []}
    iid = pv.get("inspectorId")
    rows = []
    for pr in pv["primitives"]:
        src = prims.get(pr["id"], {})
        nm = one_line(src.get("name", pr["id"].split(":")[-1]))
        nm = nm.split(" - ", 1)[-1].split(" — ", 1)[-1]
        mid = src.get("liongardMetricId")
        note = []
        if pr.get("compliantWhen"):
            note.append("OK when " + one_line(str(pr["compliantWhen"])))
        if pr.get("fieldGotcha"):
            g = one_line(str(pr["fieldGotcha"]))
            note.append(g[:160] + ("..." if len(g) > 160 else ""))
        q = one_line(str(pr.get("query", "")))
        rows.append(f"- **{pr['seq']}** metricId {mid or 'none'} - {nm} ({pr.get('resultType') or 'value'})"
                    + (f" - {' ; '.join(note)}" if note else "") + f"\n  - fallback query: {code(op_encode(q))}")
    sec = custom.get("sections") or {}
    sections = [str(v) for v in sec.values() if v]
    slas = custom.get("slas") or {}
    sla_line = "; ".join(f"{k}={v}" for k, v in slas.items()) if slas else "(none)"
    insights = ""
    for h, t in parts["exec"]:
        if h.lower().startswith("insights"):
            insights = t.strip()
    gaps = ""
    for h, t in parts["exec"]:
        if h.lower().startswith("data gaps"):
            gaps = t.strip()
    fmts = ", ".join(fm.get("output_formats", []))
    n = len(pv["primitives"])
    doc = f"""# {title} (Run Card)

<!-- Generated by scripts/copilot/build_copilot_package.py - do not edit by hand. -->

Recipe `{name}` | category {cat} | formats {fmts} | inspector `{pv['inspectorSlug']}` (ID {iid})

## 1. When to use

{when}

## 2. Run steps

1. Resolve the environment with `liongard_environment`; apply the PREFLIGHT and MSP PROFILE rules from the agent instructions.
2. `liongard_launchpoint LIST` for the environment with inspector ID {iid}. One report section per system found; if none, say so and stop. Record `latestInspectionDate` for each.
3. Before fetching, confirm you can see all {n} metric lines (P001 to P{n:03d}). Retrieval returns only part of this card: if any sequence id is missing, search the knowledge again for the heading of the missing group (for example "{name} metrics P013-P018") until every line is found. Never skip a metric because its line was not retrieved.
4. For every metric line below, call `liongard_metric EVALUATE` with `metricId`, `systemId`, `environmentId`: this returns the value Liongard already stored, so write no query. If that call returns no data rows at all (the metric is not stored on this instance) or has no metricId, do not retry the stored call: immediately call `liongard_metric EVALUATE` once with `jmesPathQuery` set to that line's fallback query exactly as written on that metric's own `fallback query` line. Operator words in fallback queries: knowledge storage corrupts the symbols, so before sending, replace each EQ_OP with two equals characters in a row and each AND_OP with two ampersand characters in a row and each OR_OP with two vertical-bar characters in a row, changing nothing else. An empty array, an empty string or 0 is a real value, not "No data": report it as such. Only a null, an error, or no rows after the fallback is "No data".
5. Run exactly these metric lines: no extra metrics, no `liongard_metric LIST`, no invented paths or sequence numbers.
6. Write the report in the report format below, apply the QA and rendering rules from the agent instructions, and end with Manual Verification Needed.

## 3. Metrics to fetch

{len(pv['primitives'])} metrics. Each line has its stored metricId and its own fallback query.

""" + metric_parts(name, rows) + f"""

## 4. Report

Sections, in order: {'; '.join(sections) if sections else 'Executive Summary; Findings; Recommended Actions; Data Gaps'}.

Thresholds: {sla_line}.

Report each metric's actual value. Show "No data" for empty values; never mark a control passing without a supporting value. A "No data" row is a coverage gap only if the control matters and no other row covers it.

Coverage table: metrics fetched / required, with data / no data counts. Internal audience: add a verification log, one row per call (seq, metricId, result shape, status).
""" + (f"\n### Insights and recommendations\n\n{insights}\n" if insights else "") + (f"\n### Data gaps\n\n{gaps}\n" if gaps else "") + f"""
## 5. Source traceability

- Canonical source: `{rel}`
- Source SHA-256: `{sha256_bytes(raw)}`
- Library version: {library_version()}
"""
    return doc


SPLIT_AT = 6


def split_run_card(name, title, doc):
    """Cards with many metrics are split so each part is retrieved on its own. Returns (main_doc, [(part_no, text), ...])."""
    m = re.search(r"(?m)^### " + re.escape(name) + r" metrics P\d{3}-P\d{3}$", doc)
    groups = list(re.finditer(r"(?m)^### " + re.escape(name) + r" metrics P(\d{3})-P(\d{3})$", doc))
    if not m:
        return doc, []
    end_metrics = doc.index("\n## 4. Report")
    cut = groups[0].start()  # every metric group lives in its own small part file; the main card keeps steps + report
    head, tail = doc[:cut], doc[cut:end_metrics]
    rest = doc[end_metrics:]
    chunks = re.split(r"(?m)(?=^### " + re.escape(name) + r" metrics P)", tail)
    chunks = [c.strip() for c in chunks if c.strip()]
    per = max(1, SPLIT_AT // 6)
    parts = []
    for i in range(0, len(chunks), per):
        grp = chunks[i:i + per]
        lo = re.search(r"P(\d{3})-", grp[0]).group(1)
        hi = re.search(r"-P(\d{3})", grp[-1]).group(1)
        no = len(parts) + 2
        parts.append((no, f"# {title} (Run Card part {no})\n\nRecipe `{name}` run card part {no}: continuation of `{name} run card` with metrics P{lo}-P{hi}. Run each line exactly as step 4 of the main run card says.\n\n" + "\n\n".join(grp) + "\n"))
    names = ", ".join(f"`{name} run card part {n}`" for n, _ in parts)
    note = "\n\nThe metric lines are in " + names + ". Search for each part by name and run every line.\n"
    main = head.rstrip() + note + rest
    searches = "; ".join(f'"{name} run card part {n}"' for n, _ in parts)
    main = main.replace("3. Before fetching, confirm", f"3. This card continues in {len(parts)} more files. Before fetching anything, run one knowledge search for each of these exact phrases and read every result: {searches}. If you run out of searches before every part is read, do not skip those metrics and do not stop silently: evaluate the parts you have, list the unread parts, and end the turn with \"Reply continue to evaluate the remaining parts.\" When the user replies continue, search only the unread parts, evaluate them, and give the complete report. Then confirm", 1)
    return main, parts


# ───────────────────────── recipe compilation ─────────────────────────
ROLE = {
    "when": ("when to use",),
    "inputs": ("inputs",),
    "customize": ("customize for your msp",),
    "qa": ("qa", "quality assurance"),
    "output": ("output format",),
    "verify": ("verification log",),
}


def role_of(heading: str):
    h = heading.lower()
    for role, keys in ROLE.items():
        if any(h.startswith(k) for k in keys):
            return role
    return None

def compact_rollup(doc: str) -> str:
    """Rollup/master recipes are too big for Copilot's per-turn knowledge-search budget. Keep the steps, queries and
    tables; drop background prose, tone variants, cross-check/insight sections and text the agent instructions already carry."""
    parts = re.split(r"(?m)^(?=## \d+\. )", doc)
    out = []
    for part in parts:
        h = part.split("\n", 1)[0]
        if h.startswith("## 4. "):
            part = h + "\n\nApply the PREFLIGHT rules from the agent instructions.\n\n"
        elif h.startswith("## 5. "):
            part = h + "\n\nApply the MSP PROFILE rules and the msp-profile knowledge file.\n\n"
        elif h.startswith("## 7. "):
            part = h + "\n\nApply the QA rules from the agent instructions: retry nulls once, flag stale inspectors, flag count divergences, end with Manual Verification Needed.\n\n"
        elif h.startswith("## 6. "):
            cut = re.search(r"(?m)^### (Tone-driven adaptations|Coverage cross-check|Insights & recommendations|Data gaps|Transitioning out of)", part)
            if cut:
                part = part[: cut.start()]
            part = re.sub(r"(?m)^>.*\n", "", part)
            part = re.sub(r"(?m)^---\s*\n", "", part)
            part = re.sub(r"\n{3,}", "\n\n", part)
        out.append(part)
    return "".join(out)


def compile_recipe(rel: str, cfg: dict, norm: Norm, guide: dict, qa_text: str, synth: list, warn: list):
    src = ROOT / rel
    raw = src.read_bytes()
    fm, body = split_frontmatter(raw.decode("utf-8"))
    name = fm.get("name") or src.stem
    cat = category_of(rel)
    grp = cfg["fileGroups"]["categories"][cat]
    tools_raw = [t for t in re.findall(r"liongard_[a-z_]+", str(fm.get("compatibility", "")))]
    tools = []
    for t in tools_raw:
        t = cfg["toolMap"].get(t, t)
        if t not in tools:
            tools.append(t)

    preamble, secs = split_sections(body)
    parts = {"when": [], "inputs": [], "customize": [], "qa": [], "output": [], "verify": [], "exec": []}
    for h, t in secs:
        r = role_of(h)
        if r:
            parts[r].append((h, t))
        else:
            parts["exec"].append((h, t))

    def block(items):
        return "\n\n".join(f"### {h}\n\n{t}" if len(items) > 1 else t for h, t in items).strip()

    # 1 when to use
    if parts["when"]:
        when = block(parts["when"])
    else:
        when = one_line(str(fm.get("description", "")))
        synth.append({"recipe": name, "section": "when-to-use", "from": "frontmatter.description"})
    # 2 inputs
    if parts["inputs"]:
        inputs = block(parts["inputs"])
    else:
        inputs = (
            "- Liongard environment (customer) name or ID. If not supplied, resolve with `liongard_environment LIST` "
            "(keyword search) and confirm with the user before pulling data.\n"
            "- Reporting period or point in time, if the report is period-based.\n"
            "- Any recipe-specific scope (system, inspector, framework) described in the execution steps below."
        )
        synth.append({"recipe": name, "section": "required-inputs", "from": "generic default"})
    # 3 tools
    tools_md = "\n".join(f"- `{t}` - {cfg['toolDescriptions'].get(t, 'see Liongard MCP tool list')}" for t in tools)
    # 4 preflight (verbatim from recipes/AGENTS.md section 3)
    pre = guide[3][1]
    # 5 msp profile
    profile = (
        "Apply the MSP profile (knowledge file `msp-profile-template`) before rendering: brand name and colors, "
        "preferred vendor stack, SLA thresholds, audience tone, default output format, and filename prefix. "
        "Values the user states in chat override the profile. If the profile still contains placeholders such as "
        "`<Your MSP Name>`, ask the user for the missing value or leave a clearly marked placeholder - never invent one."
    )
    if parts["customize"]:
        profile += "\n\nRecipe-level defaults (override the profile only where the user or profile does not specify):\n\n" + block(parts["customize"])
    # 7 QA
    qa_recipe = block(parts["qa"]) if parts["qa"] else ""
    qa = (
        "Run a QA pass after data collection and before rendering. Canonical categories "
        "(full detail in the knowledge document \"Reference: QA Retry Pattern\"):\n\n" + qa_text
    )
    if qa_recipe:
        qa += "\n\nRecipe-specific QA:\n\n" + qa_recipe
    qa += "\n\nAlways append a \"Manual Verification Needed\" section listing every item flagged above."
    # 8 output
    if parts["output"]:
        out_recipe = block(parts["output"])
    else:
        out_recipe = (
            f"Supported formats: {', '.join(fm.get('output_formats', ['markdown']))}. "
            "Default to Markdown unless the user or MSP profile selects another format. Use the recipe's section "
            "order from the execution steps as the report outline."
        )
        synth.append({"recipe": name, "section": "output-contract", "from": "generic default"})
    out = guide[4][1] + "\n\n" + out_recipe
    trace = (
        "\n\n### Verification log requirements (internal audience only)\n\n"
        "One row per Liongard tool call or per metric evaluated: tool and action, system or scope, the metric primitive "
        "`@id` (from the Metric primitives list) or the exact JMESPath if none applies, the result shape "
        "(value, count, null, error), and status (Complete, Retried, Flagged). Do not group several calls into one "
        "generic row. Include retries and which calls returned null. Omit this log entirely for external audiences."
    )
    inline_plan = cat in cfg.get("primitivePlan", {}).get("inlineCategories", [])
    embed_plan = bool(fm.get("primitives")) and (inline_plan or cat in cfg.get("primitivePlan", {}).get("categories", []))
    if embed_plan:
        trace += (
            "\n\n### Metric coverage (required in every audience)\n\n"
            "Include a short coverage table: vendor | systems evaluated | primitives executed / required | nulls | errors, "
            "and a line for vendors with no system deployed. Internal reports also list one verification-log row per "
            "primitive per system (sequence id P001..., primitive `@id`)."
        )
    out += trace
    if parts["verify"]:
        out += "\n\n### Verification log\n\n" + parts["verify"][0][1]

    # 6 execution = preamble + remaining sections in original order
    exec_md = ""
    if preamble:
        exec_md += preamble + "\n\n"
    for h, t in parts["exec"]:
        exec_md += f"### {h}\n\n{t}\n\n"
    exec_md = exec_md.strip()
    if cat != "single-system-analysis" and re.search(r"chain", exec_md, re.I):
        packaged = sorted("single-system-" + Path(r).stem for r in cfg["scope"]["recipes"] if "single-system-analysis" in r)
        chain = (
                "### Chaining in this knowledge base (read first)\n\n"
                "The cross-vendor system-type rollups named below (for example all-firewalls, all-servers, all-backups, all-edrs) are NOT packaged here. "
                "Chain per vendor instead: for each vendor system type you find with `liongard_launchpoint` that has a packaged recipe in this list: "
                + ", ".join(f"`{n}`" for n in packaged) + ", "
                "search your knowledge for `<recipe name> run card`, find every metric group of that card (headings like `<recipe name> metrics P007-P012`), "
                "and run it completely before starting the next vendor. One vendor at a time, in the order found. Your knowledge-search budget is limited per turn, so work in batches of at most 4 vendors per turn: after a batch, print each vendor's result block and end the turn with \"Batch N of M complete. Reply continue for the next batch.\" Do not try to run every vendor in one turn. When the last batch is done, merge all result blocks from this conversation into the final report. After each vendor, write a short result block "
                "(systems, data age, findings, every metric value or No data, coverage line) so later steps can use it. Do not skip a vendor or a metric to save calls. "
                "A class with no packaged recipe (for example servers, backups, hypervisors, domains) is answered from the reconciled inventory tools "
                "(`liongard_device`, `liongard_identity`, `liongard_domain`) and listed in the coverage table as \"no packaged vendor recipe\"; never invent its checks. "
                "A class whose vendor is not deployed is \"not deployed\", not a gap in the data. If a vendor's card cannot be found after searching its metric groups, list it under Manual Verification Needed.\n\n"
            )
        exec_md = chain + exec_md
    prim_ids = (fm.get("primitives") or []) if embed_plan else []
    metric_docs, plan_vendors = [], []
    title = title_of(body, name)
    if prim_ids:
        plan_md, metric_docs, plan_vendors = render_primitives(prim_ids, warn, name, title, inline=inline_plan)
        if inline_plan:
            exec_md = plan_md + "\n\n### Workflow steps (context only)\n\nThe steps below explain what each area means. Where a step lists metric names or paths that are not in the primitives list above, ignore them: execute only the primitives above.\n\n" + exec_md
        else:
            exec_md += "\n\n" + plan_md

    title = title_of(body, name)
    category_path = rel.rsplit("/", 1)[0].replace("recipes/", "")
    run_card = cat in cfg.get("primitivePlan", {}).get("compactCategories", []) and bool(plan_vendors)
    doc = f"""# {title} (Compiled Recipe)

<!-- Generated by scripts/copilot/build_copilot_package.py - do not edit by hand. Edit the canonical source and rebuild. -->

| Field | Value |
|---|---|
| Recipe name | `{name}` |
| Category | {cat} |
| Personas | {', '.join(fm.get('personas', [])) or 'all'} |
| Output formats | {', '.join(fm.get('output_formats', []))} |
| Canonical source | `{rel}` |
| Source SHA-256 | `{sha256_bytes(raw)}` |
| Library version | {library_version()} |

## 1. When to use

{when}

## 2. Required inputs

{inputs}

## 3. Liongard MCP tools

Call these tools on the connected Liongard MCP server. Do not answer from memory; every figure must come from a tool result.

{tools_md}

## 4. Preflight questions

{pre.strip()}

## 5. MSP profile

{profile}

## 6. Execution steps

{exec_md}

## 7. QA rules

{qa}

## 8. Output contract

{out}

## 9. Source traceability

- Canonical source: `{rel}` (category path: `{category_path}`)
- Source SHA-256: `{sha256_bytes(raw)}`
- Library version: {library_version()}
- Package manifest: `manifest.json` lists the source commit and checksums for this file.
"""
    if run_card:
        doc = build_run_card(fm, name, title, cat, rel, raw, parts, plan_vendors, when, cfg)
    if rel in cfg.get("compactRecipes", []):
        doc = compact_rollup(doc)
    doc = norm.paths(norm.tools(doc))
    # restore canonical-source lines that the path rewriter would have altered
    doc = re.sub(r"(Canonical source \| )[^\n]*", rf"\1`{rel}` |", doc)
    doc = re.sub(r"(- Canonical source: )[^\n]*", rf"\1`{rel}` (category path: `{category_path}`)", doc)
    entry = {
        "id": f"recipe:{cat}:{name}",
        "name": name,
        "title": title,
        "category": cat,
        "group": grp["group"],
        "groupTitle": grp["title"],
        "bundle": grp["bundle"],
        "personas": fm.get("personas", []),
        "outputFormats": fm.get("output_formats", []),
        "tools": tools,
        "description": one_line(str(fm.get("description", ""))),
        "source": rel,
        "sourceSha256": sha256_bytes(raw),
        "dependencies": {"composes": fm.get("composes", []), "primitiveCount": len(prim_ids)},
    }
    entry["plan"] = {"recipe": name, "source": rel, "sourceSha256": sha256_bytes(raw), "primitiveCount": sum(len(v["primitives"]) for v in plan_vendors), "vendors": plan_vendors} if plan_vendors else None
    return doc, entry, metric_docs


# ───────────────────────── catalog / instructions / profile ─────────────────────────
def render_catalog(entries):
    lines = [
        "LIONGARD RECIPE CATALOG",
        "Use this catalog to choose the recipe BEFORE calling any Liongard tool. Match the user's request to the trigger phrases, then open the matching compiled recipe document by name.",
        "",
    ]
    for e in sorted(entries, key=lambda e: (e["groupTitle"], e["name"])):
        lines += [
            f"RECIPE: {e['name']}",
            f"  id: {e['id']}",
            f"  title: {e['title']}",
            f"  group: {e['groupTitle']}",
            f"  personas: {', '.join(e['personas']) or 'all'}",
            f"  output formats: {', '.join(e['outputFormats'])}",
            f"  required tools: {', '.join(e['tools'])}",
            f"  use when: {e['description']}",
            f"  document: {e['name']}.md (Copilot Studio) / {e['bundle']}.txt (Agent Builder)",
            "",
        ]
    return "\n".join(lines)


def render_instructions(cfg, entries, edition):
    tpl = (TEMPLATES / "agent-instructions.txt").read_text(encoding="utf-8")
    tools = sorted({t for e in entries for t in e["tools"]} | {"liongard_environment", "liongard_launchpoint", "liongard_metric"})
    tool_lines = "\n".join(f"- {t}: {cfg['toolDescriptions'].get(t, '')}" for t in tools)
    locate = (
        "Open the compiled recipe document named in the catalog (one file per recipe, grouped in file groups)."
        if edition == "copilot-studio"
        else "Open the bundle named in the catalog (bundles contain several compiled recipes; find the recipe by its RECIPE heading)."
    )
    return tpl.replace("{{TOOLS}}", tool_lines).replace("{{LOCATE}}", locate)


def render_profile():
    cfg_text = (ROOT / "config" / "msp-config.yaml").read_text(encoding="utf-8")
    header = (
        "MSP PROFILE (partner-editable)\n"
        "Fill in the values below and upload this file as knowledge. The agent applies these values to every report; values the user states in chat take precedence.\n"
        "Derived from the library's config/msp-config.yaml - same keys, same meaning. Leave a value empty to use the library default.\n"
        "Never put customer names or credentials in this file.\n"
        "----------------------------------------------------------------\n\n"
    )
    return header + cfg_text


def to_txt(md: str) -> str:
    return md  # Markdown is plain text; Agent Builder only needs the .txt extension.


# ───────────────────────── build ─────────────────────────
def write(out: Path, rel: str, data: str | bytes, files: list, role: str, sources: list, upload: bool):
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str) and rel.endswith(".md"):
        data = encode_operators(data)
    b = data.encode("utf-8") if isinstance(data, str) else data
    p.write_bytes(b)
    files.append({"path": rel, "role": role, "bytes": len(b), "sha256": sha256_bytes(b), "sources": sources, "upload": upload})


def build(out: Path):
    cfg = load_cfg()
    index = build_index()
    guide = agent_guide_sections()
    qa_text = qa_digest()
    norm = Norm(cfg, index)
    synth, warn, entries, docs, metric_docs = [], [], [], {}, {}
    for rel in cfg["scope"]["recipes"]:
        doc, e, mdocs = compile_recipe(rel, cfg, norm, guide, qa_text, synth, warn)
        docs[e["name"]] = doc
        e["metricDocs"] = [d[0] for d in mdocs]
        metric_docs[e["name"]] = mdocs
        entries.append(e)

    manifest_common = {
        "schemaVersion": 1,
        "generator": {"name": "build_copilot_package.py", "version": GENERATOR_VERSION},
        "libraryVersion": library_version(),
        "sourceCommit": git_head(),
        "limitsDocsCheckedOn": cfg["limits"]["docsCheckedOn"],
        "normalizations": {
            "toolRewrites": norm.tool_hits,
            "unmappedPathReferences": sorted(norm.unmapped_paths),
        },
        "synthesizedSections": synth,
        "warnings": warn,
    }
    refs = []
    for r in cfg["references"]:
        refs.append((r, (ROOT / r["source"]).read_text(encoding="utf-8")))

    # ── Copilot Studio
    cs_files = []
    cs = out / "copilot-studio"
    write(cs, "agent-instructions.txt", render_instructions(cfg, entries, "copilot-studio"), cs_files, "instructions", ["copilot/templates/agent-instructions.txt"], False)
    write(cs, "recipe-catalog.txt", render_catalog(entries), cs_files, "catalog", [e["source"] for e in entries], True)
    write(cs, "msp-profile-template.txt", render_profile(), cs_files, "msp-profile", ["config/msp-config.yaml"], True)
    for r, txt in refs:
        body = f"# {r['title']}\n\n<!-- Compiled from canonical source {r['source']} (sha256 {sha256_bytes(txt.encode())}) -->\n\n" + Norm(cfg, index).paths(txt)
        write(cs, f"references/{r['name']}.md", body, cs_files, "reference", [r["source"]], True)
    for e in entries:
        main_doc, parts_ = (split_run_card(e["name"], e["title"], docs[e["name"]]) if "(Run Card)" in docs[e["name"]].splitlines()[0] else (docs[e["name"]], []))
        write(cs, f"file-groups/{e['group']}/{e['name']}.md", main_doc, cs_files, "recipe", [e["source"]], True)
        for no, txt in parts_:
            write(cs, f"file-groups/{e['group']}/{e['name']}-part-{no}.md", txt, cs_files, "metrics", [e["source"]], True)
    for e in entries:
        for dname, slug, n, md in metric_docs[e["name"]]:
            write(cs, f"file-groups/metric-references/{dname}.md", md, cs_files, "metrics", [e["source"]], True)
    for e in entries:
        if e.get("plan"):
            write(cs, f"execution-plans/{e['name']}.json", json.dumps(e["plan"], indent=2, sort_keys=True) + "\n", cs_files, "plan", [e["source"]], False)
    for doc in ("setup-copilot-studio.md", "acceptance-tests.md"):
        write(cs, doc, (DOCS / doc).read_text(encoding="utf-8"), cs_files, "docs", [f"copilot/docs/{doc}"], False)
    cs_manifest = dict(manifest_common, edition="copilot-studio", fileGroups=sorted({e["group"] for e in entries}),
                       uploadFileCount=sum(1 for f in cs_files if f["upload"]),
                       recipes=[{k: e[k] for k in ("id", "name", "source", "sourceSha256", "group", "bundle", "tools", "dependencies")} for e in entries],
                       files=cs_files)
    (cs / "manifest.json").write_text(json.dumps(cs_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # ── Agent Builder
    ab_files = []
    ab = out / "agent-builder"
    write(ab, "agent-instructions.txt", render_instructions(cfg, entries, "agent-builder"), ab_files, "instructions", ["copilot/templates/agent-instructions.txt"], False)
    write(ab, "recipe-catalog.txt", render_catalog(entries), ab_files, "catalog", [e["source"] for e in entries], True)
    write(ab, "msp-profile-template.txt", render_profile(), ab_files, "msp-profile", ["config/msp-config.yaml"], True)
    for r, txt in refs:
        body = f"# {r['title']}\n\n<!-- Compiled from canonical source {r['source']} (sha256 {sha256_bytes(txt.encode())}) -->\n\n" + Norm(cfg, index).paths(txt)
        write(ab, f"{r['name']}.txt", to_txt(body), ab_files, "reference", [r["source"]], True)
    bundles = {}
    for e in entries:
        bundles.setdefault(e["bundle"], []).append(e)
    for bname, items in sorted(bundles.items()):
        sep = "\n\n" + "=" * 72 + "\n\n"
        text = f"LIONGARD COMPILED RECIPE BUNDLE: {bname}\nRecipes in this bundle: {', '.join(i['name'] for i in items)}\n" + sep
        text += sep.join(f"RECIPE: {i['name']}\n\n{docs[i['name']]}" for i in sorted(items, key=lambda i: i["name"]))
        write(ab, f"{bname}.txt", to_txt(text), ab_files, "bundle", [i["source"] for i in items], True)
    for bname, items in sorted(bundles.items()):
        mt = [(d[0], d[3]) for i in sorted(items, key=lambda i: i["name"]) for d in metric_docs[i["name"]]]
        if mt:
            sep = "\n\n" + "=" * 72 + "\n\n"
            text = f"LIONGARD METRIC REFERENCE DOCUMENTS for bundle {bname}\nDocuments: {', '.join(n for n, _ in mt)}\n" + sep + sep.join(f"DOCUMENT: {n}\n\n{t}" for n, t in mt)
            write(ab, f"{bname}-metrics.txt", to_txt(text), ab_files, "metrics", [i["source"] for i in items], True)
    for e in entries:
        if e.get("plan"):
            write(ab, f"execution-plans/{e['name']}.json", json.dumps(e["plan"], indent=2, sort_keys=True) + "\n", ab_files, "plan", [e["source"]], False)
    for doc in ("setup-agent-builder.md", "acceptance-tests.md"):
        write(ab, doc, (DOCS / doc).read_text(encoding="utf-8"), ab_files, "docs", [f"copilot/docs/{doc}"], False)
    ab_manifest = dict(manifest_common, edition="agent-builder", uploadFileCount=sum(1 for f in ab_files if f["upload"]),
                       recipes=cs_manifest["recipes"], files=ab_files)
    (ab / "manifest.json").write_text(json.dumps(ab_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ───────────────────────── validation ─────────────────────────
def validate(tree: Path) -> list:
    cfg = load_cfg()
    errs = []
    # Partner/customer names must never be written into tracked files, so the patterns are
    # read from the local, gitignored .scrub-patterns file (same file the internal gate uses).
    # Without it the build still runs; the internal verify-promotion.sh gate covers scrubbing.
    sp = ROOT / ".scrub-patterns"
    pats = [l.strip() for l in sp.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if sp.exists() else []
    scrub = re.compile("|".join(pats), re.I) if pats else None
    for f in tree.rglob("*.md"):
        t = f.read_text(encoding="utf-8")
        if "==" in t or "&&" in t:
            errs.append(f"{f.relative_to(tree)}: contains '==' or '&&' (Copilot ingestion corrupts them; encode as EQ_OP / AND_OP)")
    for edition in ("copilot-studio", "agent-builder"):
        d = tree / edition
        mpath = d / "manifest.json"
        if not mpath.exists():
            errs.append(f"{edition}: manifest.json missing")
            continue
        m = json.loads(mpath.read_text(encoding="utf-8"))
        lim = cfg["limits"]["copilotStudio" if edition == "copilot-studio" else "agentBuilder"]
        for w in m.get("warnings", []):
            errs.append(f"{edition}: build warning: {w}")
        listed = {f["path"] for f in m["files"]}
        on_disk = {str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and p.name not in ("manifest.json", ".DS_Store")}
        for extra in sorted(on_disk - listed):
            errs.append(f"{edition}: file not in manifest: {extra}")
        for f in m["files"]:
            p = d / f["path"]
            if not p.exists():
                errs.append(f"{edition}: manifest file missing on disk: {f['path']}")
                continue
            b = p.read_bytes()
            if sha256_bytes(b) != f["sha256"]:
                errs.append(f"{edition}: checksum mismatch: {f['path']}")
            txt = b.decode("utf-8", "replace")
            if scrub and scrub.search(txt):
                errs.append(f"{edition}: scrub pattern hit in {f['path']}")
            if f["upload"] and p.suffix not in lim["uploadExtensions"]:
                errs.append(f"{edition}: unsupported upload extension {p.suffix}: {f['path']}")
            if f["role"] in ("recipe", "bundle"):
                for h in (RUN_CARD_HEADINGS if "(Run Card)" in txt.splitlines()[0] else REQUIRED_HEADINGS):
                    if h not in txt:
                        errs.append(f"{edition}: {f['path']} missing heading '{h}'")
                body_wo_trace = "\n".join(l for l in txt.splitlines() if "Canonical source" not in l)
                if FORBIDDEN_PATH.search(body_wo_trace):
                    errs.append(f"{edition}: relative repo path left in {f['path']}: {FORBIDDEN_PATH.search(body_wo_trace).group(0)}")
                if "liongard_system" in txt:
                    errs.append(f"{edition}: deprecated tool liongard_system in {f['path']}")
            if f["role"] == "instructions" and len(txt) > lim["agentInstructionsMaxChars"]:
                errs.append(f"{edition}: instructions {len(txt)} chars > {lim['agentInstructionsMaxChars']}")
        cap = lim.get("maxUploadFiles", lim.get("maxKnowledgeFiles"))
        if m["uploadFileCount"] > cap:
            errs.append(f"{edition}: {m['uploadFileCount']} upload files > limit {cap}")
        want = sum(r["dependencies"]["primitiveCount"] for r in m["recipes"])
        have = sum(len(re.findall(r"^- \*\*`metrics:|^- \*\*P\d{3}\*\* metricId", (d / f["path"]).read_text(encoding="utf-8"), re.M)) for f in m["files"] if f["role"] in ("metrics", "recipe", "bundle", "bundle-metrics"))
        if have != want:
            errs.append(f"{edition}: metric reference documents embed {have} primitives, recipes declare {want}")
        for f in m["files"]:
            if f["role"] in ("recipe", "bundle") and "Metric reference document" in (d / f["path"]).read_text(encoding="utf-8"):
                docs_named = re.findall(r"`(metrics-[a-z0-9-]+)`", (d / f["path"]).read_text(encoding="utf-8"))
                alltxt = "".join((d / g["path"]).read_text(encoding="utf-8") for g in m["files"] if g["role"] == "metrics")
                for dn in set(docs_named):
                    if dn not in alltxt:
                        errs.append(f"{edition}: {f['path']} names missing metric document {dn}")
        for r in m["recipes"]:
            src = ROOT / r["source"]
            if not src.exists():
                errs.append(f"{edition}: source missing: {r['source']}")
            elif sha256_bytes(src.read_bytes()) != r["sourceSha256"]:
                errs.append(f"{edition}: STALE - canonical source changed since build: {r['source']}")
    return errs


def tree_diff(a: Path, b: Path) -> list:
    errs = []
    fa = {str(p.relative_to(a)) for p in a.rglob("*") if p.is_file() and p.name != ".DS_Store"}
    fb = {str(p.relative_to(b)) for p in b.rglob("*") if p.is_file() and p.name != ".DS_Store"}
    for f in sorted(fa ^ fb):
        errs.append(f"STALE: file added/removed: {f}")
    for f in sorted(fa & fb):
        if f.endswith("manifest.json"):
            ma, mb = json.loads((a / f).read_text()), json.loads((b / f).read_text())
            for k in MANIFEST_VOLATILE:
                ma.pop(k, None)
                mb.pop(k, None)
            if ma != mb:
                errs.append(f"STALE: {f} differs")
        elif (a / f).read_bytes() != (b / f).read_bytes():
            errs.append(f"STALE: {f} differs from a fresh build")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="fail if copilot/generated is stale or invalid")
    g.add_argument("--validate", action="store_true", help="validate committed output only")
    a = ap.parse_args()

    if a.validate:
        errs = validate(GENERATED)
    elif a.check:
        with tempfile.TemporaryDirectory() as t:
            fresh = Path(t)
            build(fresh)
            errs = validate(fresh) + (tree_diff(GENERATED, fresh) if GENERATED.exists() else ["STALE: copilot/generated missing"])
    else:
        # Build into a temp dir, then sync: overwrite changed files, remove stale ones (best effort).
        with tempfile.TemporaryDirectory() as t:
            fresh = Path(t)
            build(fresh)
            GENERATED.mkdir(parents=True, exist_ok=True)
            fresh_files = {p.relative_to(fresh) for p in fresh.rglob("*") if p.is_file()}
            for old in sorted(p for p in GENERATED.rglob("*") if p.is_file()):
                if old.relative_to(GENERATED) not in fresh_files:
                    try:
                        old.unlink()
                    except OSError as exc:
                        print(f"  ! could not remove stale file {old.relative_to(ROOT)}: {exc}")
            for rel in fresh_files:
                dest = GENERATED / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((fresh / rel).read_bytes())
        errs = validate(GENERATED)
        print(f"Built {GENERATED.relative_to(ROOT)}")
    if errs:
        print("\n".join(f"  x {e}" for e in errs))
        print(f"\nFAILED: {len(errs)} problem(s)")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
