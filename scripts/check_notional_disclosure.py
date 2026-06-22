from __future__ import annotations

import re
import sys
from pathlib import Path


NUMBER = re.compile(r"(?<![A-Za-z0-9_./-])\d+(?:\.\d+)?%?")


def main(argv: list[str] | None = None) -> int:
    paths = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        paths = [Path("paper")]

    failures: list[str] = []
    for path in _iter_files(paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in NUMBER.finditer(text):
            if _inside_citation(text, match.start(), match.end()):
                continue
            window = text[max(0, match.start() - 80) : min(len(text), match.end() + 80)].lower()
            if "(notional)" not in window and "\\cite" not in window:
                failures.append(f"{path}: numeric claim lacks notional marker near `{match.group(0)}`")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("notional disclosure OK")
    return 0


def _inside_citation(text: str, start: int, end: int) -> bool:
    left_bracket = text.rfind("[", 0, start)
    right_bracket = text.find("]", end)
    left_newline = text.rfind("\n", 0, start)
    return left_bracket > left_newline and right_bracket != -1 and right_bracket - left_bracket < 80


def _iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".tex", ".txt"}
            )
        elif path.is_file():
            files.append(path)
    return files


if __name__ == "__main__":
    raise SystemExit(main())
