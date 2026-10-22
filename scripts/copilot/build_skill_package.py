#!/usr/bin/env python3
"""Build the Copilot Studio *skill* edition of the Liongard recipe library.

A Copilot Studio skill is a zip with SKILL.md at the root plus resource files the agent reads whole
(progressive disclosure), instead of semantic knowledge search. That removes the knowledge-edition
workarounds (operator encoding, run-card splitting, per-turn search budget batching).

Output (deterministic, never hand-edit):
  copilot/generated-skills/liongard-recipes/        unpacked skill (SKILL.md, recipes/, plans/, references/, manifest.json)
  copilot/generated-skills/liongard-recipes.zip     upload this in Copilot Studio > Build > Skills > Upload a skill

Hierarchy is preserved, not flattened:
  primitive -> single-system recipe -> same-type rollup -> cross-type environment / QBR / onboarding recipe
manifest.json records it (dependencies.composes per recipe); plans/<recipe>.json holds the exact metric list
(per inspector, sequence ids identical to the knowledge edition) for every recipe that declares primitives.

Usage:
  python3 scripts/copilot/build_skill_package.py            build + validate
  python3 scripts/copilot/build_skill_package.py --check    fail if the committed output is stale or invalid
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_copilot_package as base  # noqa: E402  (shared helpers: primitives, sequencing, hashing)

ROOT = base.ROOT
OUT = ROOT / "copilot" / "generated-skills"
TEMPLATE = ROOT / "copilot" / "templates" / "skill-instructions.md"
GENERATOR_VERSION = "0.1.0-spike"
ZIP_DATE = (2026, 1, 1, 0, 0, 0)  # fixed timestamp -> byte-identical zips


def recipe_index():
    idx = {}
    for p in sorted((ROOT / "recipes").rglob("*.md")):
        if p.name in {"README.md", "AGENTS.md"}:
            continue
        fm, body = base.split_frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("name"):
            idx[fm["name"]] = (p.relative_to(ROOT).as_posix(), fm, body)
    return idx


def resolve(roots, idx, warn, no_follow=()):
    """Roots plus everything they compose, transitively, in a stable order. Recipes in no_follow are
    re-scoped to deployed single-system recipes, so their composed rollups are not pulled in."""
    order, stack = [], list(reversed(roots))
    while stack:
        n = stack.pop()
        if n in order:
            continue
        if n not in idx:
            warn.append(f"composed recipe not in library: {n}")
            continue
        order.append(n)
        if n in no_follow:
            continue
        for c in reversed(idx[n][1].get("composes") or []):
            stack.append(str(c).split(":")[-1])
    return order


def rewrite_paths(text, bundled, refs, home=None, current=None):
    """Repo-relative links -> paths inside the skill (or the sibling Liongard skill that holds the recipe),
    or an explicit 'not bundled' marker."""
    stem_to_name = {Path(rel).stem: n for n, rel in bundled.items()}
    home = home or {}

    def link(m):
        label, path = m.group(1), m.group(2)
        return f"{label} ({target(path)})"

    def target(path):
        p = Path(path.split("#")[0])
        if p.parts and p.parts[0] in ("recipes",) or p.suffix == ".md" and p.stem in stem_to_name:
            n = stem_to_name.get(p.stem)
            if not n:
                return f"library recipe {p.stem} (not bundled)"
            other = home.get(n)
            return f"`recipes/{n}.md`" + (f" (in the `{other}` skill)" if other and other != current else "")
        if p.name in refs:
            return f"`references/{p.name}`"
        return f"library file {p.name} (not bundled)"

    text = re.sub(r"\[([^\]]+)\]\(((?:\.\./)*(?:reference|templates|config|primitives|personas|recipes)/[^)\s]*)\)", link, text)
    text = re.sub(r"\[([^\]]+)\]\(((?:\.\./)*[a-z0-9-]+\.md)\)", link, text)
    return re.sub(r"(?<![\w/`])(?:\.\./)*(?:reference|templates|config|primitives|personas|recipes)/[\w./-]+\.(?:md|yaml)",
                  lambda m: target(m.group(0)), text)


def add_single_system_note(text, singles):
    """Package override for environment-level recipes: chain the single-system recipe of each deployed vendor
    (the approach the library and the Cowork baseline use) instead of the type-wide rollups."""
    note = (
        "> **Package scope (read first).** In this skill, every step that chains another recipe (Phase 0, Step 5, and any rollup "
        "named elsewhere) runs per deployed vendor: find deployed inspectors with `liongard_launchpoint`, and for each one that has a "
        "single-system recipe here (" + (", ".join(f"`{s}`" for s in singles) if len(singles) <= 15 else "see the single-system section of `recipes/index.md`") + "), open `recipes/<name>.md` and `plans/<name>.json` "
        "and run that recipe fully for its systems. Do not run the type-wide rollups (all-servers, all-firewalls, all-backups, all-edrs, "
        "all-domains, all-hypervisors, all-external-attack-surface). Classes with no packaged single-system recipe (servers, endpoints, "
        "backups, hypervisors, domains, external attack surface) come from the inventory and dashboard tools (`liongard_device`, "
        "`liongard_identity`, `liongard_domain`, `liongard_cyber_risk_dashboard`) and are listed in the coverage table as "
        "\"no packaged vendor recipe\".\n\n"
    )
    if text.startswith("---\n"):
        end = text.find("\n---", 4) + 4
        return text[:end] + "\n\n" + note + text[end:].lstrip("\n")
    return note + text


def plan_for(name, fm, warn):
    ids = fm.get("primitives") or []
    if not ids:
        return None
    _, _, vendors = base.render_primitives(ids, [], name, name, inline=True)
    prims = base.load_primitives()
    out = []
    for v in vendors:
        rows = []
        for pr in v["primitives"]:
            src = prims.get(pr["id"], {})
            rows.append({
                "seq": pr["seq"],
                "id": pr["id"],
                "name": base.one_line(src.get("name", "")).split(" — ")[-1],
                "metricId": src.get("liongardMetricId"),
                "jmesPathQuery": src.get("jmesPath", pr["query"]),
                "resultType": src.get("resultType"),
                "okWhen": src.get("compliantWhen"),
                "gotcha": base.one_line(str(src.get("fieldGotcha"))) if src.get("fieldGotcha") else None,
                "status": src.get("status"),
            })
        out.append({"inspectorSlug": v["inspectorSlug"], "inspectorId": v["inspectorId"], "metrics": rows})
    total = sum(len(v["metrics"]) for v in out)
    if total != len(ids):
        warn.append(f"{name}: plan has {total} metrics, frontmatter declares {len(ids)}")
    return {"recipe": name, "metricCount": total, "inspectors": out}


GROUPS = [("single-system", "Single-system assessments (one vendor)"), ("same-type rollup", "Same-type rollups (all systems of one type)"),
          ("environment-level", "Environment-level, compliance, QBR, onboarding and domain assessments")]


def render_index(entries):
    out = ["# Recipe index", "", "Pick the recipe whose name or 'Use when' matches the request, then open `recipes/<name>.md` "
           "(and `plans/<name>.json` when listed).", ""]
    for kind, title in GROUPS:
        out += [f"## {title}", ""]
        for e in (x for x in entries if x["type"] == kind):
            plan = f" Plan: `plans/{e['name']}.json` ({e['metricCount']} metrics)." if e["metricCount"] else ""
            comp = f" Composes: {', '.join(e['composes'])}." if e["composes"] else ""
            out.append(f"- `{e['name']}`.{plan}{comp} Use when: {e['useWhen']}")
        out.append("")
    return "\n".join(out)


def render_skill_md(cfg, sp, specs, entries):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    counts = {k: sum(1 for e in entries if e["type"] == k) for k, _ in GROUPS}
    cat = ("The recipes in this skill, with trigger phrases, are listed in `recipes/index.md`; read it first to pick the recipe. "
           + "; ".join(f"{t}: {counts[k]}" for k, t in GROUPS if counts[k]) + ".")
    others = [o for o in specs if o["name"] != sp["name"]]
    sib = ("The Liongard library is split across these skills; when the recipe you need, or a recipe a step composes, is in another one, "
           "use that skill and open the file there: " + "; ".join(f"`{o['name']}` ({o['title']})" for o in others) + ".") if others else ""
    return (tpl.replace("{{NAME}}", sp["name"]).replace("{{DESCRIPTION}}", json.dumps(sp["description"], ensure_ascii=False)).replace("{{TITLE}}", sp["title"])
            .replace("{{CATALOG}}", cat).replace("{{SIBLINGS}}", sib)
            .replace("{{REFERENCES}}", ", ".join(f"`references/{Path(r).name}`" for r in cfg["references"])))


def kind_of(rel):
    cat = rel.split("/")[1]
    return {"single-system-analysis": "single-system", "system-type": "same-type rollup", "system-type-assessment": "same-type rollup"}.get(cat, "environment-level")


def skill_of(rel, specs):
    cat = rel.split("/")[1]
    for sp in specs:
        if cat in sp["categories"]:
            return sp["name"]
    return specs[-1]["name"]


def build(out_dir: Path):
    cfg = base.load_cfg()["skill"]
    specs = cfg["skills"]
    idx, warn = recipe_index(), []
    chain_single = set(cfg.get("chainToSingleSystem", []))
    roots = sorted(idx) if cfg["roots"] == "all" else cfg["roots"] + cfg.get("alsoInclude", [])
    names = resolve(roots, idx, warn, chain_single)
    bundled = {n: idx[n][0] for n in names}
    home = {n: skill_of(idx[n][0], specs) for n in names}
    refs = [Path(r).name for r in cfg["references"]]
    singles = [m for m in names if idx[m][0].split("/")[1] == "single-system-analysis"]
    release = {"schemaVersion": 1, "generator": {"name": "build_skill_package.py", "version": GENERATOR_VERSION},
               "libraryVersion": base.library_version(), "sourceCommit": base.git_head(), "skills": []}
    for sp in specs:
        skill = out_dir / sp["name"]
        files, entries = [], []

        def put(rel, data: str, role, sources):
            p = skill / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            b = data.encode("utf-8")
            p.write_bytes(b)
            files.append({"path": rel, "role": role, "bytes": len(b), "sha256": base.sha256_bytes(b), "sources": sources})

        for n in (x for x in names if home[x] == sp["name"]):
            rel, fm, body = idx[n]
            raw = (ROOT / rel).read_bytes()
            plan = plan_for(n, fm, warn)
            if plan:
                plan["sourceSha256"] = base.sha256_bytes(raw)
                put(f"plans/{n}.json", json.dumps(plan, separators=(",", ":"), ensure_ascii=False) + "\n", "plan", [rel])
            text = rewrite_paths(raw.decode("utf-8"), bundled, refs, home, sp["name"])
            if n in chain_single:
                text = add_single_system_note(text, singles)
            put(f"recipes/{n}.md", text, "recipe", [rel])
            entries.append({
                "name": n, "source": rel, "sourceSha256": base.sha256_bytes(raw), "type": kind_of(rel),
                "composes": (singles if n in chain_single
                             else [str(c).split(":")[-1] for c in (fm.get("composes") or []) if str(c).split(":")[-1] in bundled]),
                "metricCount": plan["metricCount"] if plan else 0,
                "useWhen": base.one_line(str(fm.get("description", "")))[:240],
            })
        for r in cfg["references"]:
            put(f"references/{Path(r).name}", rewrite_paths((ROOT / r).read_text(encoding="utf-8"), bundled, refs, home, sp["name"]), "reference", [r])
        put("recipes/index.md", render_index(entries), "catalog", [e["source"] for e in entries])
        put("SKILL.md", render_skill_md(cfg, sp, specs, entries), "skill", ["copilot/templates/skill-instructions.md"])
        manifest = {"schemaVersion": 1, "skill": sp["name"], "recipes": entries, "files": files, "warnings": warn}
        (skill / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        # deterministic zip: sorted entries, fixed timestamps, SKILL.md at the root, manifest kept outside the zip
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(files, key=lambda f: f["path"]):
                zi = zipfile.ZipInfo(f["path"], ZIP_DATE)
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, (skill / f["path"]).read_bytes())
        data = buf.getvalue()
        (out_dir / f"{sp['name']}.zip").write_bytes(data)
        release["skills"].append({"name": sp["name"], "zip": f"{sp['name']}.zip", "zipSha256": base.sha256_bytes(data),
                                  "recipes": len(entries), "files": len(files),
                                  "uncompressedBytes": sum(f["bytes"] for f in files)})
    (out_dir / "manifest.json").write_text(json.dumps(release, indent=1) + "\n", encoding="utf-8")
    build_release(out_dir, release)


RELEASE_DIR = "Liongard-Copilot-Studio"


def build_release(out_dir: Path, release: dict):
    """Partner release package: START-HERE.html, skills/*.zip, agent-instructions.txt, manifest.json."""
    rel = out_dir / "release" / RELEASE_DIR
    (rel / "skills").mkdir(parents=True, exist_ok=True)
    items = []

    def add(name, data: bytes):
        (rel / name).write_bytes(data)
        items.append({"path": name, "bytes": len(data), "sha256": base.sha256_bytes(data)})

    add("START-HERE.html", (ROOT / "copilot" / "docs" / "setup-copilot-skill.html").read_bytes())
    add("agent-instructions.txt", (ROOT / "copilot" / "templates" / "skill-agent-instructions.txt").read_bytes())
    for s in release["skills"]:
        add(f"skills/{s['zip']}", (out_dir / s["zip"]).read_bytes())
    man = {k: v for k, v in release.items() if k != "skills"}
    man["edition"] = "copilot-studio-skills"
    man["skills"] = [{k: s[k] for k in ("name", "zip", "zipSha256", "recipes", "files", "uncompressedBytes")} for s in release["skills"]]
    man["files"] = items
    (rel / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(x for x in rel.rglob("*") if x.is_file()):
            zi = zipfile.ZipInfo(f"{RELEASE_DIR}/{p.relative_to(rel).as_posix()}", ZIP_DATE)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, p.read_bytes())
    (out_dir / "release" / f"{RELEASE_DIR}-{man['libraryVersion']}.zip").write_bytes(buf.getvalue())


def validate(out_dir: Path) -> list:
    cfg = base.load_cfg()["skill"]
    lim = base.load_cfg()["limits"]["skills"]
    errs = []
    rel = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    if len(rel["skills"]) > lim["maxSkillsPerAgent"]:
        errs.append(f"{len(rel['skills'])} skills > {lim['maxSkillsPerAgent']} per agent")
    total_files = sum(s["files"] for s in rel["skills"])
    if total_files > lim["maxFilesPerAgent"]:
        errs.append(f"{total_files} files across skills > {lim['maxFilesPerAgent']}")
    sp_ = ROOT / ".scrub-patterns"
    pats = [l.strip() for l in sp_.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if sp_.exists() else []
    scrub = re.compile("|".join(pats), re.I) if pats else None
    all_recipes = {}
    for s in rel["skills"]:
        skill = out_dir / s["name"]
        m = json.loads((skill / "manifest.json").read_text(encoding="utf-8"))
        for e in m["recipes"]:
            all_recipes[e["name"]] = s["name"]
    for s in rel["skills"]:
        skill, tag = out_dir / s["name"], s["name"]
        m = json.loads((skill / "manifest.json").read_text(encoding="utf-8"))
        errs += [f"{tag}: build warning: {w}" for w in m["warnings"]]
        if s["uncompressedBytes"] > lim["maxSkillUncompressedBytes"]:
            errs.append(f"{tag}: {s['uncompressedBytes']} uncompressed bytes > {lim['maxSkillUncompressedBytes']} (Copilot Studio silently rejects larger skills)")
        for f in m["files"]:
            p = skill / f["path"]
            if not p.exists():
                errs.append(f"{tag}: missing on disk: {f['path']}")
                continue
            b = p.read_bytes()
            if base.sha256_bytes(b) != f["sha256"]:
                errs.append(f"{tag}: checksum mismatch: {f['path']}")
            txt = b.decode("utf-8", "replace")
            if scrub and scrub.search(txt):
                errs.append(f"{tag}: scrub pattern hit: {f['path']}")
            if len(Path(f["path"]).parts) - 1 > lim["maxDirectoryDepth"]:
                errs.append(f"{tag}: directory depth > {lim['maxDirectoryDepth']}: {f['path']}")
            if p.suffix not in lim["fileExtensions"]:
                errs.append(f"{tag}: unsupported file type: {f['path']}")
            if re.search(r"(?i)(accessKeySecret\s*[:=]\s*\w|bearer\s+[a-z0-9]{20,}|password\s*[:=]\s*\S+)", txt):
                errs.append(f"{tag}: possible credential in {f['path']}")
        sk = (skill / "SKILL.md").read_text(encoding="utf-8")
        head = sk.split("\n---", 1)[0]
        try:
            fm = base.yaml.safe_load(head[4:]) if sk.startswith("---\n") else None
        except Exception as exc:  # invalid YAML -> Copilot Studio silently drops the upload
            fm, _ = None, errs.append(f"{tag}: SKILL.md front matter is not valid YAML: {exc}")
        if not isinstance(fm, dict) or not fm.get("name") or not fm.get("description"):
            errs.append(f"{tag}: SKILL.md needs YAML front matter with name and description")
        if len(sk) > lim["skillMdMaxChars"]:
            errs.append(f"{tag}: SKILL.md {len(sk)} chars > {lim['skillMdMaxChars']}")
        z = out_dir / s["zip"]
        if not z.exists() or z.stat().st_size > lim["maxZipBytes"]:
            errs.append(f"{tag}: zip missing or > {lim['maxZipBytes']}")
        else:
            with zipfile.ZipFile(z) as zf:
                names = set(zf.namelist())
                if "SKILL.md" not in names:
                    errs.append(f"{tag}: zip: SKILL.md not at root")
                if names != {f["path"] for f in m["files"]}:
                    errs.append(f"{tag}: zip contents differ from manifest")
        for e in m["recipes"]:
            if base.sha256_bytes((ROOT / e["source"]).read_bytes()) != e["sourceSha256"]:
                errs.append(f"{tag}: STALE source: {e['source']}")
            if e["metricCount"]:
                plan = json.loads((skill / f"plans/{e['name']}.json").read_text(encoding="utf-8"))
                seqs = [r["seq"] for v in plan["inspectors"] for r in v["metrics"]]
                if seqs != [f"P{i:03d}" for i in range(1, len(seqs) + 1)]:
                    errs.append(f"{tag}: {e['name']}: sequence ids not contiguous")
                if any(r.get("status") == "PROPOSED" for v in plan["inspectors"] for r in v["metrics"]):
                    errs.append(f"{tag}: {e['name']}: plan contains PROPOSED metrics (recipes may only use validated metrics)")
                if any(not r["jmesPathQuery"] and not r["metricId"] for v in plan["inspectors"] for r in v["metrics"]):
                    errs.append(f"{tag}: {e['name']}: metric with neither metricId nor query")
            for c in e["composes"]:
                if c not in all_recipes:
                    errs.append(f"{tag}: {e['name']}: composed recipe {c} not in any skill")
        for f in skill.rglob("*.md"):
            left = re.findall(r"(?<![\w/`(])(?:reference|templates|config|primitives|personas)/[\w./-]+\.(?:md|yaml)", f.read_text(encoding="utf-8"))
            if left:
                errs.append(f"{tag}: unrewritten repo path in {f.relative_to(skill)}: {left[0]}")
    rdir = out_dir / "release" / RELEASE_DIR
    if not rdir.exists():
        errs.append("release package missing")
    else:
        rm = json.loads((rdir / "manifest.json").read_text(encoding="utf-8"))
        for f in rm["files"]:
            p = rdir / f["path"]
            if not p.exists() or base.sha256_bytes(p.read_bytes()) != f["sha256"]:
                errs.append(f"release: checksum mismatch or missing: {f['path']}")
            elif scrub and p.suffix in (".html", ".txt") and scrub.search(p.read_text(encoding="utf-8")):
                errs.append(f"release: scrub pattern hit: {f['path']}")
        if not list((out_dir / "release").glob(f"{RELEASE_DIR}-*.zip")):
            errs.append("release zip missing")
    return errs


def summary(out_dir):
    rel = json.loads((out_dir / "manifest.json").read_text())
    return "; ".join(f"{s['name']}: {s['recipes']} recipes, {s['files']} files, {s['uncompressedBytes'] / 1e6:.2f} MB" for s in rel["skills"])


def tree_equal(a: Path, b: Path) -> list:
    errs = []
    def tracked(root):  # zips and the release package are gitignored build outputs
        return {f for f in (p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
                if not f.endswith(".zip") and not f.startswith("release/") and not f.endswith(".DS_Store")}
    fa, fb = tracked(a), tracked(b)
    errs += [f"STALE: added/removed {f}" for f in sorted(fa ^ fb)]
    for f in sorted(fa & fb):
        if f.endswith("manifest.json"):
            ma, mb = json.loads((a / f).read_text()), json.loads((b / f).read_text())
            ma.pop("sourceCommit", None)
            mb.pop("sourceCommit", None)
            if ma != mb:
                errs.append(f"STALE: {f}")
        elif f.endswith(".zip") or f.endswith("release/Liongard-Copilot-Studio/manifest.json"):
            continue  # zip embeds manifest (sourceCommit); its contents are covered file by file
        elif (a / f).read_bytes() != (b / f).read_bytes():
            errs.append(f"STALE: {f}")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as t:
        fresh = Path(t)
        build(fresh)
        errs = validate(fresh)
        if a.check:
            errs += tree_equal(OUT, fresh) if OUT.exists() else ["STALE: copilot/generated-skills missing"]
        else:
            import shutil
            shutil.rmtree(OUT, ignore_errors=True)
            shutil.copytree(fresh, OUT)
            print(f"Built {OUT.relative_to(ROOT)}: {summary(OUT)}")
    if errs:
        print("\n".join(f"  x {e}" for e in errs))
        print(f"\nFAILED: {len(errs)} problem(s)")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
