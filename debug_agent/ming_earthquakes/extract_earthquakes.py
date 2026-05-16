#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "corpus"
OUT = ROOT / "debug_agent" / "ming_earthquakes"

EVENT_TERMS = re.compile(r"地(?:大)?震|震(?:动|响|声|裂|陷|塌)?")
LOSS_TERMS = re.compile(
    r"压死|死者|死伤|伤人|陷|裂|坏|圮|倾|倒|塌|崩|摧|民舍|庐舍|城|垣|墙|"
    r"宫|殿|庙|陵|塔|屋|仓|桥|赈|振|免|蠲|灾|饥|修省|自责"
)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u3000", " ")).strip()


def snippets_for_line(line: str, line_no: int, source: str) -> list[dict[str, str]]:
    text = clean(line)
    rows = []
    for match in EVENT_TERMS.finditer(text):
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 140)
        snippet = text[start:end]
        rows.append(
            {
                "source": source,
                "line": str(line_no),
                "term": match.group(0),
                "loss_flag": "yes" if LOSS_TERMS.search(snippet) else "no",
                "snippet": snippet,
            }
        )
    return rows


def main() -> None:
    rows: list[dict[str, str]] = []
    for path in sorted(CORPUS.glob("*.txt")):
        if path.name == "README.md":
            continue
        with path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                if EVENT_TERMS.search(line):
                    rows.extend(snippets_for_line(line, line_no, path.name))

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "earthquake_snippets.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "line", "term", "loss_flag", "snippet"])
        writer.writeheader()
        writer.writerows(rows)

    with (OUT / "earthquake_loss_snippets.md").open("w", encoding="utf-8") as handle:
        handle.write("# Ming Earthquake Loss Snippets\n\n")
        for row in rows:
            if row["loss_flag"] == "yes":
                handle.write(
                    f"- `{row['source']}:{row['line']}` `{row['term']}`: {row['snippet']}\n"
                )

    print(f"snippets: {len(rows)}")
    print(f"loss flagged: {sum(1 for row in rows if row['loss_flag'] == 'yes')}")


if __name__ == "__main__":
    main()
