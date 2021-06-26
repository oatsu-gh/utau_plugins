#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
utau_plugin をリリース用にする奴。
"""

import subprocess
from glob import glob
from os import chdir
from os.path import basename, dirname, exists, isdir, join
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
    dirs_to_remove = [path for path in glob(join('**/', ''), recursive=True)
                      if basename(path) in remove_list]
    for cache_dir in dirs_to_remove:
        print(f'  {cache_dir}')
        rmtree(cache_dir)


def copy_files_to_release_dir(release_dir, release_name, ignore_list):
    """
    配布したいファイルをリリース用のフォルダに複製する。
    """
    if exists(join(release_dir, release_name)):
        rmtree(release_dir, release_name)
    # 直下のファイルとフォルダ一覧を取得
    files_and_dirs = [path for path in glob('*') if path not in ignore_list]
    for path in files_and_dirs:
        print(f'  {path}')
        if isdir(path):
            copytree(path, join(release_dir, release_name, basename(path)))
        else:
            copy2(path, join(release_dir, release_name, basename(path)))


def main():
    """
    不要なファイルを削除してから、リリースフォルダに複製する。
    """
    print('Upgrading pip')
    upgrade_pip()
    print('Removing cache')
    remove_cache_files(REMOVE_LIST)
    print('Copyind files')
    try:
        copy_files_to_release_dir(RELEASE_DIR, RELEASE_NAME, IGNORE_LIST)
    except FileExistsError as e:
        print(e)
        input('Failed to prepare release.')


if __name__ == '__main__':
    chdir(dirname(__file__))
    main()
    input('Press Enter to exit.')
