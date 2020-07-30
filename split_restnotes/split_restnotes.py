#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
'x R' の語尾ブレスを使うために、
音符のあとの休符を分割して、同じ音程にする。
    1. 現在のノートが休符であるか判定する
    2. 直前のノートの歌詞がRを含むか調べる
    3. 現在のノートを直前と同じ音程にする
    4. 現在のノートを分割する
        全休符→4分と残りに分割
        2分休符→4分x2に分割
        4分休符→8分x2に分割
        8分休符→16x2に分割
        16分休符→32x2に分割
        32分休符以下→半分にする
    5. 音符→休符の流れをまた探す
"""

import sys
from pprint import pprint

import utaupy as up


def split_restnotes(plugin):
    """
    ノートを分割する。
    """
    notes = plugin.notes
    for i, note in enumerate(notes[1:]):
        n1 = notes[i-1]
        n2 = notes[i]
        if ('R' not in n1.lyric) and (n2.lyric == 'R'):
            n2.notenum = n1.notenum
            new_note = plugin.insert_note(i+1)
            new_note.lyric = 'R'
            tmp = n2.length
            if tmp > 960:
                n2.length = 480
                new_note.length = tmp - 480
            else:
                n2.length = tmp // 2
                new_note.length = tmp - (tmp // 2)
        print(note)
    print('---')

def main():
    path = input('path: ').strip(r'"')
    plugin = up.utauplugin.load(path)
    print(plugin.prev)
    print(plugin.next)
    for note in plugin.values:
        print(note)
    print('-----------------------')
    split_restnotes(plugin)
    for note in plugin.values:
        print(note)
    plugin.write(path + '_out.txt')

    input('Press Enter to exit')

if __name__ == '__main__':
    main()
