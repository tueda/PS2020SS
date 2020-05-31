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
    # 句読点
    "，",
    "．",
    # 漢字とひらがなの表記ゆれ
    # See also:
    #   http://www.gp.tohoku.ac.jp/pol/pol/hanawa/open-siryo/report_manual.pdf
    #   http://www.yamanouchi-yri.com/yrihp/techwrt-2-4s/t-2-4s01f.htm
    "(?<!の)並びに",
    "(この|する)時(?!点)",
    "(その|以下の)通り",
    "[1-3]つ",
    "いっぽう",
    "おもな",
    "おもに",
    "およぼ([さしすせそ])?",
    "くわえて",
    "その他",  # そのほか
    "たがいに",
    "たとえば",
    "とくに",
    "の様([なに])?",
    "ひとつ",
    "ふたつ",
    "よぶ",
    "一層",
    "且つ",
    "但し",
    "全く",
    "全て",
    "共に",
    "即ち",
    "又は",
    "及び",
    "従って",
    "故に",
    "既に",
    "易い",
    "易しい",
    "更に",
    "最も",
    "極めて",
    "様々",
    "殆ど",
    "無い",
    "良い",
    "良く",
    "若しくは",
    "難い",
    # 外来語の表記ゆれ
    # See also: https://www.microsoft.com/ja-jp/language/search
    "コンピュータ(?!ー)",
    "パラメータ(?!ー)",
    "フォルダ(?!ー)",
    "メモリー",
    "ユーザ(?!ー)",
    # 誤字
    "シュミレーション",
    "再起呼(び出し)?",
    "再起的",
    "再起関数",
    # 言葉遣いの表記ゆれ
    "演習問題",
    "練習課題",
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
