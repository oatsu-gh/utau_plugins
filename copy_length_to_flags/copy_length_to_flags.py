#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""UTAUのノート長をフラグにコピーする。調声晒しで長さがわかりやすそう。

## 仕様
以下の機能を自動で切り替えます。

- 全ノートのフラグにノート長が記入されている場合は、フラグからノート長を削除する。
  - `Length=480` & `Flags=g-2H40` → `Flags=【480】g-2H40`
- フラグにノート長が記入されていないノートが一つでもある場合は、ノート長を記入する。
  - `Flags=【480】g-2H40` → `Flags=g-2H40`
"""
import re
from sys import argv

import utaupy as up


def copy_length_to_flags(plugin: up.utauplugin.UtauPlugin):
    """ノート長をフラグに追記する

    Length=480(4分音符)で元のフラグが'g-2H40'のとき、
    '【480】g-2H40' みたいな表記になるようにする。
    """
    for note in plugin.notes:
        note.flags = f'【{str(note.length)}】{str(note.flags)}'


def delete_length_to_flags(plugin: up.utauplugin.UtauPlugin, pattern: re.Pattern):
    """フラグ内のLengthを消す

    '【480】g-2H40' -> 'g-2H40'
    'g-2【480】H40' -> 'g-2H40'
    """
    for note in plugin.notes:
        note.flags = pattern.sub('', note.flags)


def main(plugin):
    """自動で動作を切り替える。

    - 全ノート(休符を除く)のフラグにノート長が記入されている場合は、フラグからノート長を削除する。
    - フラグにノート長が記入されていないノート(休符を除く)が一つでもある場合は、ノート長を記入する。
    """
    pattern = re.compile('【.*?】')
    notes = plugin.notes
    if all([note.lyric == 'R' or pattern.search(note.flags) for note in notes]):
        delete_length_to_flags(plugin, pattern)
    else:
        delete_length_to_flags(plugin, pattern)
        copy_length_to_flags(plugin)


if __name__ == '__main__':
    # `python copy_length_to_flags.py hogehoge.tmp --mode copy`
    up.utauplugin.run(main)
