#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
r"""
インストールしたいUTAUプラグインを選択して、
C:\Users\{username}\AppData\Roaming\UTAU\Plugins にインストールする。
"""

import subprocess
from glob import glob
from os import chdir
from os.path import basename, dirname, exists, expandvars, join, relpath
from shutil import copytree

from send2trash import send2trash


def utau_appdata_root() -> str:
    r"""
    プラグインとか音源が置いてあるフォルダのパスを返す。
    C:\Users\{username}\AppData\Roaming\UTAU

    この関数は utaupy.utau.utau_appdata_root() を移植したもの。
    """
    return expandvars(r'%APPDATA%\UTAU')


def get_python_dir(start='./'):
    """
    組み込み用Pythonのフォルダを特定する。
    """
    # python.exeのパスをすべて取得する
    python_exe_files = glob(join(start, 'python-*-embed-*', 'python.exe'))
    # 一つも見つからなかった場合
    if len(python_exe_files) == 0:
        raise Exception('組み込み用Pythonが見つかりません。')
    # 複数見つかった場合
    if len(python_exe_files) > 1:
        raise Exception('組み込み用Pythonが複数見つかってしまいました。開発者に連絡してください。',
                        str([relpath(path) for path in python_exe_files]))
    # 一つだけ見つかった場合(正常な場合)
    python_dir = dirname(python_exe_files[0])
    return python_dir


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
    available_plugins = [dirname(path) for path in glob(join(start, '*', 'plugin.txt'))]
    available_plugins_names = [read_plugin_txt_as_dict(path)['name'] for path in available_plugins]
    # ユーザーに指定させるために表示する文字列を作成する。
    message = '\n'.join(f'  {i}: {name}' for i, name in enumerate(available_plugins_names))
    # ユーザーにプラグインを指定させる。
    print('インストールしたいプラグインを番号で指定してください。')
    print(message)
    idx = int(input('>>> '))
    print(f'「{available_plugins_names[idx]}」をインストールします。')
    # 選んだプラグインのパスを返す
    return available_plugins[idx]


def install_plugin(input_dir, python_dir, dst_dir):
    """
    ソースコードをUTAUプラグインフォルダにインストールする。
    input_dir: インストールしたいプラグインのフォルダ
    path_python_dir: Embeddable Python のフォルダ
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
    # Pythonをインストールする
    copytree(python_dir, join(output_dir, basename(python_dir)))
    # インストール先のパスを返す
    return output_dir


def make_wrapper_bat(plugin_installed_dir):
    r"""
    UTAUプラグインとしてちゃんと動くように、wrapper としてのバッチファイルを作成する。
    プラグインのフォルダ名とPythonスクリプト名が一致する必要がある。
    @python-3.9.5-embed-amd64\python.exe plugin_name.py %*
    """
    # pythonw.exeを探す
    path_python_exe = glob(join('python-*-embed-*', 'python.exe'))[0]
    # plugin_name.py のファイル名がフォルダ名と一致する前提で処理する。
    plugin_name = basename(plugin_installed_dir)
    # プラグインのフォルダ名とPythonスクリプト名が一致することを確認する。
    assert exists(join(plugin_installed_dir, f'{plugin_name}.py'))
    # バッチファイルのパス
    path_bat = join(plugin_installed_dir, f'{plugin_name}.bat')
    # バッチファイルに書き込む文字列
    s = f'{path_python_exe} "{plugin_name}.py" %*'
    # バッチファイルに書き込む
    with open(path_bat, 'w', encoding='cp932') as f:
        f.write(s)


def install_requirements_with_pip(plugin_installed_dir):
    """
    Python.exeとソースコードのインストールが終わったフォルダを指定して、
    そのプラグインに必要なライブラリをインストールする。
    """
    # プラグインのフォルダ名やユーザー名に空白があると困るので、作業フォルダを移動する。
    chdir(plugin_installed_dir)
    # pythonw.exeを探す
    path_python_exe = glob(join('python-*-embed-*', 'python.exe'))[0]
    # ライブラリをインストール
    if exists('requirements.txt'):
        subprocess.run([path_python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                       check=True)
    else:
        subprocess.run([path_python_exe, '-m', 'pip', 'install', 'utaupy'],
                       check=True)
    # 作業フォルダをもとに戻す
    chdir(dirname(__file__))


def main():
    """
    インストール先のpathをCMDに返す
    """
    # 組み込み用Pythonのフォルダを特定する
    python_dir = get_python_dir()
    # インストールしたいプラグインを指定する。
    input_dir = select_plugin()
    # インストールする。
    utau_appdata_roaming_plugins = join(utau_appdata_root(), 'plugins')
    installed_dir = install_plugin(input_dir, python_dir, utau_appdata_roaming_plugins)
    # バッチファイルを作成する。
    make_wrapper_bat(installed_dir)
    # インストールしたプラグインに必要なライブラリをインストールする。
    install_requirements_with_pip(installed_dir)
    print('インストール完了しました！')


if __name__ == '__main__':
    chdir(dirname(__file__))
    main()
