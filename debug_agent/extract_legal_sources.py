#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
OUT = ROOT / "debug_agent" / "legal_hits.jsonl"

KEYWORDS = [
    "大明律",
    "大诰",
    "问刑条例",
    "律例",
    "刑法志",
    "刑部",
    "都察院",
    "大理寺",
    "三法司",
    "法司",
    "锦衣卫",
    "诏狱",
    "东厂",
    "西厂",
    "镇抚司",
    "录囚",
    "审录",
    "朝审",
    "大审",
    "热审",
    "恤刑",
    "慎刑",
    "五覆奏",
    "覆奏",
    "充军",
    "枷号",
    "廷杖",
    "凌迟",
    "连坐",
    "赎罪",
    "赃罚",
    "奸党",
    "谋反",
    "谋逆",
    "条例",
    "刑名",
]

HEADING_RE = re.compile(
    r"^(?P<h>(本纪|志|表|列传|皇帝实录卷|大明.*实录卷|明实录闽海关系史料).{0,30}|[一二三四五六七八九十百]+、\s*.{0,30})$"
)
DATE_RE = re.compile(
    r"(?P<date>(洪武|建文|永乐|洪熙|宣德|正统|景泰|天顺|成化|弘治|正德|嘉靖|隆庆|万历|泰昌|天启|崇祯)[一二三四五六七八九十百元\d]+年[^。○\n]{0,20})"
)


def compact(text: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def main() -> None:
    rows = []
    for path in sorted(CORPUS.glob("*.txt")):
        current_heading = ""
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for lineno, raw in enumerate(f, 1):
                line = raw.strip()
                if not line:
                    continue
                m = HEADING_RE.match(line)
                if m:
                    current_heading = m.group("h")
                hit_words = [kw for kw in KEYWORDS if kw in line]
                if not hit_words:
                    continue
                dm = DATE_RE.search(line)
                rows.append(
                    {
                        "file": path.name,
                        "line": lineno,
                        "heading": current_heading,
                        "date": dm.group("date") if dm else "",
                        "keywords": hit_words,
                        "text": compact(line),
                    }
                )
    with OUT.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} hits to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
