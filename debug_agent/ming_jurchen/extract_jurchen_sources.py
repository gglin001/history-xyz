#!/usr/bin/env python3
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
OUT_DIR = ROOT / "debug_agent" / "ming_jurchen"


TERMS = [
    "女真",
    "女直",
    "野人",
    "建州",
    "建州卫",
    "建州左卫",
    "建州右卫",
    "海西",
    "奴儿干",
    "奴儿干都司",
    "兀者",
    "忽剌温",
    "毛怜",
    "董山",
    "李满住",
    "王杲",
    "王台",
    "叶赫",
    "哈达",
    "辉发",
    "乌拉",
    "速把亥",
    "努尔哈赤",
    "奴儿哈赤",
    "奴酋",
    "奴贼",
    "后金",
    "清河",
    "抚顺",
    "开原",
    "铁岭",
    "萨尔浒",
    "沈阳",
    "辽阳",
    "广宁",
    "熊廷弼",
    "杨镐",
    "袁应泰",
    "王化贞",
    "毛文龙",
    "袁崇焕",
    "宁远",
]


PHASES = {
    "early_system": [
        "明实录太祖实录.txt",
        "明实录太宗实录.txt",
        "明实录仁宗实录.txt",
        "明实录宣宗实录.txt",
    ],
    "mid_system": [
        "明实录英宗实录.txt",
        "明实录宪宗实录.txt",
        "明实录孝宗实录.txt",
        "明实录武宗实录.txt",
        "明实录世宗实录.txt",
        "明实录穆宗实录.txt",
    ],
    "late_war": [
        "明实录神宗实录.txt",
        "明实录光宗实录.txt",
        "明实录熹宗实录.txt",
        "明实录崇祯实录.txt",
    ],
}


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def snippets(text: str, term: str, radius: int = 90):
    for match in re.finditer(re.escape(term), text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        yield compact(text[start:end])


def main():
    term_pattern = re.compile("|".join(re.escape(t) for t in sorted(TERMS, key=len, reverse=True)))
    rows = []
    counts = {}
    selected = {}

    for path in sorted(CORPUS.glob("明实录*.txt")):
        rel = path.relative_to(ROOT).as_posix()
        counts[rel] = {term: 0 for term in TERMS}
        with path.open(encoding="utf-8", errors="ignore") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.rstrip("\n")
                matches = list(term_pattern.finditer(line))
                if not matches:
                    continue
                found = sorted({m.group(0) for m in matches}, key=lambda x: TERMS.index(x) if x in TERMS else 999)
                for term in found:
                    counts[rel][term] += line.count(term)
                    selected.setdefault(term, [])
                    if len(selected[term]) < 60:
                        for snippet in snippets(line, term):
                            selected[term].append(
                                {
                                    "file": rel,
                                    "line": lineno,
                                    "term": term,
                                    "snippet": snippet,
                                }
                            )
                            break
                rows.append(
                    {
                        "file": rel,
                        "line": lineno,
                        "terms": found,
                        "snippet": compact(line[:700]),
                    }
                )

    with (OUT_DIR / "jurchen_hits.jsonl").open("w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (OUT_DIR / "jurchen_term_counts.tsv").open("w", encoding="utf-8") as out:
        out.write("file\tterm\tcount\n")
        for file, term_counts in counts.items():
            for term, count in term_counts.items():
                if count:
                    out.write(f"{file}\t{term}\t{count}\n")

    with (OUT_DIR / "jurchen_selected_snippets.md").open("w", encoding="utf-8") as out:
        out.write("# 明实录女真与辽东摘录\n\n")
        for term in TERMS:
            items = selected.get(term, [])
            if not items:
                continue
            out.write(f"## {term}\n\n")
            for item in items[:25]:
                out.write(f"- `{item['file']}:{item['line']}`: {item['snippet']}\n")
            out.write("\n")

    phase_summary = {}
    for phase, filenames in PHASES.items():
        total = {term: 0 for term in TERMS}
        for filename in filenames:
            rel = f"corpus/{filename}"
            for term, count in counts.get(rel, {}).items():
                total[term] += count
        phase_summary[phase] = {term: count for term, count in total.items() if count}

    with (OUT_DIR / "jurchen_phase_counts.json").open("w", encoding="utf-8") as out:
        json.dump(phase_summary, out, ensure_ascii=False, indent=2)

    print(f"hits={len(rows)}")
    print(f"wrote {OUT_DIR / 'jurchen_hits.jsonl'}")
    print(f"wrote {OUT_DIR / 'jurchen_selected_snippets.md'}")


if __name__ == "__main__":
    main()
