#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
歌詞を括弧でくくってファイル出力するプラグイン
"""

import sys
from os.path import dirname, join

from utaupy.utauplugin import run


def main(plugin):
    """
    選択範囲または全体から歌詞を取得する。
    歌詞をファイルにまとめて出力する。
    """
    try:
        path_ust = plugin.setting['Project']
    except KeyError:
        print('USTファイルを保存してから実行してください。')
        input('エンターキーを押すと終了します。')
        sys.exit(1)
    lyrics = [note.lyric for note in plugin.notes]
    str_lyrics = '[' + ']['.join(lyrics) + ']'
    str_lyrics = str_lyrics.replace('[R]', '\n')

    path_result = join(dirname(path_ust), '歌詞を括弧でくくって出力するやつの結果.txt')
    with open(path_result, 'w') as f:
        f.write(str_lyrics)


if __name__ == '__main__':
    run(main)
