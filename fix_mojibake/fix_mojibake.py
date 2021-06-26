#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
UTAU音源のreadme.txtを開くプラグイン

## 機能

- テンポを直す
- 歌詞の文字化けを修正する
- readme.txt の文字コードを修正する
- character.txt の文字コードを修正する
- prefix.map の文字コードを修正する
- oto.ini の文字コードを修正する
- テンポが 500000.00 の時に 120 にする
- USTファイルを修正する
    - 文字コードを修正する
    - Mode2を有効にする
- readme.txt を開く

usage:
    python open_voicebank_readme.py hogehoge.tmp
"""

from glob import glob
from os import startfile
from os.path import exists, join
from tempfile import TemporaryFile
from typing import Union

import utaupy


def utf8_to_cp932(path):
    """
    指定したファイルをUTF8で開いてcp932(Shift-JISの拡張)で再保存する。
    エンコードエラーが起きたら中断するために、いったんバックアップを取る。
    """
    if exists(path):
        try:
            with open(path, 'r', encoding='utf8') as f:
                s = f.read()
            with TemporaryFile('w', encoding='cp932') as f:
                f.write(s)
            with open(path, 'w', encoding='cp932') as f:
                f.write(s)
                print('UTAU上で文字化けしてそうだから直した。:', path)
        except UnicodeDecodeError:
            pass
        except UnicodeEncodeError:
            print('文字コードがcp932だと保存できない文字が入ってるみたい。:', path)


def is_mojibake_string(lyric: str) -> bool:
    """
    文字列がcp932デコードで文字化けしているか判定する。
    """
    if any(('縺' in lyric, '繧' in lyric, '繝' in lyric, '縲' in lyric)):
        return True
    return False


def repair_mojibake_lyrics(plugin):
    """
    UTF8のファイルを読み込んで文字化けしてしまった歌詞を直す。
    """
    plugin_lyrics = [note.lyric for note in plugin.notes]

    # 歌詞が文字化けしていなかったら何もしない。
    if not is_mojibake_string(''.join(plugin_lyrics)):
        return
    # 1か所でも歌詞が文字化けしていたら全部の歌詞を修復する。
    path_ust = plugin.setting.get('Project')
    if (path_ust is not None) and exists(path_ust):
        try:
            # USTファイルの文字コードを直して上書き保存する。
            ust = utaupy.ust.load(path_ust, encoding='utf-8')
            # USTファイルから文字化け前の歌詞を取得する
            ust_lyrics = [note.lyric for note in ust.notes]
            # USTファイルが文字化け歌詞で上書きされているかどうか
            ust_is_mojibaked = any(map(is_mojibake_string, ust_lyrics))
        # USTファイルが文字化けしているとそもそも開けないのを回避
        except UnicodeDecodeError:
            ust_is_mojibaked = True

        # USTファイルがUTF-8のまま無事な時
        if not ust_is_mojibaked:
            print('USTファイルを参照して歌詞を修復します。')
            new_lyrics = ust_lyrics
            # USTファイルのテンポと文字コードを修正して上書き保存
            ust.setting['Mode2'] = True
            fix_tempo(ust)
            ust.write(path_ust, encoding='cp932')
            print('USTファイルの文字コードを修正しました。USTファイルを開きます。')
            startfile(path_ust)

        # USTファイルが文字化け歌詞で上書きされており手遅れな時
        else:
            print('歌詞を可能な限り修復します。')
            new_lyrics = [lyric.encode('cp932').decode('utf-8', errors='ignore')
                          for lyric in plugin_lyrics]

        # ノート数が合うことを確認
        print(f'  歌詞修復前: [{"][".join(plugin_lyrics)}]')
        print(f'  歌詞修復後: [{"][".join(new_lyrics)}]')
        assert len(new_lyrics) == len(plugin_lyrics), '修復前後のノート数が一致しません。'

    # 歌詞を置換
    for i, note in enumerate(plugin.notes):
        note.lyric = new_lyrics[i]


def fix_tempo(ust: Union[utaupy.ust.Ust, utaupy.utauplugin.UtauPlugin]):
    """
    MIDIを取り込んだ時に生じるテンポを修正する。
    """
    if str(ust.tempo) in ['500000', '500000.00']:
        ust.notes[0].tempo = 120


def main(plugin):
    """
    ファイルの存在を確認して各種文字コードやUSTの不具合を修正する。
    """

    # readme.txt の文字化けを修正する
    path_readme_txt = join(plugin.voicedir, 'readme.txt')
    utf8_to_cp932(path_readme_txt)
    # character.txt の文字化けを修正する
    path_character_txt = join(plugin.voicedir, 'character.txt')
    utf8_to_cp932(path_character_txt)
    # prefix.map の文字化けを修正する
    path_prefix_map = join(plugin.voicedir, 'prefix.map')
    utf8_to_cp932(path_prefix_map)
    # oto.ini の文字化けを修正する
    otoini_files = glob(join(plugin.voicedir, '*/**/oto.ini'), recursive=True)
    for path_otoini in otoini_files:
        utf8_to_cp932(path_otoini)
    # テンポを直す
    fix_tempo(plugin)
    # 歌詞の文字化けを修正する
    repair_mojibake_lyrics(plugin)


if __name__ == '__main__':
    utaupy.utauplugin.run(main)
