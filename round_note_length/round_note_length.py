#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
ノート長を10で丸める
"""

from utaupy.utauplugin import run

UNIT_LENGTH = 10


def round_note_length(plugin, unit):
    """
    ノート長を10で割って丸めて10をかける
    """
    for note in plugin.notes:
        note.length = round(note.length / unit) * unit


if __name__ == '__main__':
    run(round_note_length, option=UNIT_LENGTH)
