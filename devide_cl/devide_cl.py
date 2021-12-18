#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
促音が含まれているノートを半分に割る。
「くっ」→「く」「っ」
"""
from copy import deepcopy
from typing import List

from utaupy.utauplugin import run
from utaupy.ust import Note


def split_cl_note(plugin):
    """
    ノートに促音が含まれていたら分割してノートを追加し、
    そうではなかったらそのまま複製する。
    """
    new_notes: List[Note] = []
    for note in plugin.notes:
        if 'っ' in note.lyric:
            # 半分にした時の長さが2.5とかになった時は2.6を経由して3にする
            new_note = deepcopy(note)
            new_note.lyric = new_note.lyric.replace('っ', '')
            new_note.length = round(new_note.length / 2 + 0.01)
            # 半分にした時の長さが2.5とかになった時は2.4を経由して2にする
            cl_note = deepcopy(note)
            cl_note.lyric = 'っ'
            cl_note.length = round(cl_note.length / 2 - 0.01)
            cl_note.tag = '[#INSERT]'
            # ノートを追加
            new_notes.append(new_note)
            new_notes.append(cl_note)
        else:
            new_notes.append(note)
    plugin.notes = new_notes


if __name__ == '__main__':
    print('_____ξ・ヮ・) < copy_note_index_to_label ________')
    print('Copyright (c) 2021 oatsu')
    print('Copyright (c) 2001-2021 Python Software Foundation\n')
    run(split_cl_note)
