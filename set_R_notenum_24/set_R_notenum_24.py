#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
調声晒し用に休符の音程を低くする
"""
import utaupy


def set_rest_notenum_24(plugin):
    """
    休符の音程をUTAUで最低の24にする。
    """
    for note in plugin.notes:
        if note.lyric == 'R':
            note.notenum = 24


if __name__ == '__main__':
    utaupy.utauplugin.run(set_rest_notenum_24)
