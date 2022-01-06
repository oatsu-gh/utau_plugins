#!/usr/bin/env python3
# Copyright (c) 2021-2022 oatsu
"""
ENUNUで歌わせるときに適当に動くようにする。

- 歌詞すっぴん
- 促音を前の音符に結合
- 休符を連結
- 最後に休符がなかったら休符を追加
"""
import jaconv
import utaupy


def force_lyric_zenkaku_hiragana(plugin):
    """
    歌詞に含まれるカタカナとひらがなを、全角ひらがなにする。
    破壊的処理
    """
    for note in plugin.notes:
        lyric = note.lyric
        # 半角カタカナを全角カタカナにする
        lyric = jaconv.h2z(lyric, kana=True, ascii=False, digit=False)
        # カタカナをひらがなにする
        lyric = jaconv.kata2hira(lyric)
        # 無声化とかにつかう歌詞を適当に変更
        # 歌詞を上書きする
        note.lyric = lyric


def replace_special_lyric(plugin):
    """
    ブレスや語尾音素などの特殊歌詞を置換する
    """
    d_replace = {
        'ゔ': 'ヴ',
        ' n': 'ん', ' s': ' す', ' t': ' っ', ' k': ' っ', ' p': ' っ',
        ' h': ' R', ' -': ' R',
        '息': 'R', 'ぶれす': 'R', 'br': 'R',
        'づ': 'ず', 'を': 'お'
    }
    for note in plugin.notes:
        lyric = note.lyric
        for k, v in d_replace.items():
            lyric = lyric.replace(k, v)
        note.lyric = lyric


def suppin_lyric(plugin):
    """
    平仮名以外の文字を歌詞から削除する。
    """
    hiragana_set = {chr(i) for i in range(12353, 12436)}
    for note in plugin.notes:
        original_lyric = note.lyric
        # 休符のとき
        if 'R' in original_lyric:
            new_lyric = 'R'
        # 休符でないときは平仮名以外の文字をすべて削除
        else:
            new_lyric = ''.join(
                [character for character in original_lyric if character in hiragana_set]
            )
        # すっぴん化で歌詞が消滅した場合は元の歌詞を使う
        if len(new_lyric) == 0:
            note.lyric = original_lyric
        else:
            note.lyric = new_lyric


def join_cl(plugin):
    """
    歌詞が「っ」だった場合、次の処理を行う。
    1. そのノートを [#DELETE] にする
    2. そのノート長を 直前のノート長に加算する
    3. 直前のノートの歌詞に「っ」を追加する
    """
    notes = plugin.notes
    for i, note in enumerate(notes):
        if note.lyric == 'っ':
            # 「っ」のノートを削除 ([#DELETE] にする)
            note.delete()
            # 直前のノート
            previous_note = notes[i - 1]
            # 直前のノート長を伸ばす
            previous_note.length += note.length
            # 直前のノートの歌詞に「っ」を追加する
            previous_note.lyric += 'っ'


def join_R(plugin):
    """
    給付が連続しているときに結合する。
    """
    for i, note in enumerate(plugin.notes[:-1]):
        next_note = plugin.notes[i + 1]
        if note.lyric == 'R' and next_note.lyric == 'R':
            # 直後の休符を伸ばす
            next_note.length += note.length
            # 今の休符を削除 ([#DELETE] にする)
            note.delete()


def append_R(plugin):
    """
    最後が休符じゃなかったら追加
    """
    if plugin.notes[-1].lyric != 'R':
        new_note = utaupy.ust.Note()
        new_note.lyric = 'R'
        new_note.length = 480
        plugin.notes.append(new_note)


def main(plugin):
    """
    平仮名にしてからすっぴん化する。
    """
    # 歌詞すっぴん
    force_lyric_zenkaku_hiragana(plugin)
    replace_special_lyric(plugin)
    suppin_lyric(plugin)
    # 促音結合
    # join_cl(plugin)
    # 休符結合
    join_R(plugin)
    # 休符を追加する
    append_R(plugin)


if __name__ == '__main__':
    utaupy.utauplugin.run(main)
