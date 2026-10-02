# -*- coding: utf-8 -*-
"""卡表数据完整性校验：自动同步提交前的最后闸门。

校验项：
1. 卡表文件总数不低于历史合理值（大面积拉取失败/空数据直接拒绝）
2. 每弹文件卡数与索引 count 一致（偏差超过一半视为异常）
3. 清单内各弹 md5 与 manifest.json 一致（防部分文件漏提交/手工改动）

用法：python tools/verify_data.py    # 通过退出码 0，失败退出码 1
"""
import hashlib
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
MIN_TOTAL = 10000  # 当前全量约 12600 张；低于此值视为大面积失败


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _git_head_counts() -> dict:
    """上一次提交时各弹的卡数（无 git / 无历史时返回空表跳过对比）。"""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "show", "HEAD:data/sets_index.json"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode != 0:
            return {}
        idx = json.loads(out.stdout)
        return {e["id"]: int(e.get("count") or 0) for e in idx}
    except Exception:
        return {}


def main() -> int:
    idx_path = DATA / "sets_index.json"
    if not idx_path.exists():
        print("校验失败：sets_index.json 不存在")
        return 1
    idx = json.loads(idx_path.read_text(encoding="utf-8"))

    problems = []
    total_files = 0
    total_index = 0
    head_counts = _git_head_counts()
    for e in idx:
        p = DATA / "cards" / f"{e['id']}.json"
        if not p.exists():
            problems.append(f"{e['id']}: 卡表文件缺失")
            continue
        cards = json.loads(p.read_text(encoding="utf-8"))
        total_files += len(cards)
        total_index += e.get("count", 0)
        if e.get("count") and len(cards) < e["count"] * 0.5:
            problems.append(f"{e['id']}: 索引 {e['count']} 张，文件仅 {len(cards)} 张")
        # 与上次提交对比：已有数据的弹骤减超过一半视为拉取残缺（索引自比是循环论证）
        old = head_counts.get(e["id"], 0)
        if old >= 20 and len(cards) < old * 0.5:
            problems.append(f"{e['id']}: 较上次提交 {old} 张骤减至 {len(cards)} 张")

    # manifest 逐弹 md5 比对（清单缺失时视为异常——本仓库以 manifest 为热更新基准）
    manifest_path = DATA / "manifest.json"
    if not manifest_path.exists():
        problems.append("manifest.json 不存在")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checked = 0
        for set_id, m in manifest.get("sets", {}).items():
            p = DATA / "cards" / f"{set_id}.json"
            if not p.exists():
                problems.append(f"{set_id}: manifest 有记录但卡表文件缺失")
                continue
            if _md5(p) != m.get("md5"):
                problems.append(f"{set_id}: 卡表 md5 与 manifest 不一致")
            checked += 1
        print(f"manifest md5 比对 {checked} 弹（schemaVersion {manifest.get('schemaVersion')}）")

    print(f"索引总数 {total_index} 张 / 文件总数 {total_files} 张（{len(idx)} 弹）"
          + (f"；对比基线：上次提交 {len(head_counts)} 弹" if head_counts else "；无 git 基线，跳过对比"))
    if total_files < MIN_TOTAL:
        problems.insert(0, f"卡表总数 {total_files} 低于阈值 {MIN_TOTAL}，疑似大面积拉取失败")

    if problems:
        print("校验失败：")
        for p in problems[:20]:
            print(" -", p)
        return 1
    print("校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
