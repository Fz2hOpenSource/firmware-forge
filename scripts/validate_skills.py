#!/usr/bin/env python3
"""技能仓库统一校验脚本。

用法（仓库根目录）：
    python -X utf8 scripts/validate_skills.py

检查项：
  1. 每个技能的 SKILL.md：frontmatter 存在、name 与目录一致、
     description 存在且 ≤1024 字符（UTF-8 计数）
  2. 正文中引用的 references/*.md 文件必须存在
  3. references/ 下每个文件必须在 SKILL.md 正文中有提及（防孤儿）
  4. 仓库内所有 .ps1 必须带 UTF-8 BOM（GBK 环境防解析灾难）

任一失败项以非零退出码结束。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESC_LIMIT = 1024

failures = []
warnings = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
    return cond


def skill_dirs():
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists() and not d.name.startswith("."):
            yield d


def main():
    # ---- 技能校验 ----
    for d in skill_dirs():
        skill_md = d / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        tag = d.name

        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not check(m is not None, f"[{tag}] 缺少 frontmatter"):
            continue
        fm = m.group(1)

        nm = re.search(r"^name:\s*(\S+)", fm, re.M)
        check(nm is not None and nm.group(1) == d.name,
              f"[{tag}] name 缺失或与目录名不一致")

        dm = re.search(r"description:\s*>?\s*\n((?:\s+.*\n?)*)", fm)
        desc = " ".join(dm.group(1).split()) if dm else ""
        check(bool(desc), f"[{tag}] description 缺失")
        check(len(desc) <= DESC_LIMIT,
              f"[{tag}] description {len(desc)} 字符，超过 {DESC_LIMIT} 上限"
              f"——请把示例与次要排除项移入正文")

        # 正文引用的 references 必须存在
        body = text[m.end():]
        raw_refs = set(re.findall(r"references/([\w\-./]+\.md)", body))
        refs = {re.sub(r"^(?:references/)+", "", r) for r in raw_refs}
        for r in sorted(refs):
            check((d / "references" / r).exists(),
                  f"[{tag}] 正文引用了不存在的 references/{r}")

        # references 下未在正文提及的文件（孤儿警告）
        ref_dir = d / "references"
        if ref_dir.exists():
            for f in sorted(ref_dir.rglob("*.md")):
                rel = f.relative_to(d).as_posix()
                if not (rel in body or f.name in body):
                    warnings.append(f"[{tag}] references/{rel} 未在 SKILL.md 中提及（孤儿文件？）")

    # ---- .ps1 BOM 守卫 ----
    for p in sorted(ROOT.rglob("*.ps1")):
        if "__pycache__" in str(p):
            continue
        b = p.read_bytes()
        if not (len(b) >= 3 and b[0] == 0xEF and b[1] == 0xBB and b[2] == 0xBF):
            failures.append(f"[ps1] {p.relative_to(ROOT)} 缺少 UTF-8 BOM"
                            "（GBK 环境下会解析失败）")

    # ---- 报告 ----
    print(f"校验完成：{len(failures)} 个失败，{len(warnings)} 个警告")
    for w in warnings:
        print(f"  警告: {w}")
    for f in failures:
        print(f"  失败: {f}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
