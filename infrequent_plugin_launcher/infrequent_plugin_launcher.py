#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu
"""
# Infrequent Plugin Launcher
使用頻度の低いUTAUプラグインを呼び出すUTAUプラグイン

## 開発動機および要件
八歌さんのツイート
https://twitter.com/yauta7577/status/1338854212487114752

## 設計
1. プラグインフォルダにある各種プラグインのフォルダにある plugin.txt を読み取る。Appdata内にもプラグインがあることに注意。
2. 全プラグインのうち、plugin.txt 中のプラグイン名がエスケープされているものだけに絞り込む。
3. フォルダ名順に番号を振り、選択したプラグインを起動する。このとき、対象プラグインにUTAUからの一時ファイルを渡す。
4. 対象プラグインの処理が終わったら、このプラグイン自身も閉じる。
"""

import subprocess
from glob import glob
from os.path import abspath, basename, dirname
from pprint import pprint
from sys import argv

from tqdm import tqdm


def load_all_plugins(path_dir: str):
    """
    plugin.txt を全部取得する。
    その内容の一覧を辞書のリストにして返す。
    """
    l_path_plugintxt = glob(f'{path_dir}/*/plugin.txt')

    # 全プラグインの情報を格納するリスト
    all_plugins = []

    # 各プラグインの plugin.txt 内の情報をまとめる
    for path_plugintxt in tqdm(l_path_plugintxt):
        # plugin.txtを読みとる。
        with open(path_plugintxt, 'r', encoding='shift-jis') as f:
            lines = f.readlines(path_plugintxt)
        # 改行文字を取り除く
        lines = [line.strip() for line in lines]
        # プラグインの情報を取得して辞書にする
        d = {'path': abspath(path_plugintxt),
             'dirname': dirname(path_plugintxt),
             'basename': basename(path_plugintxt),
             'name': None,
             'shell': None}
        for line in lines:
            k, v = line.split('=')
            d[k] = v
        # プラグイン一覧に追加する
        all_plugins.append(d)

    # 全プラグインの情報のリストを返す
    return all_plugins


def filter_plugins(all_plugins: list):
    """
    全プラグインのリストを受け取り、
    無効化されてるプラグインだけに絞り込んだリストを返す。
    """
    infrequent_plugins = []
    for d_plugin in all_plugins:
        name = d_plugin['name']
        # 無効化されたプラグインだった場合のみリストに追加
        if name.startswith('//') or name.startswith('#'):
            d_plugin['name'] = name.lstrip('/#')
            infrequent_plugins.append(d_plugin)
    return infrequent_plugins


def run_external_plugin(d_plugin: dict, path_temporary_ust: str):
    """
    プラグインを起動して実行する。
    d_plugin: plugin.txt をもとにした辞書
    path_temporary_ust: UTAUがプラグインに渡す一時ファイルのパス
    """
    # 実行したいコマンド
    args = [d_plugin['abspath'], path_temporary_ust]
    # シェルを使うかどうか (True/False)
    use_shell: bool = (d_plugin['shell'] == 'use')
    # 対象のプラグインを起動
    subprocess.run(args=args, check=True, shell=(use_shell))


def select_plugin(plugins: list):
    """
    プラグイン一覧から、どのプラグインを使うか選択する。
    plugins: プラグイン情報を持つ辞書 のリスト
    """
    print('プラグインを半角数字で選択し、エンターを押してください。')
    # プラグインを一覧表示
    for i, d_plugin in enumerate(plugins):
        print(f'{i} : {d_plugin["name"]}\t({d_plugin["basename"]})')
    selected_i = int(input())
    # プラグイン情報の辞書を返す
    return plugins[selected_i]

def main():
    """
    全体の処理を実行
    """
    # UTAUが出力する一時ファイル(拡張子はtmp)
    path_temporary_ust = argv[1]
    # UTAU/plugins になるはずのパス
    path_plugins_dir = dirname(dirname(argv[0]))

    # 全プラグインを取得
    all_plugins = load_all_plugins(path_plugins_dir)
    print('all_plugins----------------------')
    pprint(all_plugins)
    # 絞り込む
    infrequent_plugins = filter_plugins(all_plugins)
    print('infrequent_plugins----------------------')
    pprint(infrequent_plugins)
    # プラグインをユーザーが選択する
    d_plugin = select_plugin(infrequent_plugins)
    print('d_plugin----------------------')
    pprint(d_plugin)

    # 実行する
    run_external_plugin(d_plugin, path_temporary_ust)


if __name__ == '__main__':
    main()
