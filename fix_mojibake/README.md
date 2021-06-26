# fix_mojibake

使用中の音源の readme.txt を開くついでに文字化けを直す UTAU プラグイン

## インストール

open_voicebank_readme.zip をダウンロードして、D&D でインストールしてください。

## 主な動作内容

- 各種ファイルの文字コードを修正する。
- 歌詞の文字化けを修復する。
- テンポが 500000 になってるのを 120 にする。
- 使用中の音源フォルダにある readme.txt を開く。

## 開発環境

- Windows 10
- Python 3.9.5
- utaupy 1.13.0
- UTAU 0.4.18e

## 更新履歴

### v0.0.1（2021-05-29）

- [open_voicebank_readme](https://github.com/oatsu-gh/open_voicebank_readme) として配布
- 初配布
    - readmeを開く機能のみ。

### v0.1.0（2021-06-20）

- [open_voicebank_readme](https://github.com/oatsu-gh/open_voicebank_readme) として配布
- 文字コード修正機能を追加
    - readme.txt, character.txt, prefix.map, oto.ini, ust の文字コードを修正します。
      - UTF8→cp932 に変換します。
- 文字化け歌詞修復機能を追加
    - UST ファイルが生きてたらちゃんと修復
    - UST ファイル自体が文字化けしていたら可能な限りで修復
- テンポが 500,000 の時に 120 にする機能を追加
- Mode2 を True にして UST を上書き保存する機能を追加

