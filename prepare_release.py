#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
utau_plugin をリリース用にする奴。
"""

from glob import glob
from os import chdir, rename
from os.path import basename, dirname, exists, isdir, join, splitext
from shutil import copy2, copytree, rmtree
from time import sleep

from tqdm import tqdm

from install import (find_python_exe, pip_install_requirements,
                     upgrade_python_embed_packages)

RELEASE_DIR = '_release'
RELEASE_NAME = 'utau_plugins_v---'
IGNORE_LIST = [RELEASE_DIR, basename(__file__), '__pycache__',
               '_archive', '_test', '.git', '.gitignore', '.gitattribute']
REMOVE_LIST = ['__pycache__', '.mypy']


def remove_cache_files(remove_list):
    """
    キャッシュファイルを削除する。
    """
    print('Removing cache')
    # キャッシュフォルダを再帰的に検索
    dirs_to_remove = [path for path in glob(join('**', '*'), recursive=True)
                      if (isdir(path) and basename(path) in remove_list)]
    # キャッシュフォルダを削除
    for cache_dir in tqdm(dirs_to_remove):
        rmtree(cache_dir)


def copy_files_to_release_dir(release_dir, ignore_list):
    """
    配布したいファイルをリリース用のフォルダに複製する。
    """
    print('Copying files')
    if exists(release_dir):
        rmtree(release_dir)
    # 直下のファイルとフォルダ一覧を取得
    files_and_dirs = [path for path in glob('*') if path not in ignore_list]
    for path in tqdm(files_and_dirs):
        # print(f'  {path}')
        if isdir(path):
            copytree(path, join(release_dir, basename(path)))
        else:
            copy2(path, join(release_dir, basename(path)))


def markdown2txt(release_dir):
    """
    プラグインフォルダ内の Markdown ファイルの拡張子 .md から .txt に変える。
    """
    print('Renaming markdown files')
    markdown_files = glob(join(release_dir, '*.md')) + glob(join(release_dir, '*', '*.md'))
    for path_markdown in tqdm(markdown_files):
        path_txt = f'{splitext(path_markdown)[0]}.txt'
        rename(path_markdown, path_txt)


def prepare_online_installer(online_release_dir, ignore_list):
    """
    オンライン環境向けのインストーラーを用意する。
    不要なファイルを削除してから、リリースフォルダに複製する。
    """
    print('\nPreparing online installer-----------------------------')
    # プラグインと組み込み用pythonをコピー
    copy_files_to_release_dir(online_release_dir, ignore_list)
    # md拡張子をtxtに変更する
    markdown2txt(online_release_dir)


def prepare_offline_installer(offline_release_dir, ignore_list):
    """
    オフライン環境向けのインストーラーを用意する。

    あらかじめ python-embed をあらかじめ仕込んで、
    pip install -r requirements.txt を済ませておく。
    """
    print('\nPreparing offline installer----------------------------')
    copy_files_to_release_dir(offline_release_dir, ignore_list)
    python_embed_dir = dirname(find_python_exe())
    # pythonのフォルダを除いた子フォルダをプラグインフォルダとみなす
    plugin_dirs = [path for path in glob(join(offline_release_dir, '*', ''))
                   if path != python_embed_dir]
    # 各プラグインに必要なパッケージをインストールする。
    basename_python_embed_dir = basename(python_embed_dir)
    for plugin_dir in plugin_dirs:
        copytree(python_embed_dir, join(plugin_dir, basename_python_embed_dir))
        print('\nInstalling requirements for', plugin_dir)
        pip_install_requirements(plugin_dir)
    print()
    # md拡張子をtxtに変更する
    markdown2txt(offline_release_dir)


def main(release_dir, ignore_list, remove_list):
    """
    オンラインインストーラーを準備してからオフラインインストーラーを準備する。
    """
    online_release_dir = release_dir
    offline_release_dir = release_dir + '_offline'
    # 組み込み用Pythonの中にあるpipをアップデートする。
    upgrade_python_embed_packages()
    # 一部のキャッシュフォルダが自動的に消えるのを待つ
    sleep(0.1)
    # オンラインインストーラーのリリースを作る
    prepare_online_installer(online_release_dir, ignore_list)
    # オフラインインストーラーのリリースを作る
    prepare_offline_installer(offline_release_dir, ignore_list)
    # キャッシュファイルを削除
    remove_cache_files(remove_list)


if __name__ == '__main__':
    chdir(dirname(__file__))
    main(join(RELEASE_DIR, RELEASE_NAME), IGNORE_LIST, REMOVE_LIST)
    input('\nPress Enter to exit.')
