#!/usr/bin/env python3
# Copyright (c) 2024 oatsu
"""
「っ」「R」の順でノートが並んでいるとき、「っ」を延長して「R」を消す
"""

from utaupy.ust import Note
from utaupy.utauplugin import UtauPlugin, run


def merge_cl_and_R(plugin: UtauPlugin):
    """clとRを結合してclにする
    """

    cl_flag = False
    cl_note: None | Note = None
    # 各ノートに対して処理を始める
    for note in plugin.notes:
        if note.lyric not in ('っ', 'R'):
            cl_flag = False
        # cl が出現したらフラグをオンにして、長さを伸ばすためのノートとして記憶する
        elif note.lyric == 'っ':
            cl_flag = True
            cl_note = note
            # print(cl_note.lyric)
            # print(cl_note.length)
        elif cl_flag is True and note.lyric == 'R':
            cl_note.length += note.length
            # print(cl_note.length)
            note.delete()  # [#DELETE]


if __name__ == "__main__":
    run(merge_cl_and_R)
