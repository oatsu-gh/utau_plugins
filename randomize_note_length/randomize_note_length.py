#!/usr/bin/env python3
# Copyright (c) 2025 oatsu
"""
正規分布に従ってノート長をランダムに調整するプラグイン。
ユニゾンとかハモリでの使用を想定。
"""

import random

import utaupy


def randomize_note_length(plugin: utaupy.utauplugin.UtauPlugin, sigma: int = 15):
    """
    ノート長をランダムに調整する関数。
    指定されたUtauPluginオブジェクト内のノート列に対して、各ノートの長さを正規分布（平均0、標準偏差sigma）に基づいてランダムに増減させます。
    ただし、ノート長がsigma以下になる場合は調整をスキップします。調整は隣接する2つのノート間で行われ、全体の長さは維持されます。
    Args:
        plugin (utaupy.utauplugin.UtauPlugin): ノート長をランダム化する対象のUtauPluginオブジェクト。
        sigma (int, optional): ノート長調整の標準偏差。デフォルトは 20 [ticks] = 3連64分。
    Returns:
        None
    """

    notes = plugin.notes
    residual = 0  # 調整残差を保持（浮動小数で計算）

    for i in range(len(notes) - 1):  # 最後のノートは対象外
        note = notes[i]
        next_note = notes[i + 1]

        # 平均0、標準偏差σの正規分布から調整値を取得しつつ、残差を加える。
        delta = round(random.gauss(0, sigma)) + round(residual)

        new_length = note.length + delta
        new_next_length = next_note.length - delta

        # ノート長が0以下になる場合はスキップ
        if new_length <= sigma or new_next_length <= sigma:
            residual = 0.0
            continue

        # 調整を適用
        note.length = new_length
        next_note.length = new_next_length

        residual = 0.0  # 残差は吸収済み


if __name__ == "__main__":
    # 使用例
    utaupy.utauplugin.run(randomize_note_length)
