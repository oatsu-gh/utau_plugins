#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
選択範囲の最初のノートを巻き舌っぽくするUTAUプラグイン

## 目的

- 「ら」を「rrrrrあ」 って歌ってほしい
- 「ら aら aら aら」にする。

## 設計

- 選択した範囲の最初のノートを処理する
- 32部音符をいくつか重ねる(個数は実行時に指定)
- そのときの歌詞は選択したやつと同じのを重ねる
- とりあえず単独音で作る(連続音化はほかのプラグインで)
- 子音速度を200にする

"""
from copy import deepcopy
# from pprint import pprint

from utaupy import utauplugin


def main(plugin: utauplugin.UtauPlugin, num: int):
    """
    先頭ノートを分割する。
    32分音符をいくつか重ねる。

    num: 短いノートをいくつ増やすか
    """
    # らららららー の「らららら」の部分用のノート
    short_note = deepcopy(plugin.notes[0])
    short_note.length = 60
    short_note.tag = '[#INSERT]'
    short_note.velocity = 200
    # らららららー の「らー」の部分用のノート
    long_note = plugin.notes[0]
    long_note.length -= 60 * num
    long_note.velocity = 200
    # 編集前後のノートをまとめる
    plugin.notes = [short_note] * num + [long_note] + plugin.notes[1:]
    # pprint(plugin.notes)  # デバッグ用出力


if __name__ == '__main__':
    print('_____ξ・ヮ・) < makijita_maker v0.0.2 ________')
    print('Copyright (c) 2020 oatsu')
    print('Copyright (c) 2020 oatsu')
    print('Copyright (c) 2001-2020 Python Software Foundation\n')
    # 追加ノート数を指定
    print('短いノートをいくつ追加しますか？(半角数字で入力してエンター)\n>>> ')
    option = int(input())
    # 実行
    utauplugin.run(main, option=option)
