"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
from math import isfinite
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item
from lab9.graders import GRADERS


def _report_index(report: dict, label: str, graded: set[str], problems: list[str]) -> dict:
    manifest = report["manifest"]
    seeds = manifest["seeds"]
    rows = report["rows"]
    index = {(row["item_id"], row["seed"]): frozenset(row.get("slices") or ()) for row in rows}
    items = {item for item, _ in index}
    expected = {(item, seed) for item in items for seed in seeds}
    if len(rows) != manifest["items"] * len(seeds) or len(items) != manifest["items"]:
        problems.append(f"{label}: row or item count disagrees with manifest")
    if len(index) != len(rows):
        problems.append(f"{label}: duplicate (item_id, seed) pairs")
    if index.keys() != expected or not seeds or not items or len(seeds) != len(set(seeds)):
        problems.append(f"{label}: incomplete or invalid item × seed grid")
    if report.get("evaluator_failures"):
        problems.append(f"{label}: evaluator_failures is non-empty")
    for metric, value in report["metrics"].items():
        if value is not None and (not isinstance(value, (int, float)) or not isfinite(value)):
            problems.append(f"{label}: invalid aggregate for {metric}")
    for metric in sorted(graded):
        if any(not isinstance(row.get(metric), (bool, int, float)) or not isfinite(row[metric]) for row in rows):
            problems.append(f"{label}: missing or invalid row values for {metric}")
    return index


def _threshold_regressions(current: dict, previous: dict) -> list[str]:
    relaxed = []
    if "min" in previous and ("min" not in current or not current["min"] >= previous["min"]):
        relaxed.append("min")
    for limit in ("max", "max_increase"):
        if limit in previous and (limit not in current or not current[limit] <= previous[limit]):
            relaxed.append(limit)
    if previous.get("no_significant_drop") and not current.get("no_significant_drop"):
        relaxed.append("no_significant_drop")
    return relaxed


def _ratchet(spec: dict, base_spec: dict) -> list[str]:
    problems = []
    for section in ("metrics", "slices"):
        def rule_id(rule):
            return rule["id"] if section == "metrics" else f"slice:{rule['name']}/{rule['metric']}"

        current = {rule_id(rule): rule for rule in spec.get(section, [])}
        for old in base_spec.get(section, []):
            key = rule_id(old)
            new = current.get(key)
            if new is None:
                problems.append(f"ratchet: removed {key}")
                continue
            if old.get("blocking") and not new.get("blocking"):
                problems.append(f"ratchet: {key} is no longer blocking")
            old_threshold = old.get("threshold", {}) if section == "metrics" else old
            new_threshold = new.get("threshold", {}) if section == "metrics" else new
            for field in _threshold_regressions(new_threshold, old_threshold):
                problems.append(f"ratchet: {key} loosened {field}")
    return problems


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems: list[str] = []
    graded = {metric["id"] for metric in spec["metrics"]} & GRADERS.keys()
    pr_index = _report_index(pr, "PR", graded, problems)
    base_index = _report_index(base, "baseline", graded, problems)
    if pr_index.keys() != base_index.keys():
        problems.append("PR: (item_id, seed) pairs differ from baseline")
    if any(pr_index[key] != base_index[key] for key in pr_index.keys() & base_index.keys()):
        problems.append("PR: slice tags differ from baseline")
    if base_spec is not None and spec["eval_set_version"] == base_spec["eval_set_version"]:
        problems.extend(_ratchet(spec, base_spec))
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for rule in spec.get("slices", []):
        name, metric = rule["name"], rule["metric"]
        rule_id = f"slice:{name}/{metric}"
        scores = per_item(pr, metric, slice_name=name)
        reference = per_item(base, metric, slice_name=name)
        if not scores or scores.keys() != reference.keys():
            failed, details = True, "missing or unmatched item scores"
        else:
            value = sum(scores.values()) / len(scores)
            floor = rule.get("min")
            failed = floor is not None and value < floor
            details = f"{value:.4f} (min {floor})" if floor is not None else f"{value:.4f}"
            if rule.get("no_significant_drop"):
                keys = sorted(scores)
                delta, lo, hi = stats.paired_bootstrap(
                    [scores[key] for key in keys], [reference[key] for key in keys],
                    n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                    confidence=bs.get("confidence", 0.95),
                )
                failed = failed or hi < 0
                details += f" Δ {delta:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
        blocking = rule.get("blocking", False)
        if failed and blocking:
            blocked.append(rule_id)
        verdict = "ok" if not failed else ("BLOCK" if blocking else "warn")
        lines.append(f"  {rule_id:<34} {details} {verdict}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap(
                [a[k] for k in keys], [b[k] for k in keys],
                n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                confidence=bs.get("confidence", 0.95),
            )
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
