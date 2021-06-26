#!/usr/bin/env python3
# Copyright (c) 2020 oatsu
"""
歌詞を大明神式にするプラグイン
3音以上離れていたら↑/↓
5音以上離れていたら↑↑/↓↓
"""
import utaupy


def daimyojinize(plugin: utaupy.utauplugin.UtauPlugin):
    """
    歌詞をいじる。pluginオブジェクトを破壊的処理する。
    """
    notes = plugin.notes
    # [#PREV] のノートがあるとき
    if plugin.previous_note is not None:
        notes.insert(0, plugin.previous_note)
    # 音程差を調べて、それに応じて歌詞を変える
    for idx, note in enumerate(notes[1:], 1):
        notenum_difference = note.notenum - notes[idx - 1].notenum
        note.lyric = note.lyric.strip('↑↓')
        if note.lyric == 'R' or notes[idx - 1].lyric == 'R':
            continue
        # 音程差が小さいとき
        if -3 < notenum_difference < 3:
            pass
        # 音程差が大きいとき
        elif notenum_difference >= 5:
            note.lyric += '↑↑'
        elif 3 <= notenum_difference < 5:
            note.lyric += '↑'
        elif -5 < notenum_difference <= 3:
            note.lyric += '↓'
        elif notenum_difference <= -5:
            note.lyric += '↓↓'
        else:
            raise Exception('音程差の区分に関するエラーです。開発者に連絡してください。')


if __name__ == '__main__':
    utaupy.utauplugin.run(daimyojinize)
