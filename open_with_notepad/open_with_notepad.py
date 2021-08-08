#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
「メモ長で開く」UTAUプラグイン
"""
import subprocess
from sys import argv

NOTEPAD_EXE = r"C:\WINDOWS\system32\notepad.exe"


def main(path_exe, path_plugin_script):
    """
    指定されたプログラムで指定されたファイルを開く。
    """
    print('メモ帳で編修中です。編集が終わったら、上書き保存してメモ帳を閉じてください。')
    print(path_plugin_script)
    subprocess.run([path_exe, path_plugin_script], check=True)


if __name__ == '__main__':
    main(NOTEPAD_EXE, argv[1])
