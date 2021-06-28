#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
utau_plugin をリリース用にする奴。
"""

import subprocess
from glob import glob
from os import chdir, rename
from os.path import basename, dirname, exists, isdir, join, splitext
from shutil import copy2, copytree, rmtree
from time import sleep

from tqdm import tqdm
from install import install_requirements_with_pip

RELEASE_DIR = '_release'
RELEASE_NAME = 'utau_plugins_v---'
IGNORE_LIST = [RELEASE_DIR, basename(__file__), '__pycache__',
               '_archive', '_test', '.git', '.gitignore', '.gitattribute']
REMOVE_LIST = ['__pycache__', '.mypy']


def upgrade_python_embed_packages():
    r"""
    python-3.9.5-embed-amd64/python.exe -m pip install --upgrade pip

    同梱配布するパッケージを更新する。
    """
    print('\nUpgrading packages')
    python_exe = glob(join('python-*-embed-*', 'python.exe'))[0]
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'setuptools'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'wheel'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'send2trash'], check=True)


def remove_cache_files(remove_list):
    """
    キャッシュファイルを削除する。
    """
    print('\nRemoving cache')
    # キャッシュフォルダを再帰的に検索
    dirs_to_remove = [path for path in glob(join('**', '*'), recursive=True)
                      if (isdir(path) and basename(path) in remove_list)]
    for cache_dir in tqdm(dirs_to_remove):
        rmtree(cache_dir)


def copy_files_to_release_dir(release_dir, ignore_list):
    """
    配布したいファイルをリリース用のフォルダに複製する。
    """
    print('\nCopying files')
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
    print('\nRenaming markdown files')
    markdown_files = glob(join(release_dir, '*.md')) + glob(join(release_dir, '*', '*.md'))
    for path_markdown in tqdm(markdown_files):
        path_txt = f'{splitext(path_markdown)[0]}.txt'
        rename(path_markdown, path_txt)


def prepare_online_installer(release_dir, ignore_list):
    """
    オンライン環境向けのインストーラーを用意する。
    不要なファイルを削除してから、リリースフォルダに複製する。
    """
    # プラグインと組み込み用pythonをコピー
    copy_files_to_release_dir(release_dir, ignore_list)
    # md拡張子をtxtに変更する
    markdown2txt(release_dir)


def prepare_offline_installer(release_dir, ignore_list):
    """
    オフライン環境向けのインストーラーを用意する。

    あらかじめ python-embed をあらかじめ仕込んで、
    pip install -r requirements.txt を済ませておく。
    """
    copy_files_to_release_dir(release_dir, ignore_list)
    python_embed_dir = glob(join(release_dir, 'python-*-embed-*'))[0]
    plugin_dirs = [path for path in glob(join(release_dir, '*', '')) if path != python_embed_dir]
    basename_python_embed_dir = basename(python_embed_dir)
    for plugin_dir in plugin_dirs:
        copytree(python_embed_dir, join(plugin_dir, basename_python_embed_dir))
        print('\nInstalling requirements  for', plugin_dir)
        install_requirements_with_pip(plugin_dir)
    # 組み込み用Pythonの余ってるやつを削除
    rmtree(python_embed_dir)
    # md拡張子をtxtに変更する
    markdown2txt(release_dir)


def main(release_dir, ignore_list, remove_list):
    """
    オンラインインストーラーを準備してからオフラインインストーラーを準備する。
    """
    online_release_dir = release_dir
    offline_release_dir = release_dir + '_offline'
    # 組み込み用Pythonの中にあるpipをアップデートする。
    upgrade_python_embed_packages()
    prepare_online_installer(online_release_dir, ignore_list)
    prepare_offline_installer(offline_release_dir, ignore_list)
    # キャッシュファイルを削除
    remove_cache_files(remove_list)


if __name__ == '__main__':
    chdir(dirname(__file__))
    main(join(RELEASE_DIR, RELEASE_NAME), IGNORE_LIST, REMOVE_LIST)
    input('Press Enter to exit.')
