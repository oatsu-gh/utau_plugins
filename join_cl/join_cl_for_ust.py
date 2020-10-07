#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
「っ」を前のノートに結合する。
"""
from os.path import splitext

import utaupy as up
from tqdm import tqdm


def join_cl(ust):
    """
    歌詞が「っ」だった場合、次の処理を行う。
    1. そのノートを [#DELETE] にする
    2. そのノート長を 直前のノート長に加算する
    3. 直前のノートの歌詞に「っ」を追加する
    """
    notes = ust.notes
    for i, note in enumerate(tqdm(notes)):
        if note.lyric == 'っ':
            print(note)
            # 「っ」のノートを削除 ([#DELETE] にする)
            note.delete()
            # 直前のノート
            previous_note = notes[i - 1]
            # 直前のノート長を伸ばす
            previous_note.length += note.length
            # 直前のノートの歌詞に「っ」を追加する
            previous_note.lyric += 'っ'
    return ust


def main():
    """
    処理対象ファイルを指定し、ファイル入出力を行う。
    """
    path_ust = input('path_ust: ')
    ust = up.ust.load(path_ust)
    ust = join_cl(ust)
    path_ust_out = splitext(path_ust)[0] + '_joincl.ust'
    ust.write(path_ust_out)

if __name__ == '__main__':
    main()
