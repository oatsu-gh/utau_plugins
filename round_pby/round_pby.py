#!/usr/bin/env python3
# Copyright (c) 2024 oatsu
"""
ピッチ点の高さを丸める。全て半音レベルにする。EnuPitchを使った後に使用する想定。
"""
from utaupy.utauplugin import run


def round_pitches(plugin):
    """音高を丸める
    """
    for note in plugin.notes:
        note.pbs = [note.pbs[0], round(note.pbs[1] / 10) * 10]
        note.pby = [round(x/10) * 10 for x in note.pby]


if __name__ == "__main__":
    run(round_pitches)
