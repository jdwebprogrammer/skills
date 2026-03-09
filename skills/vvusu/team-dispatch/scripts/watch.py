#!/usr/bin/env python3
"""Team Dispatch Watcher (low-frequency reconciliation)

Purpose
- Provide a *low-frequency* safety net when completion events are missed.
- Detect and surface "stuck" tasks (in-progress longer than timeoutSeconds + grace).

What it does
- Scans ~/.openclaw/workspace/tasks/active/*.json
- For each task in-progress:
    - If overdue -> mark as failed with error=timeout and increment retries
    - If retries remain -> reset to pending (so the main agent can re-dispatch)
    - Else -> keep failed and mark project blocked

What it does NOT do
- It does not dispatch agents (that is the main agent's job via sessions_spawn).
- It does not attempt to parse session store to infer completion.

Usage
  python3 scripts/watch.py --interval 60 --grace 15

Recommended
- interval: 30-120s (adaptive is implemented; this is the max sleep)
- grace: 10-30s
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

TZ_SH = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(TZ_SH).isoformat(timespec="seconds")


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        # Python can parse ISO with offset
        return datetime.fromisoformat(s)
    except Exception:
        return None


@dataclass
class ScanResult:
    changed_files: int = 0
    overdue_tasks: int = 0
    reset_to_pending: int = 0
    blocked_projects: int = 0


def scan_file(path: str, grace: int) -> tuple[bool, dict, ScanResult]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    retry_limit = int(data.get("retryLimit", 1))
    project_status = data.get("status", "active")

    changed = False
    sr = ScanResult()

    if project_status not in ("active", "blocked"):
        return False, data, sr

    tasks = data.get("tasks", [])
    for t in tasks:
        if t.get("status") != "in-progress":
            continue
        started = parse_iso(t.get("startedAt"))
        timeout_s = int(t.get("timeoutSeconds", 60))
        if not started:
            continue

        deadline = started.timestamp() + timeout_s + grace
        if time.time() <= deadline:
            continue

        # overdue
        sr.overdue_tasks += 1
        t["error"] = f"timeout: exceeded {timeout_s}s (+{grace}s grace)"
        t["status"] = "failed"
        t["completedAt"] = now_iso()
        t["retries"] = int(t.get("retries", 0)) + 1
        changed = True

        if t["retries"] <= retry_limit:
            # auto retry: reset to pending
            t["status"] = "pending"
            t["startedAt"] = None
            t["sessionKey"] = None
            sr.reset_to_pending += 1
        else:
            # retries exhausted -> block project (default strategy)
            data["status"] = "blocked"
            sr.blocked_projects += 1

    if changed:
        sr.changed_files += 1
    return changed, data, sr


def scan_once(tasks_dir: str, grace: int) -> ScanResult:
    out = ScanResult()
    for path in glob.glob(os.path.join(tasks_dir, "active", "*.json")):
        changed, data, sr = scan_file(path, grace=grace)
        out.changed_files += sr.changed_files
        out.overdue_tasks += sr.overdue_tasks
        out.reset_to_pending += sr.reset_to_pending
        out.blocked_projects += sr.blocked_projects
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-dir", default=os.path.expanduser("~/.openclaw/workspace/tasks"))
    ap.add_argument("--interval", type=int, default=60, help="max sleep between scans (seconds)")
    ap.add_argument("--grace", type=int, default=15, help="grace seconds after timeoutSeconds")
    ap.add_argument("--once", action="store_true", help="run one scan and exit")
    args = ap.parse_args()

    interval = max(10, args.interval)

    def sleep_s() -> int:
        # low-frequency with jitter; when no changes, backoff up to interval
        return max(10, int(interval * (0.6 + random.random() * 0.6)))

    while True:
        sr = scan_once(args.tasks_dir, grace=args.grace)
        print(
            f"[{now_iso()}] scan: changed_files={sr.changed_files} overdue={sr.overdue_tasks} "
            f"reset_to_pending={sr.reset_to_pending} blocked_projects={sr.blocked_projects}")
        if args.once:
            break
        time.sleep(sleep_s())


if __name__ == "__main__":
    main()
