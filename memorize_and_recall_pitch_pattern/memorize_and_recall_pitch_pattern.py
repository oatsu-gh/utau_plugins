#!/usr/bin/env python3
# Copyright (c) 2023 oatsu
"""
ピッチパターンを記憶したり呼び出したりする
"""

import json
from os import remove
from os.path import dirname, join
from shutil import copy2

import utaupy

JSON_FILE = join(dirname(__file__), 'memory.json')
UST_FILE = join(dirname(__file__), 'memory_view.ust')
MAX_NOTE_LENGTH = 3840
MIN_NOTE_LENGTH = 10


def json2ust(path_json, path_ust):
    """ピッチを記録しているjsonファイルの内容をUTAUで確認できるようにUSTファイルに変換する
    """
    with open(path_json, 'r', encoding='utf-8') as f:
        d = json.load(f)
    ust = utaupy.ust.Ust()
    ust.setting['Mode2'] = True
    ust.setting['Charset'] = 'UTF-8'
    for key, v in d.items():
        previous_length, length, delta_notenum, lyric = \
            key.split('_', maxsplit=3)
        # 音程変化を確認するための音符を追加
        note = utaupy.ust.Note()
        note.lyric = 'dummy'
        note.length = previous_length
        note.label = previous_length
        note.notenum = 60
        ust.notes.append(note)
        # 本体
        note = utaupy.ust.Note()
        note.length = length
        note.label = length
        note.lyric = lyric
        note.pbw = v['PBW']
        note.pby = v['PBY']
        note.pbm = v['PBM']
        note.pbs = v['PBS']
        note['Modulation'] = 0
        note.notenum = 60 + int(delta_notenum)
        ust.notes.append(note)
        # 見た目を区切るための休符を追加
        note = utaupy.ust.Note()
        note.lyric = 'R'
        note.length = 1920 - (int(previous_length) + int(length)) % 1920
        note.notenum = 60
        ust.notes.append(note)
    ust.write(path_ust, encoding='utf-8')


def generate_key(note, previous_note, max_length, min_length):
    """ピッチ登録・呼び出し用のキーを生成する
    """
    # 直前の音高と現在の音高の差
    delta_notenum = note.notenum - previous_note.notenum
    # 直前のノート長を丸める
    previous_note_length = min(
        max_length,
        max(round(previous_note.length / min_length) * min_length, min_length))
    # 現在のノート長を丸める
    note_length = min(
        max_length,
        max(round(previous_note.length / min_length) * min_length, min_length))
    return f'{previous_note_length}_{note_length}_{delta_notenum}_{note.lyric}'


def memorize(plugin: utaupy.utauplugin.UtauPlugin):
    """指定されたノートのピッチパターンを辞書として返す
    辞書のキーは
    直前のノート長_現在のノート長_音程変化_直前の歌詞_現在の歌詞
    のようにする(暫定)
    """
    # 既存のファイルを読み取る
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
        copy2(JSON_FILE, JSON_FILE.replace('.json', '_backup.json'))
    except FileNotFoundError:
        d = {}
    # 各ノートのピッチ情報を読み取って記録していく
    if plugin.previous_note is not None:
        notes = [plugin.previous_note] + plugin.notes
    else:
        notes = plugin.notes
    # UST内からピッチパターンを読み取る
    d_temp = {}
    for note, previous_note in zip(notes[1:], notes[:-1]):
        # 登録に必要な情報が一つでもなければスキップ
        if any(k not in note for k in ['PBS', 'PBW', 'PBY', 'PBM', 'Lyric', 'Length']):
            continue
        # ピッチパターンを分類するときのキー
        key = generate_key(
            note, previous_note, max_length=MAX_NOTE_LENGTH, min_length=MIN_NOTE_LENGTH)
        # ピッチパターンを記録させる内容
        d_temp[key] = {
            'PBS': note.pbs,
            'PBW': note.pbw,
            'PBY': note.pby,
            'PBM': note.pbm
        }
    d.update(d_temp)
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(d, f, sort_keys=True, indent=4, ensure_ascii=False)
    json2ust(JSON_FILE, UST_FILE)


def recall(plugin: utaupy.utauplugin.UtauPlugin):
    """指定されたノートのピッチパターンを辞書として返す
    """
    # 既存のファイルを読み取る
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except FileNotFoundError:
        d = {}
    # 各ノートのピッチ情報を読み取って記録していく
    if plugin.previous_note is not None:
        notes = [plugin.previous_note] + plugin.notes
    else:
        notes = plugin.notes
    # UST内からピッチパターンを読み取る
    for note, previous_note in zip(notes[1:], notes[:-1]):
        # ピッチ情報を検索する文字列を生成
        key = generate_key(
            note, previous_note, max_length=MAX_NOTE_LENGTH, min_length=MIN_NOTE_LENGTH)
        # 一致するピッチ情報を探して登録
        if key in d:
            note.pbs = d[key]['PBS']
            note.pbw = d[key]['PBW']
            note.pby = d[key]['PBY']
            note.pbm = d[key]['PBM']


def clean_data():
    """ピッチデータを記録しているファイルを削除する
    """
    copy2(JSON_FILE, JSON_FILE.replace('.json', '_backup.json'))
    remove(JSON_FILE)
    remove(UST_FILE)


def main():
    """機能の分岐
    """
    s = '動作モードを選択して下さい\n'\
        '1: Memorize mode / ピッチ登録モード\n'\
        '2: Recall mode / ピッチ呼び出しモード\n'\
        '99: Clean mode / プラグインデータ初期化\n'\
        '>>> '
    mode = input(s).strip()
    if mode in ['1', '１']:
        utaupy.utauplugin.run(memorize)
    elif mode in ['2', '２']:
        utaupy.utauplugin.run(recall)
    elif mode in ['99', '９９']:
        if input('Really? / 本当に削除していいですか？(yes/no)\n>>> ') == 'yes':
            clean_data()


if __name__ == "__main__":
    main()
