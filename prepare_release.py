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

RELEASE_DIR = '_release'
RELEASE_NAME = 'utau_plugins_v---'
IGNORE_LIST = [RELEASE_DIR, basename(__file__),
               '_archive', '_test', '.git', '.gitignore', '.gitattribute']
REMOVE_LIST = ['__pycache__', '.mypy']


def upgrade_pip():
    r"""
    python-3.9.5-embed-amd64/python.exe -m pip install --upgrade pip

    同梱配布するパッケージを更新する。
    """
    python_exe = glob(join('python-*-embed-*', 'python.exe'))[0]
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'setuptools'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'wheel'], check=True)
    subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'send2trash'], check=True)


def remove_cache_files(remove_list):
    """
    キャッシュファイルを削除する。
    """
    # キャッシュフォルダを再帰的に検索
    dirs_to_remove = [path for path in glob(join('**', '*'), recursive=True)
                      if (isdir(path) and basename(path) in remove_list)]
    for cache_dir in dirs_to_remove:
        print(f'  {cache_dir}')
        rmtree(cache_dir)


def copy_files_to_release_dir(release_dir, ignore_list):
    """
    配布したいファイルをリリース用のフォルダに複製する。
    """
    if exists(release_dir):
        rmtree(release_dir)
    # 直下のファイルとフォルダ一覧を取得
    files_and_dirs = [path for path in glob('*') if path not in ignore_list]
    for path in files_and_dirs:
        print(f'  {path}')
        if isdir(path):
            copytree(path, join(release_dir, basename(path)))
        else:
            copy2(path, join(release_dir, basename(path)))


def markdown2txt(release_dir):
    """
    プラグインフォルダ内の Markdown ファイルの拡張子 .md から .txt に変える。
    """
    markdown_files = glob(join(release_dir, '*.md')) + glob(join(release_dir, '*', '*.md'))
    for path_markdown in markdown_files:
        print(f'  {path_markdown}')
        path_txt = f'{splitext(path_markdown)[0]}.txt'
        rename(path_markdown, path_txt)


def main(release_dir, ignore_list, remove_list):
    """
    不要なファイルを削除してから、リリースフォルダに複製する。
    """
    # 組み込み用Pythonの中にあるpipをアップデートする。
    print('Upgrading pip')
    upgrade_pip()
    # キャッシュファイルを削除
    print('Removing cache')
    remove_cache_files(remove_list)
    print('Copyind files')
    try:
        copy_files_to_release_dir(release_dir, ignore_list)
    except FileExistsError as e:
        print(e)
        input('Failed to prepare release.')
    # Markdownファイルをプレーンテキストファイルに変更
    print('Renaming markdown files')
    # md拡張子をtxtに変更する
    markdown2txt(release_dir)


if __name__ == '__main__':
    chdir(dirname(__file__))
    main(join(RELEASE_DIR, RELEASE_NAME), IGNORE_LIST, REMOVE_LIST)
    input('Press Enter to exit.')
