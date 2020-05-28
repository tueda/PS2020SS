#!/usr/bin/env python3
"""A simple viewer."""
import curses
import re
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import nbformat

StringList = List[str]


def load_answers(path: Path) -> Optional[List[List[List[str]]]]:
    """Return answers in the given directory."""
    files = [p for p in path.glob("*") if p.is_file()]
    files.sort(key=lambda p: p.name)
    seen: Set[Path] = set()
    answers: Dict[str, List[StringList]] = {}

    for p in files:
        m = re.match(r"^(us\d{6})\.txt$", p.name)
        if m:
            user = m.group(1)
            assert user not in answers
            assert p not in seen
            seen.add(p)
            answers[user] = parse_txt(p)

    for p in files:
        m = re.match(r"^(us\d{6})_.*$", p.name)
        if m:
            user = m.group(1)
            suffix = p.suffix.lower()
            if suffix in (".ipynb", ".json"):
                assert user in answers
                assert p not in seen
                seen.add(p)
                answers[user] += parse_ipynb(p)

    if not answers:
        return None

    for p in files:
        if p not in seen:
            raise RuntimeError(f"unexpected file: {p.name}")

    for i, user in enumerate(sorted(answers.keys())):
        blocks = answers[user]
        header1 = blocks[0][0] + f" [{i + 1} / {len(answers)}]"
        header2 = blocks[0][1]
        for j, b in enumerate(blocks):
            if j == 0:
                b[0] = header1
            else:
                b.insert(0, header1)
                b.insert(1, header2)
            b[1] += f" [{j + 1} / {len(blocks)}]"
            if len(b) >= 3 and b[2].strip():
                b.insert(2, "")

    return [answers[user] for user in sorted(answers.keys())]


def parse_txt(path: Path) -> List[StringList]:
    """Parse a text file."""
    text = path.read_text()
    lines = text.splitlines(keepends=False)

    assert len(lines) >= 4

    if lines[0].startswith("\ufeff"):  # Check BOM
        lines[0] = lines[0][1:]

    assert lines[0].startswith("#")
    assert lines[1].startswith("#")
    assert not lines[2].startswith("#")
    assert lines[3].startswith("#")

    header = lines[0][1:]
    info = lines[2].split(",")

    first_block = [f"# {header}", f"# {info[0]} {info[1]}"]
    blocks = [first_block]

    for b in split_blocks(lines[3:]):
        if b[0] in ("#回答内容", "#コメント", "#提出ファイル"):
            first_block.append("")
            first_block.extend(b)
        else:
            blocks.append(b)

    return blocks


def parse_ipynb(path: Path) -> List[StringList]:
    """Parse a Jupyter notebook file."""
    blocks = []
    for cell in nbformat.read(path, nbformat.NO_CONVERT).cells:
        if cell["cell_type"] == "code" and re.search(
            r"#\s*課題解答\d+\.\d+", cell["source"]
        ):
            blocks.append(cell["source"].splitlines(keepends=False))
    return blocks


def is_block_beginning(line: str) -> bool:
    """Return True for a beginning of a block."""
    if line in ("#回答内容", "#コメント", "#提出ファイル"):
        return True
    if re.match(r"#\s*課題解答\d+\.\d+", line):
        return True
    return False


def split_blocks(lines: StringList) -> List[StringList]:
    """Split lines into blocks."""
    blocks: List[StringList] = []

    current_block: StringList = []

    for line in lines:
        if is_block_beginning(line):
            blocks.append(current_block)
            current_block = []
        current_block.append(line)

    blocks.append(current_block)

    return [b for b in blocks if not is_empty_block(b)]


def is_empty_block(lines: StringList) -> bool:
    """Return True for an empty block of lines."""
    first = True
    for line in lines:
        if first:
            first = False
            if line.startswith("#"):
                continue
        if line.strip():
            return False
    return True


def main(stdscr: "curses._CursesWindow") -> None:
    """Entry point."""
    current_path = Path.cwd()
    dir_list: List[str] = []
    selected_dir = 0
    answers: Optional[List[List[List[str]]]] = None
    selected_answer: Optional[Tuple[int, int]] = None

    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    A_SELECTED = curses.A_REVERSE  # noqa: N806
    A_DIRECTORY1 = curses.color_pair(1)  # noqa: N806
    A_DIRECTORY2 = curses.color_pair(2)  # noqa: N806
    A_EMPHASIZED = A_DIRECTORY2  # noqa: N806

    def change_dir(dirname: str) -> None:
        nonlocal current_path
        nonlocal dir_list
        nonlocal selected_dir
        nonlocal answers
        nonlocal selected_answer

        old_dirname = ".."
        if dirname == "..":
            old_dirname = current_path.name

        new_path = current_path / dirname
        if not new_path.is_dir():
            raise ValueError(f"illegal dirname={dirname}")
        current_path = new_path.resolve()

        dir_list = [str(p.name) for p in current_path.glob("*") if p.is_dir()]
        dir_list = [d for d in dir_list if not d.startswith(".")]
        dir_list = [".."] + sorted(dir_list)

        selected_dir = dir_list.index(old_dirname)
        if selected_dir < 0:
            selected_dir = 0

        answers = load_answers(current_path)
        if answers is None:
            selected_answer = None
        else:
            selected_answer = (0, 0)

    change_dir(".")

    while True:
        max_rows, max_cols = stdscr.getmaxyx()

        def draw_str(y: int, x: int, text: str, attr: int = curses.A_NORMAL) -> None:
            if y < max_rows:
                stdscr.addnstr(y, x, text, max_cols - x, attr)

        def draw_dirtree_screen() -> None:
            draw_str(0, 2, str(current_path), A_DIRECTORY1)

            for i, d in enumerate(dir_list):
                if i == selected_dir:
                    draw_str(i + 1, 0, ">")
                    draw_str(i + 1, 2, d, A_SELECTED)
                else:
                    draw_str(i + 1, 2, d)

        def draw_answer_screen() -> None:
            draw_str(0, 0, "#")
            draw_str(0, 2, str(current_path), A_DIRECTORY2)

            assert answers
            assert selected_answer

            i, j = selected_answer
            lines = answers[i][j]

            for i, s in enumerate(lines):
                if is_block_beginning(s):
                    draw_str(i + 1, 0, s, A_EMPHASIZED)
                else:
                    draw_str(i + 1, 0, s)

        def input_dirtree_screen(key: str) -> bool:
            nonlocal selected_dir

            if key == "Q":
                return True
            elif key == "KEY_UP":
                if selected_dir > 0:
                    selected_dir -= 1
            elif key == "KEY_DOWN":
                if selected_dir < len(dir_list) - 1:
                    selected_dir += 1
            elif key == "\n" or key == " ":
                change_dir(dir_list[selected_dir])
            return False

        def input_answer_screen(key: str) -> bool:
            nonlocal selected_answer

            assert answers
            assert selected_answer

            i, j = selected_answer

            if key == "Q":
                change_dir("..")
            elif key == "KEY_UP":
                if i > 0:
                    selected_answer = (i - 1, 0)
            elif key == "KEY_DOWN":
                if i < len(answers) - 1:
                    selected_answer = (i + 1, 0)
            elif key == "KEY_LEFT":
                if j > 0:
                    selected_answer = (i, j - 1)
                elif j == 0 and i > 0:
                    selected_answer = (i - 1, len(answers[i - 1]) - 1)
            elif key == "KEY_RIGHT":
                if j < len(answers[i]) - 1:
                    selected_answer = (i, j + 1)
                elif j == len(answers[i]) - 1 and i < len(answers) - 1:
                    selected_answer = (i + 1, 0)
            return False

        stdscr.clear()
        if answers:
            draw_answer_screen()
        else:
            draw_dirtree_screen()

        stdscr.refresh()

        key = stdscr.getkey().upper()
        if answers:
            quited = input_answer_screen(key)
        else:
            quited = input_dirtree_screen(key)
        if quited:
            break


if __name__ == "__main__":
    curses.wrapper(main)
