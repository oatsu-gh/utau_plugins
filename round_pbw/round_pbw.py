#!/usr/bin/env python3
# Copyright (c) 2024 oatsu
"""
ピッチ点の高さを丸める。全て半音レベルにする。EnuPitchを使った後に使用する想定。
"""
from itertools import accumulate

import utaupy

# PBW丸める単位
PBW_UNIT_BY_NOTELENGTH = 64  # 分音符


def round_pbw(plugin):
    """ピッチ点のタイミングを時刻グリッドに合わせる
    """
    for note in plugin.notes:
        # PBWが無かったら何も処理せず次のノートに進む
        if note.pbw is None or len(note.pbw) == 0:
            continue
        # PBSが無かったら [0;0] を入れる
        if note.pbs is None:
            note.pbs = [0, 0]
        # 丸める単位
        unit_ms = (60 / note.tempo) / (PBW_UNIT_BY_NOTELENGTH / 4) * 1000

        # 丸めた時に誤差蓄積しないように累積和にする
        pbs_pbw_accumulate = list(accumulate(
            note.pbw, initial=float(note.pbs[0])))

        # グリッドに丸めこむ
        pbs_pbw_accumulate_round = [
            round(t / unit_ms) * unit_ms for t in pbs_pbw_accumulate]

        # PBWの累積時間を各ピッチ線の時間に戻す
        pbw_round = [
            t_1 - t_2 for (t_1, t_2) in
            zip(pbs_pbw_accumulate_round[1:], pbs_pbw_accumulate_round[:-1])
        ]

        # PBSに入れる
        note.pbs = [pbs_pbw_accumulate_round[0], note.pbs[1]]
        # PBWに入れる
        note.pbw = pbw_round


def reduce_pitch_points(plugin):
    """不要なピッチ点を削除する。具体的には、同じPBYが連続しているときに削除する。
    """
    for note in plugin.notes:
        # PBYがない場合はSkip
        if 'PBY' not in note:
            continue
        # 削減しようがない場合はSkip
        if len(note.pby) <= 2:
            continue
        assert len('PBY') == len('PBW') == len('PBM')

        # ピッチ点を削減する
        temp_pby = [note.pby[0]]
        temp_pbw = [note.pbw[0]]
        temp_pbm = [note.pbm[0]]

        # PBWの繰り越し量
        pbw_carry_over = 0
        for i, _ in enumerate(note.pby[1:-1], 1):
            if not note.pby[i-1] == note.pby[i] == note.pby[i+1]:
                temp_pby.append(note.pby[i])
                temp_pbw.append(note.pbw[i] + pbw_carry_over)
                temp_pbm.append(note.pbm[i])
                pbw_carry_over = 0
            else:
                print('ピッチ点を削除しました。')
                pbw_carry_over += note.pbw[i]

        # ノート内の最後のピッチ点を復元
        temp_pby.append(note.pby[-1])
        temp_pbw.append(note.pbw[-1] + pbw_carry_over)
        temp_pbm.append(note.pbm[-1])
        # 削減後のピッチ点でノート情報を上書き
        note.pby = temp_pby
        note.pbw = temp_pbw
        note.pbm = temp_pbm


def test_round_pbw():
    """round_pbw が想定通りの計算になっているかをテストする。
    """
    # テスト入力
    pbs_in = [-100, 0]
    pbw_in = [100, 30, 80, 50]
    tempo = 120

    # TODO: 64分音符で計算しなおす
    # 入力ピッチ点は -100ms, 0ms, +30ms, +110ms, +160ms にある。
    # BPM120で処理したら 32分音符グリッドは 60/120/8 = 0.0625 s = 62.5 ms なので、
    # 62.5 の倍数で丸められるはず。
    # 出力ピッチ点は -125ms, 0ms, 0ms, 125ms, 182.5 となる見込み。
    # pbsとpbw はそれに基づいて計算する。
    expected_pbs = [-125, 0]
    expected_pbw = [125, 0, 125, 62.5]

    # expected_pbs =
    # expected pbw =
    # サンプルUSTを作る
    plugin = utaupy.utauplugin.UtauPlugin()
    note = utaupy.ust.Note()
    note.tempo = tempo
    note.pbs = pbs_in
    note.pbw = pbw_in
    plugin.notes.append(note)
    # テスト
    round_pbw(plugin)
    pbs_out = plugin.notes[0].pbs
    pbw_out = plugin.notes[0].pbw
    print('pbs_in  :', pbs_in)
    print('pbs_out :', pbs_out)
    print('expected:', expected_pbs)
    print('-> PBS OK' if pbs_out == expected_pbs else '-> PBS NG')
    print('pbw_in  :', pbw_in)
    print('pbw_out :', pbw_out)
    print('expected:', expected_pbw)
    print('-> PBW OK' if pbw_out == expected_pbw else '-> PBW NG')
    assert pbs_out == expected_pbs and pbw_out == expected_pbw


def main(plugin):
    """全体の処理をする

    Args:
        plugin (utaupy.utauplugin.UtauPlugin): UtauPlubin オブジェクト
    """
    # ピッチ点を削減
    reduce_pitch_points(plugin)
    # PBWを丸める
    round_pbw(plugin)


if __name__ == "__main__":
    utaupy.utauplugin.run(main)
