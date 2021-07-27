#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
r"""
インストールしたいUTAUプラグインを選択して、
C:\Users\{username}\AppData\Roaming\UTAU\Plugins にインストールする。
"""

import subprocess
import sys
from glob import glob
from os import chdir
from os.path import basename, dirname, exists, expandvars, join, relpath
from shutil import copytree

from send2trash import send2trash


def upgrade_python_embed_packages():
    r"""
    python-3.9.5-embed-amd64/python.exe -m pip install --upgrade pip

    同梱配布するパッケージを更新する。
    """
    print('Upgrading packages')
    python_exe = find_python_exe()
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'setuptools'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'wheel'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'send2trash'], check=True)


def utau_appdata_root() -> str:
    r"""
    プラグインとか音源が置いてあるフォルダのパスを返す。
    C:\Users\{username}\AppData\Roaming\UTAU

    この関数は utaupy.utau.utau_appdata_root() を移植したもの。
    """
    return expandvars(r'%APPDATA%\UTAU')


def find_python_exe():
    """
    組み込み用Pythonの実行ファイルのパスを特定する。
    子フォルダの改装にあるものを探して、相対パスを返す。
    """
    # python.exeのパスをすべて取得する
    python_exe_files = glob(join('python-*-embed-*', 'python.exe'))
    # 一つも見つからなかった場合
    if len(python_exe_files) == 0:
        raise Exception('組み込み用Pythonが見つかりません。')
    # 複数見つかった場合
    if len(python_exe_files) > 1:
        raise Exception('組み込み用Pythonが複数見つかってしまいました。開発者に連絡してください。',
                        str([relpath(path) for path in python_exe_files]))
    # 一つだけ見つかった場合(正常な場合)
    python_exe = python_exe_files[0]
    return python_exe


def read_plugin_txt_as_dict(input_dir) -> dict:
    """
    指定したフォルダにある plugin.txt を読んで名前を取得する。
    """
    path_plugin_txt = join(input_dir, 'plugin.txt')
    # 読み取る
    try:
        with open(path_plugin_txt, 'r', encoding='cp932') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(path_plugin_txt, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(path_plugin_txt, 'w', encoding='cp932') as f:
            f.writelines(lines)
    # 改行文字と空白を消したのち、イコールで分割して2次元リストにする
    lines_2d = [line.strip('\n\r 　').split('=', maxsplit=1) for line in lines]
    # 辞書にする
    d = {key_and_value[0]: key_and_value[1] for key_and_value in lines_2d}
    # 結果を返す
    return d


def select_plugin(start='./'):
    """
    インストールしたいプラグインをユーザーに指定させる。
    """
    # インストール可能なプラグイン一覧を取得する。
    available_plugins = \
        [dirname(path) for path in glob(join(start, '*', 'plugin.txt'))]
    available_plugins_names = \
        [read_plugin_txt_as_dict(path)['name'] for path in available_plugins]
    # ユーザーに指定させるために表示する文字列を作成する。
    message = '\n'.join(f'  {i}: {name}' for i, name in enumerate(available_plugins_names))
    # ユーザーにプラグインを指定させる。
    print('インストールしたいプラグインを番号で指定してください。')
    print(message)
    # 番号を入力してもらう。
    idx = int(input('\n>>> '))
    # 対応するプラグイン名を示す。
    print(f'\n「{available_plugins_names[idx]}」をインストールします。')
    # 選んだプラグインのパスを返す。
    return available_plugins[idx], available_plugins_names[idx]


def install_plugin(input_dir, dst_dir):
    """
    ソースコードをUTAUプラグインフォルダにインストールする。
    input_dir: インストールしたいプラグインのフォルダ
    dst_dir: UTAUが参照するプラグインフォルダ

    1. インストール対象のフォルダがすでにある場合はゴミ箱に送る。
    2. プラグインをフォルダごとインストールする。
    """
    # プラグインがインストールされたらできるフォルダ
    output_dir = join(dst_dir, basename(input_dir))
    # すでにインストールされている場合は削除する
    if exists(output_dir):
        send2trash(output_dir)
    # ソースコードをインストールする
    copytree(input_dir, output_dir)

    # インストール先のパスを返す
    return output_dir


def install_python(plugin_installed_dir):
    """
    組み込み用Pythonをプラグインフォルダにインストールする。
    """
    python_dir = dirname(find_python_exe())
    # Pythonをインストールする
    copytree(python_dir, join(plugin_installed_dir, basename(python_dir)))


def install_requirements_with_pip(plugin_installed_dir):
    """
    Python.exeとソースコードのインストールが終わったフォルダを指定して、
    そのプラグインに必要なライブラリをインストールする。
    """
    # プラグインのフォルダ名やユーザー名に空白があると困るので、作業フォルダを移動する。
    chdir(plugin_installed_dir)
    # pythonw.exeを探す
    python_exe = find_python_exe()
    # ライブラリをインストール
    if exists('requirements.txt'):
        subprocess.run(
            [python_exe, '-m', 'pip', 'install',
             '--no-warn-script-location',
             '-r', 'requirements.txt'],
            check=True
        )
    else:
        subprocess.run(
            [python_exe, '-m', 'pip', 'install', '--no-warn-script-location', 'utaupy'],
            check=True
        )
    # 作業フォルダをもとに戻す
    chdir(dirname(__file__))


def make_wrapper_bat(plugin_installed_dir):
    r"""
    UTAUプラグインとしてちゃんと動くように、wrapper としてのバッチファイルを作成する。
    プラグインのフォルダ名とPythonスクリプト名が一致する必要がある。
    @python-3.9.5-embed-amd64\python.exe plugin_name.py %*
    """
    # バッチファイルから見たpython.exeの相対パスを一致させるため、作業フォルダを移動する。
    chdir(plugin_installed_dir)
    # pythonw.exeを探す
    python_exe = find_python_exe()
    # plugin_name.py のファイル名がフォルダ名と一致する前提で処理する。
    plugin_name = basename(plugin_installed_dir)
    # プラグインのフォルダ名とPythonスクリプト名が一致することを確認する。
    assert exists(join(plugin_installed_dir, f'{plugin_name}.py'))
    # バッチファイルのパス
    path_bat = join(plugin_installed_dir, f'{plugin_name}.bat')
    # バッチファイルに書き込む文字列
    s = f'{python_exe} "{plugin_name}.py" %*'
    # バッチファイルに書き込む
    with open(path_bat, 'w', encoding='cp932') as f:
        f.write(s)
    # もとの作業フォルダに戻る
    chdir(dirname(__file__))


def main():
    """
    インストール先のpathをCMDに返す
    """
    # オフライン版とオンライン版のどちらとしてダウンロードされたか調べる。
    release_name = basename(dirname(__file__))
    offline_mode = \
        any(keyword in release_name for keyword in ('offline', 'off-line', 'オフライン'))
    # インストールしたいプラグインを指定する。
    input_dir, plugin_name = select_plugin()
    # プラグインをインストールする。
    utau_appdata_roaming_plugins_dir = join(utau_appdata_root(), 'plugins')
    plugin_installed_dir = install_plugin(input_dir, utau_appdata_roaming_plugins_dir)

    # オンライン実行の場合は、Pythonやパッケージをオンデマンドインストールする。
    if not offline_mode:
        # インストーラーと同じ階層にあるPythonのpip等のパッケージをアップデートする。
        upgrade_python_embed_packages()
        # Pythonをインストールする。
        install_python(plugin_installed_dir)
        # インストールしたプラグインに必要なライブラリをインストールする。
        try:
            install_requirements_with_pip(plugin_installed_dir)
        except subprocess.CalledProcessError:
            print('--------------------------------------------------')
            print('プラグインのインストールに失敗しました。')
            print('インターネットに接続した状態でやり直してください。')
            print('--------------------------------------------------')
            sys.exit(1)

    # バッチファイルを作成する。プラグインフォルダに既にPythonが存在する必要がある。
    make_wrapper_bat(plugin_installed_dir)
    # 成功したことを伝える
    print(f'「{plugin_name}」をインストールしました！')


if __name__ == '__main__':
    chdir(dirname(__file__))
    main()
