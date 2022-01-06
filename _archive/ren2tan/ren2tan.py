#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
連続音歌詞を空白で区切って単独音にするUTAUプラグイン
"""


import utaupy


def ren2tan(plugin):
    """
    歌詞を空白で区切って、空白より後ろ側だけ残す。
    """
    for note in plugin.notes:
        note.lyric = note.lyric.split()[-1]


if __name__ == '__main__':
    utaupy.utauplugin.run(ren2tan)
