#!/usr/bin/env python3
"""Check inconsistent spellings."""
import itertools
import re
from pathlib import Path

import colorama
from colorama import Fore
from colorama import Style

colorama.init()

bad_patterns = (
    "コンピュータ(?!ー)",
    "フォルダ(?!ー)",
    "メモリー",
    "ユーザ(?!ー)",
)


def process_file(path: Path) -> None:
    """Process the specified file."""
    tmp_sep = "__TMP_SEP__"

    def replace(m: re.Match) -> str:
        result = tmp_sep
        for c in m.group(0):
            result += c + tmp_sep
        return Style.BRIGHT + Fore.RED + result + Style.RESET_ALL

    fmt1 = Fore.MAGENTA
    fmt2 = Fore.GREEN
    fmt3 = Style.RESET_ALL

    lines = path.read_text().splitlines()
    for line_no, line_str in enumerate(lines):
        line_str = line_str.rstrip()
        found = False
        for pattern in bad_patterns:
            new_line_str = re.sub(pattern, replace, line_str)
            if new_line_str != line_str:
                found = True
                line_str = new_line_str
        if found:
            line_str = line_str.replace(tmp_sep, "")
            print(f"{fmt1}{path}{fmt2}:{line_no + 1}:{fmt3}    {line_str}")


def main() -> None:
    """Entry point."""
    for path in itertools.chain(
        Path("notebooks").glob("*.ipynb"),
        Path("notebooks").glob("*.md"),
        Path("docs").glob("*.md"),
    ):
        process_file(path)


if __name__ == "__main__":
    main()
