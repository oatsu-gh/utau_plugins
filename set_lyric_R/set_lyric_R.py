#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""
選択範囲を休符にするプラグイン
"""
from utaupy.utauplugin import run


def set_lyric_R(plugin):
    """
    選択範囲の歌詞を休符にしてすっぴん化する。
    """
    for note in plugin.notes:
        note.lyric = 'R'
        note.suppin()


if __name__ == '__main__':
    run(set_lyric_R)
