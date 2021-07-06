#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
ふえるわかめ
"""
from os.path import exists
from shutil import copytree


def main():
    """
    わかめを生産する
    """
    new_wakame_dir = '../wakame_increased'
    while exists(new_wakame_dir):
        new_wakame_dir += '_increased'
    print('               ____             ')
    print('     ____    (    (     ____    ')
    print('   (    (     )    )  (    (    ')
    print('    )    )   (    (    )    )   ')
    print('   (    (     )   )  (    (     ')
    print(' ~~~)   )~~~~(~  (~~~~ )   )~~~ ')
    print(' ~~(~  (~~~~~~~~~~~~~(~  (~~~~  ')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    copytree('./', new_wakame_dir)


if __name__ == '__main__':
    main()
