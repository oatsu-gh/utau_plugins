#!python3
# coding: utf-8
# Copyright (c) oatsu
"""
連続音用歌詞すっぴんプラグイン
"""
from utaupy import utauplugin


def main(plugin):
    """
    "V CV" のCV部分はひらがなとカタカナとRのみ許可する
    """
    # 許可する文字のリスト
    allowed_list = [chr(i) for i in range(12353, 12436)] + [chr(i) for i in range(12449, 12532 + 1)] + ['R']

    notes = plugin.notes
    for note in notes:
        s = note.lyric
        if s == 'R':
            continue

        s1, s2 = s.split()  # VCVをVとCVに分割
        s3 = ''
        for c in s2:
            if c in allowed_list:
                s3 += c
        note.lyric = '{s1} {s3}'


if __name__ == '__main__':
    print('_____ξ・ヮ・) < lyric_suppin_ren v0.0.0 ________')
    utauplugin.run(main)
