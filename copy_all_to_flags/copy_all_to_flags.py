#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""ノートの全情報をフラグで見れるようにする
"""
import utaupy as up
from copy import copy

def copy_all_to_flags(plugin: up.utauplugin.UtauPlugin):
    """ノートの全情報をフラグにする
    """
    for note in plugin.notes:
        note_data = copy(note.data)
        del note_data['Tag']
        note.flags = str(note_data)[1:-1]
        print(note.flags)

if __name__ == '__main__':
    up.utauplugin.run(copy_all_to_flags)
