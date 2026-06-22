from __future__ import annotations

import re
import sys
from pathlib import Path


BANNED_TERMS = {
    "best-in-class",
    "breakthrough",
    "disruptive",
    "game-changing",
    "revolutionary",
    "transformative",
    "world-class",
}

ANTITHETICAL_REVERSAL = re.compile(r"\bnot\b[^.\n]{0,80}\bbut\b", re.IGNORECASE)


def main(argv: list[str] | None = None) -> int:
    paths = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not paths:
        paths = [Path("paper"), Path("mechanism"), Path("README.md")]

    failures: list[str] = []
    for path in _iter_files(paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        for term in sorted(BANNED_TERMS):
            if term in lower:
                failures.append(f"{path}: banned marketing term: {term}")
        if ANTITHETICAL_REVERSAL.search(text):
            failures.append(f"{path}: antithetical-reversal phrasing")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("voice_lint OK")
    return 0


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
