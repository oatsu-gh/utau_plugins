#!/usr/bin/env python3
# Copyright (c) 2023 oatsu
"""
音程をもとにノートの歌詞を設定する。
"""
from utaupy.utauplugin import run

MOD12NOTENUM_TO_LYRIC = (
    'ど', 'れ', 'れ', 'み', 'み', 'ふぁ', 'そ', 'そ', 'ら', 'ら', 'し', 'し'
)


def main(plugin):
    """音高をもとに歌詞を決める。
    """
    for note in plugin.notes:
        if 'R' not in note.lyric:
            note.lyric = MOD12NOTENUM_TO_LYRIC[note.notenum % 12]


if __name__ == "__main__":
    run(main)
