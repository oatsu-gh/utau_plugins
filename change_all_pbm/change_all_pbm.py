#!/usr/bin/env python3
# Copyright (c) 2022 oatsu
"""
選択範囲のノートのピッチ形状を一括変更する。
"""
import itertools

import utaupy

# 「曲線」→「直線」→「R型」→「J型」→「曲線」の順に変更する。
PBM_TOGGLE_DICT = {'': 's', 's': 'r', 'r': 'j', 'j': ''}


def get_global_pbm_set(notes):
    """全ノート内のピッチ形状が同一か否かを返す。
    """
    # 各ノートからピッチ形状の項目を取り出して2次元リストにする。
    all_pbm_2d = [note.pbm for note in notes if 'PBM' in note]
    # 1次元にする。
    all_pbm_1d = itertools.chain.from_iterable(all_pbm_2d)
    # 選択範囲に含まれるピッチ形状の種類を列挙
    pbm_types = set(all_pbm_1d)
    # 何種類あるかを返す。pbmが含まれない場合は0になるはず。
    return pbm_types


def change_all_pbm(plugin):
    """全ノートのピッチ形状が同一の時、ピッチ形状を変更する。
    """
    if plugin.setting.get('Mode2') != 'True':
        raise Exception('UTAUのMode2が有効になっていません。')

    notes = plugin.notes
    pbm_set = get_global_pbm_set(notes)
    len_pbm_set = len(pbm_set)

    # ピッチ形状の情報が選択範囲に一つもない場合は何もしない
    if len_pbm_set == 0:
        new_pbm = ''
    # ピッチ形状が単一の場合
    elif len_pbm_set == 1:
        new_pbm = PBM_TOGGLE_DICT[list(pbm_set)[0]]
    # ピッチ形状が複数種類含まれる場合
    elif len_pbm_set > 1:
        new_pbm = ''

    # pbmを置換
    for note in notes:
        if 'PBM' in note:
            note.pbm = [new_pbm] * len(note.pbm)


if __name__ == "__main__":
    utaupy.utauplugin.run(change_all_pbm)
