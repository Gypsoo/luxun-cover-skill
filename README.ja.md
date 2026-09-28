[简体中文](README.md) | [English](README.en.md) | **日本語**

# luxun-cover-skill

人とプログラミング用エージェントのための、民国期の書衣（本のカバー）をつくる道具である。エージェント向けの Skill と、ローカルで動く Python の生成器からなる。魯迅の本のために陶元慶が立てたカバーの文法で SVG を書く。幾何学的な文様、暖色の紙、墨に強調色ひとつ、広い余白、書名は文様から離す。出力はオマージュの構図であり、原カバーの複製ではない。

## これは何か

1926年ころ、陶元慶は魯迅の本の書衣を描いた。最も知られているのが『彷徨』である。上下に色帯、広い白紙、幾何学的な面、書名は片側に置く。後の印刷では色がずれ、画面も繰り返し翻刻された。このプロジェクトはその絵を描き直さず、烏合叢書の人物も描き直さない。文法を、繰り返し実行できる規則にした。

- カバーは本である。上下に書口があり、ポスターではない
- 文様は一角か一辺だけを占める
- 紙色が一層、墨が一層、強調色は多くて一つ
- 書名は字の塊である。縦組みは右上、横組みは下に置く

『呐喊』の初版カバーは魯迅自身の作、『野草』のカバーは孫福熙の作である。下の例はこれらの書名だけを使い、版式は新しい。

## 人物

**魯迅**（周樹人、1881–1936）は浙江紹興の人で、現代中国文学の主要な書き手である。小説集『呐喊』『彷徨』と散文詩集『野草』はいずれも1920年代に出た。彼は自分の本もデザインした。1923年の『呐喊』初版カバーは彼の作で、深紅の地に黒の一塊、書名と著者は陰文である。のちに陶元慶に書衣を頼んだ。再版で色がずれたとき、彼はそれを、画家にとって文章を改竄されて意味を失うのと同じことだと考えた。

**陶元慶**（1893–1929）、字は璇卿。画家で、浙江紹興の人である。1926年ころ魯迅の本のカバーを描き、本ツールがたどるのはこの系統である。『彷徨』は1926年8月、北新書局から初版が出た。烏合叢書の一冊で、カバーは彼の絵である。三人が並んで座り、落日に向かう。書名は片側に置き、上下に書口がある。魯迅は彼の展覧会について文章を書き、その絵は時代の思潮に合い、しかも中国自身の魂を失っていない、とした。本ツールが取るのは幾何学文様、暖色の紙、少ない色、広い余白である。あの絵は複製しない。

**孫福熙**（1898–1962）、字は春苔。画家で、文章も書いた。孫伏園の弟であり、フランスで絵を学んだ。1927年の『野草』初版カバーは彼の作で、山水に近い。雲、遠山、草である。これは陶元慶の幾何学的な書衣ではなく、本生成器のひな型でもない。

よく一緒に挙げられる三冊は、カバーの作者がそれぞれ違う。

| 書 | カバー |
| --- | --- |
| 『呐喊』（1923年初版） | 魯迅自身のデザイン |
| 『彷徨』（1926年） | 陶元慶 |
| 『野草』（1927年） | 孫福熙 |

詳細は [docs/references.md](docs/references.md)。この文書は中国語である。

## インストール

Python 3.10 以降。配布名は `luxun-cover-skill`、コマンドは `luxun-cover` である。

```bash
pip install -e .
```

書名は既定で輪郭パスに変換して SVG に書き込む（`--outline-text`）。`--no-outline-text` を付けると `<text>` に戻る。輪郭は、そのマシンに入っている中国語フォントから取る。フォントファイルはリポジトリに置かず、SVG にも埋め込まない。中国語フォントのないマシンで SVG を開いても、cairosvg で PNG に書き出しても、字は漢字のまま残り、空白の四角にはならない。

まず `fc-list` で探す。当たらなければ、既知のインストールパスをいくつか試す。順序は下のとおりで、明朝系が先、ゴシック系が後である。当たったフォントは「魯」の字を実際に持っていなければならない。漢字を含まない Noto Sans へ落ちないようにするためである。

### フォントの順序

```
Noto Serif CJK SC
Noto Serif SC
Source Han Serif SC
Source Han Serif CN
Source Han Serif
Songti SC
Songti TC
STSong
SimSun
AR PL UMing CN
AR PL UMing TW
PingFang SC
Hiragino Mincho ProN
Noto Sans CJK SC
Noto Sans SC
Source Han Sans SC
Source Han Sans CN
Microsoft YaHei
WenQuanYi Zen Hei
WenQuanYi Micro Hei
Droid Sans Fallback
```

Noto CJK、源ノ明朝（Source Han Serif）、源ノ角ゴシック（Source Han Sans）は SIL Open Font License である。このリポジトリにフォントファイルは含めない。

Linux:

```bash
sudo apt install fonts-noto-cjk
```

このパッケージには Noto Serif CJK SC と Noto Sans CJK SC の両方が入っている。

macOS には Songti SC と PingFang SC がある。`brew install --cask font-noto-serif-cjk` でもよい。Windows には宋体（SimSun）と微软雅黑（Microsoft YaHei）がある。[Noto Serif CJK](https://github.com/notofonts/noto-cjk) または源ノ明朝を入れてもよい。

どれも見つからないとき、輪郭モードはインストールを促すエラーで終わり、空白の四角は描かない。`--no-outline-text` は引き続き `<text>` を書き、`font-family` には上と同じ名前を使い、最後は `serif` に落ちる。その経路はビューアと fontconfig に依存する。中国語フォントがなければ、字は四角になる。

## カバーを一枚つくる

```bash
luxun-cover --title 彷徨 --out panghuang.svg
```

または次でも同じである。

```bash
python -m luxun_cover --title 彷徨 --out panghuang.svg
```

`--out` の親ディレクトリがなければ作る。標準出力には SVG のパスを出す。書名が8字を超える、文様の占める面積が大きすぎる、書名と文様が近すぎる、のいずれかのとき、標準エラーに `note:` を出す。

| 引数 | 説明 |
| --- | --- |
| `--title` | 書名。必須。短い方がよい。8字を超えると `note:` を出す。16字を超えるとエラー |
| `--author` | 著者。既定は「鲁迅」。署名しないときは空文字列。最大12字 |
| `--subtitle` | 副題。空でよい。既定は空。最大18字 |
| `--motif` | 文様。既定は `lattice`。`lattice` は窓格子、`cloud` は雲頭、`frame` は角枠、`meander` は雷文 |
| `--palette` | 色板。既定は `cinnabar`。`cinnabar` は朱砂、`ochre` は赭黄、`indigo` は暗い藍、`ink` は墨のみ |
| `--layout` | `auto`（既定）、`vertical` は縦組み、`horizontal` は横組み。`auto` では窓格子と角枠が縦、雲頭と雷文が横 |
| `--seed` | 整数。既定は `1`。同じ種からは同じ SVG が出る |
| `--outline-text` / `--no-outline-text` | 既定では漢字を輪郭にする。切ると `<text>` を書き、ビューアのフォントに依存する |
| `--out` | 出力する `.svg` のパス。必須 |
| `--png` | 同名の `.png` も書く。下の任意依存が要る。v0.1 が保証するのは SVG だけ |

PNG は v0.1 の既定の機能ではない。必要なときに任意依存を入れ、`--png` を付ける。システムに cairo が要る。cairo がなければ、ブラウザで SVG を開く。

```bash
pip install 'luxun-cover-skill[png]'
luxun-cover --title 彷徨 --out panghuang.svg --png
```

## 例

<table width="100%">
<tr>
<td width="33%" align="center"><img src="examples/panghuang.png" alt="彷徨" width="100%"></td>
<td width="33%" align="center"><img src="examples/nahan.png" alt="呐喊" width="100%"></td>
<td width="33%" align="center"><img src="examples/yecao.png" alt="野草" width="100%"></td>
</tr>
<tr>
<td align="center"><b>彷徨</b><br>赭黄 · 窓格子</td>
<td align="center"><b>呐喊</b><br>墨のみ · 雲頭</td>
<td align="center"><b>野草</b><br>暗藍 · 角枠</td>
</tr>
</table>

オマージュの構図であり、原カバーではない。『呐喊』の初版は魯迅自身の作、『野草』は孫福熙の作である。図は PNG のプレビューで、基準は SVG である。

<details>
<summary>再生成</summary>

この『呐喊』は、1923年に魯迅が自ら作った赤地に黒一塊の初版ではない。この『野草』は孫福熙の山水ではない。

```bash
luxun-cover --title 彷徨 --author 鲁迅 --palette ochre --motif lattice --layout vertical --seed 0 --out examples/panghuang.svg
luxun-cover --title 呐喊 --author 鲁迅 --palette ink --motif cloud --layout horizontal --seed 1 --out examples/nahan.svg
luxun-cover --title 野草 --author 鲁迅 --palette indigo --motif frame --layout vertical --seed 1 --out examples/yecao.svg
```

雷文の例：

```bash
luxun-cover --title 呐喊 --palette cinnabar --motif meander --layout horizontal --seed 1 --out nahan-meander.svg
```

</details>

## エージェント向け

リポジトリ直下の [SKILL.md](SKILL.md) は、プログラミング用エージェントへの手順である。いつ使うか、いつ止めるか、色板と文様の選び方、ファイルを書いたあとの点検項目が書いてある。このファイルは中国語である。

視覚上の規則の細目は [docs/aesthetic.md](docs/aesthetic.md)。歴史的な参照と著作権は [docs/references.md](docs/references.md)。どちらも中国語である。

## テスト

```bash
python -m unittest discover -s tests
```

リポジトリのルートで実行する。テストは描かれた SVG を調べ、`examples/` にコミット済みの三つのファイルが現在の出力と一致するかを照合する。

## 許諾とオマージュ

[MIT](LICENSE)。

幾何学文様はプログラムの中で計算したもので、陶元慶の絵からトレースしたものではない。出力を『彷徨』の原カバーとも、烏合叢書の原画とも呼ばない。SVG の `<desc>` には `not a facsimile` とある。消さない。陶元慶は1929年に没した。著作権の期間は国によって異なり、後世のスキャンが別に権利を持つこともある。確実な使い方は、文法を学び、画面を複製しないことである。詳細は [docs/references.md](docs/references.md)。
