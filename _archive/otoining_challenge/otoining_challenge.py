#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
chromedriverで診断メーカーをひらいて原音設定チャレンジをする。
"""

import subprocess
import winreg
from os import startfile
from os.path import join
from time import sleep
from glob import glob

import pyperclip
import utaupy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_character_name(plugin):
    """
    charecter.txt を参照して音源名を取得する。
    """
    character_txt = join(plugin.setting['VoiceDir'], 'character.txt')
    with open(character_txt) as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('name='):
            name = line.strip('\n\r').replace('name=', '')
            return name
    raise Exception('character.txtに音源名が記載されていません。')


def get_chrome_version():
    """
    Windowsにインストールされている Google Chrome のバージョンをレジストリから取得する。
    """
    reg_path = join('SOFTWARE', 'Google', 'Chrome', 'BLBeacon')
    key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, reg_path)
    version, _ = winreg.QueryValueEx(key, 'version')
    return version


def upgrade_chromedriver(chrome_version, path_python_exe):
    """
    chromedriver を更新して、Google Chrome のバージョンに合わせる。
    """
    subprocess.run([path_python_exe, '-m', 'pip', 'install', '--upgrade',
                    f'chromedriver-binary<={chrome_version}'], check=True)


def shindan(name: str):
    """
    診断メーカーのサイトで診断する
    """
    import chromedriver_binary
    driver = webdriver.Chrome()
    # 開く
    driver.get('https://shindanmaker.com/888119')
    # 診断したい名前を入力
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'shindanInput')))
    shindan_input = driver.find_element_by_id('shindanInput')
    shindan_input.send_keys(name)
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located)
    # 診断ボタンをクリックする
    sleep(2)
    shindan_button_submit = driver.find_element_by_id('shindanButtonSubmit')
    shindan_button_submit.click()
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located)
    # ほかの方法でシェアするボタンをクリック
    sleep(2)
    share_button = driver.find_element_by_xpath(r'/html/body/div[2]/div[2]/div[6]/div[2]/span[4]')
    share_button.click()
    # ツイートボタンからツイートするときのURLを取得する。
    sleep(2)
    tweet_button = driver.find_element_by_xpath(r'/html/body/div[2]/div[2]/div[6]/div[1]/span')
    data_share_url = tweet_button.get_attribute('data-share_url')
    # クリップボードにコピーするボタンをクリック
    share_copytext = driver.find_element_by_id('share-copytext')
    share_copytext.click()
    result = pyperclip.paste()
    sleep(3)

    return result, data_share_url

def find_pythonw_exe():
    """
    pipコマンドを実行するPythonwのパス
    """
    pythonw_exe = glob(join('python-*-embed-*', 'python.exe'))[0]
    return pythonw_exe


def main(plugin):
    """
    discription
    """
    # 音源名を取得
    character_name = get_character_name(plugin)
    if character_name == 'デフォルト':
        character_name = 'デフォ子'
    print('character_name:', character_name)
    # chromedriverを更新
    chrome_version = get_chrome_version()
    print('chrome_version:', chrome_version)

    # DEBUG: 組み込み用PythonではchromedriverがインストールできないならローカルのPythonを使う。
    pythonw_exe= find_pythonw_exe()
    # pythonw_exe = 'python'
    upgrade_chromedriver(chrome_version, pythonw_exe)

    # Seleniumつかって診断
    result, data_share_url = shindan(character_name)
    print('---- クリップボードにコピーしました ----')
    print(result)
    print('----------------------------------------')
    # print('data_share_url:', data_share_url)
    print('ツイート画面を開きます。')
    startfile(data_share_url)


if __name__ == '__main__':
    utaupy.utauplugin.run(main)
