#!/usr/bin/env python3
# Copyright (c) 2024 oatsu
"""
ピッチ点の高さを丸める。全て半音レベルにする。EnuPitchを使った後に使用する想定。
"""
from utaupy.utauplugin import run

# PBW丸める単位
PBW_UNIT_BY_NOTELENGTH = 32  # 分音符


def round_pbw(plugin):
    """音高を丸める
    """
    for note in plugin.notes:
        try:
            # 丸める単位
            unit_ms = (60 / note.tempo) / (PBW_UNIT_BY_NOTELENGTH / 4)
            # PBWが無かったら何も処理せず次のノートに進む
            if 'PBW' not in note:
                continue
            # PBSが無かったらオフセット無し
            if 'PBS' not in note:
                offset = 0
            # PBSにオフセットの値が入っているとき (基本的には負の値が入っていることに注意)
            # 負の値だとノート開始より前にピッチ点があり、正の値だと遅れた位置にピッチ点がある。
            else:
                offset = round(note.pbs[0] / unit_ms) * unit_ms
                note.pbs[0] = offset
                note.pbw = [round(x / unit_ms) * unit_ms for x in note.pbw]

        except Exception as e:
            print('Exception in note below ----------------------------------------')
            print(note)
            print('----------------------------------------------------------------')
            raise e


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


def main(plugin):
    # ピッチ点を削減
    reduce_pitch_points(plugin)
    # PBWを丸める
    round_pbw(plugin)


if __name__ == "__main__":
    run(main)
