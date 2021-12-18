#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""
UTAUのノート番号をラベルにコピーする。ENUNUの音素チェックとかで便利そう。
"""
import re

import utaupy as up


def copy_tag_to_label(plugin: up.utauplugin.UtauPlugin):
    """
    ノート番号をラベルに追記する
    """
    for note in plugin.notes:
        note_index = str(note.tag).strip('#[]')
        note.label = f'【{note_index}】{str(note.label)}'


def delete_tag_from_label(plugin: up.utauplugin.UtauPlugin, pattern: re.Pattern):
    """
    ラベル内のノート番号を消す
    """
    for note in plugin.notes:
        note.label = pattern.sub('', note.label)


def main(plugin):
    """自動で動作を切り替える。

    - 全ノート(休符を除く)のラベルにノート番号が記入されている場合は、ラベルからノート番号を削除する。
    - ラベルにノート番号が記入されていないノート(休符を除く)が一つでもある場合は、ノート番号を記入する。
    """
    pattern = re.compile('【.*?】')
    notes = plugin.notes
    if all((note.lyric == 'R' or pattern.search(note.label)) for note in notes):
        delete_tag_from_label(plugin, pattern)
    else:
        delete_tag_from_label(plugin, pattern)
        copy_tag_to_label(plugin)
    for note in notes:
        note.refresh()


if __name__ == '__main__':
    print('_____ξ・ヮ・) < copy_note_index_to_label ________')
    print('Copyright (c) 2021 oatsu')
    print('Copyright (c) 2001-2021 Python Software Foundation\n')
    up.utauplugin.run(main)
