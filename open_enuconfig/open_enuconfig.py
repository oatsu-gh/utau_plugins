#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
音源フォルダにある enuconfig.yaml を開く
"""

from os import startfile
from os.path import join

import utaupy


def open_enuconfig(plugin):
    """
    音源のパスを取得して、そこにあるenuconfigを開く
    """
    path_enuconfig = join(plugin.voicedir, 'enuconfig.yaml')
    startfile(path_enuconfig)


if __name__ == '__main__':
    utaupy.utauplugin.run(open_enuconfig)
