#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
歌詞にRを含むノートの子音速度を100にするUTAUプラグイン
休符 'R' は処理しない。
"""

import utaupy as up


def main(plugin):
    """
    ノートの歌詞に R が含まれていたらVelocity=100
    """
    notes = plugin.notes
    for note in notes:
        if ('R' in note.lyric):
            note.velocity = 100
            print('子音速度を100にしました:', note.lyric)


if __name__ == '__main__':
    print('_____ξ・ヮ・) < set_R_vel100 v1.0.1 ________')
    up.utauplugin.run(main)
