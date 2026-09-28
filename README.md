# luxun-cover-skill

**中文**

给人和编程代理用的一套民国书衣工具：一份 Agent Skill，加上一个本地 Python 生成器。它按陶元庆为鲁迅书籍建立的封面语法作 SVG：几何纹样、暖纸、墨加一个强调色、大块余白、书名与纹样分开。输出是致敬构图，不是原封面的复制。

**English**

A tool for Republican-era Chinese book covers, for people and for coding agents: an agent skill, plus a local Python generator. It writes SVG in the cover grammar Tao Yuanqing set for Lu Xun’s books: geometric ornament, warm paper, ink plus one accent, wide margins, the title kept apart from the ornament. The output is a homage layout, not a copy of an original cover.

## 这是什么 / What this is

**中文**

1926 年前后，陶元庆为鲁迅做书衣。《彷徨》是其中最有名的一张：色地带、大片空纸、几何块面、书名排在一边。后来的印刷变过色，画面也被反复翻印。这个项目不复刻那张画，也不复刻乌合丛书上的人物。它把那套语法收成可以重复运行的规则：

- 封面是一本书，上下有书口，不是一张海报
- 纹样只占一角或一条边
- 一层纸色，一层墨色，最多再加一个强调色
- 书名是一块字。直排靠右上，横排落在下方

《呐喊》初版封面是鲁迅自己做的，《野草》封面是孙福熙做的。下面的示例只用这些书名，版式是新的。

**English**

Around 1926, Tao Yuanqing designed covers for Lu Xun’s books. 《彷徨》 is the best known of them: bands at the top and bottom, a large field of bare paper, geometric blocks, the title set to one side. Later printings shifted the colors, and the picture has been reproduced many times. This project does not redraw that picture, and it does not redraw the figures on the 乌合丛书 covers. It turns that grammar into rules that can be run again:

- The cover is a book, with bands at the top and bottom, not a poster
- The ornament takes one corner or one edge
- One paper color, one ink, and at most one accent
- The title is a block of type. Vertical setting sits at the upper right; horizontal setting sits lower down

The first-edition cover of 《呐喊》 was designed by Lu Xun. The cover of 《野草》 was designed by Sun Fuxi. The examples below use those titles only. The layouts are new.

## 安装 / Install

**中文**

需要 Python 3.10 或更新版本。包名是 `luxun-cover-skill`，命令是 `luxun-cover`。

**English**

Python 3.10 or newer. The distribution name is `luxun-cover-skill`. The command is `luxun-cover`.

```bash
pip install -e .
```

**中文**

书名默认转成轮廓路径再写入 SVG（`--outline-text`）。加 `--no-outline-text` 则改回 `<text>`。轮廓取自本机已安装的中文字体。字体文件不放进仓库，也不嵌入 SVG。没有中文字体的机器打开 SVG，或用 cairosvg 导出 PNG，看到的仍是汉字，而不是空心方框。

先用 `fc-list` 查找。没有命中时，再试几条已知的安装路径。顺序见下：宋体在前，黑体在后。命中的字体必须真有「鲁」这个字，避免退回到不含汉字的 Noto Sans。

**English**

By default the title is converted to outline paths and written into the SVG (`--outline-text`). `--no-outline-text` writes `<text>` instead. Outlines come from a CJK font already installed on the machine. Font files are not stored in this repository and are not embedded in the SVG. A machine without a CJK font can still open the SVG, or export PNG through cairosvg, and the characters stay Chinese characters rather than empty boxes.

The program asks `fc-list` first. If that returns nothing, it tries a few known install paths. The order is below: Song (serif) faces first, sans-serif faces after. The face must contain the character 鲁, so the search does not fall back to a Latin face such as Noto Sans.

### 字体顺序 / Font order

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

**中文**

Noto CJK 与思源宋体、思源黑体是 SIL Open Font License。本仓库不附带字体文件。

**English**

Noto CJK, Source Han Serif, and Source Han Sans are under the SIL Open Font License. This repository does not include the font files.

Linux:

```bash
sudo apt install fonts-noto-cjk
```

**中文**

这个包里同时有 Noto Serif CJK SC 和 Noto Sans CJK SC。

macOS 自带 Songti SC、PingFang SC，也可以 `brew install --cask font-noto-serif-cjk`。Windows 自带宋体（SimSun）和微软雅黑（Microsoft YaHei），也可以安装 [Noto Serif CJK](https://github.com/notofonts/noto-cjk) 或思源宋体。

一款都找不到时，轮廓模式会报错并提示安装，不会画出空心方框。`--no-outline-text` 仍写 `<text>`，`font-family` 用上面同一套名字，最后落到 `serif`。那条路径依赖查看器和 fontconfig。没有中文字体时，字会变成方框。

**English**

That package contains both Noto Serif CJK SC and Noto Sans CJK SC.

macOS includes Songti SC and PingFang SC. `brew install --cask font-noto-serif-cjk` also works. Windows includes SimSun (宋体) and Microsoft YaHei (微软雅黑). [Noto Serif CJK](https://github.com/notofonts/noto-cjk) or Source Han Serif (思源宋体) can be installed as well.

If none of these faces is found, outline mode exits with an install message and does not draw empty boxes. `--no-outline-text` still writes `<text>`, using the same family names and a final fallback of `serif`. That path depends on the viewer and on fontconfig. Without a CJK font, the characters become boxes.

## 生成一张封面 / Make a cover

```bash
luxun-cover --title 彷徨 --out panghuang.svg
```

或 / or:

```bash
python -m luxun_cover --title 彷徨 --out panghuang.svg
```

**中文**

`--out` 的父目录不存在时会创建。标准输出打印 SVG 路径。书名超过八个字、纹样占地偏多、或书名与纹样贴得太近时，标准错误打印 `note:`。

**English**

If the parent directory of `--out` does not exist, it is created. The SVG path is printed on stdout. stderr prints `note:` when the title is longer than eight characters, the ornament covers too much of the page, or the title sits too close to the ornament.

| 参数 / Flag | 中文 | English |
| --- | --- | --- |
| `--title` | 书名。必填。宜短。超过 8 个字会打印 `note:`；超过 16 个字报错 | Title. Required. Keep it short. Longer than 8 characters prints `note:`; longer than 16 is an error |
| `--author` | 著者。默认「鲁迅」。不要署名就传空字符串。最多 12 个字 | Author. Default `鲁迅`. Pass an empty string to omit the name. At most 12 characters |
| `--subtitle` | 副题。可空，默认空。最多 18 个字 | Subtitle. Optional, empty by default. At most 18 characters |
| `--motif` | 纹样。默认 `lattice`。`lattice` 窗格，`cloud` 云头，`frame` 角框，`meander` 回纹 | Motif. Default `lattice`. `lattice` window grid, `cloud` cloud-head border, `frame` corner frame, `meander` fret |
| `--palette` | 色板。默认 `cinnabar`。`cinnabar` 朱砂，`ochre` 赭黄，`indigo` 暗蓝，`ink` 纯墨 | Palette. Default `cinnabar`. `cinnabar`, `ochre`, `indigo` (dull blue), `ink` (ink only, no second color) |
| `--layout` | `auto`（默认）、`vertical` 直排、`horizontal` 横排。`auto` 时窗格和角框直排，云头和回纹横排 | `auto` (default), `vertical`, or `horizontal`. Under `auto`, lattice and frame are vertical; cloud and meander are horizontal |
| `--seed` | 整数。默认 `1`。相同种子得到相同 SVG | Integer. Default `1`. The same seed yields the same SVG |
| `--outline-text` / `--no-outline-text` | 默认把汉字转成轮廓。关掉之后写 `<text>`，依赖查看器字体 | On by default: characters become outlines. Off writes `<text>`, which depends on the viewer’s fonts |
| `--out` | 输出的 `.svg` 路径。必填 | Output `.svg` path. Required |
| `--png` | 同时写同名 `.png`。需要可选依赖，见下。v0.1 默认只保证 SVG | Also write a `.png` with the same stem. Needs the optional extra below. v0.1 guarantees SVG only |

**中文**

PNG 不是 v0.1 的默认能力。需要时再装可选依赖，并加上 `--png`。系统要有 cairo。没有 cairo 时，用浏览器打开 SVG。

**English**

PNG is not a default capability of v0.1. Install the optional extra and pass `--png` when a PNG is required. The system needs cairo. Without cairo, open the SVG in a browser.

```bash
pip install 'luxun-cover-skill[png]'
luxun-cover --title 彷徨 --out panghuang.svg --png
```

## 示例 / Examples

**中文**

下面三张都是本工具画的致敬构图，不是历史封面的扫描或复刻。预览 PNG 只为了在本页能看见；以 SVG 为准。

**English**

The three pictures below are homage layouts drawn by this tool. They are not scans or redrawings of historical covers. The PNG files are previews so this page can show them. The SVG is the reference.

### 彷徨

赭黄纸，朱红书口，窗格在左下，书名直排在右上。

Ochre paper, vermilion bands at the top and bottom, a lattice at the lower left, the title set vertically at the upper right.

![彷徨致敬构图 / homage layout, 彷徨](examples/panghuang.png)

```bash
luxun-cover --title 彷徨 --author 鲁迅 --palette ochre --motif lattice --layout vertical --seed 0 --out examples/panghuang.svg
```

### 呐喊

纯墨。上端一条云头边饰，书名落在下方双线之间。这不是 1923 年那张红地黑块的初版封面。初版封面是鲁迅自己做的。

Ink only. A cloud-head border along the top; the title sits between a pair of rules below. This is not the 1923 first-edition cover (red ground, one black block). Lu Xun designed that cover himself.

![呐喊致敬构图 / homage layout, 呐喊](examples/nahan.png)

```bash
luxun-cover --title 呐喊 --author 鲁迅 --palette ink --motif cloud --layout horizontal --seed 1 --out examples/nahan.svg
```

### 野草

暗蓝书口，角框，书名直排。这不是孙福熙那张山水封面。

Dull indigo bands, a corner frame, the title set vertically. This is not the landscape cover by Sun Fuxi.

![野草致敬构图 / homage layout, 野草](examples/yecao.png)

```bash
luxun-cover --title 野草 --author 鲁迅 --palette indigo --motif frame --layout vertical --seed 1 --out examples/yecao.svg
```

回纹可以这样试。 / A meander:

```bash
luxun-cover --title 呐喊 --palette cinnabar --motif meander --layout horizontal --seed 1 --out nahan-meander.svg
```

## 给 Agent / For agents

**中文**

仓库根目录的 [SKILL.md](SKILL.md) 是给编程代理的操作说明：什么时候用、什么时候停、怎么选色板和纹样、生成之后按什么清单自检。

视觉规则的细目在 [docs/aesthetic.md](docs/aesthetic.md)。历史参照和版权在 [docs/references.md](docs/references.md)。

**English**

[SKILL.md](SKILL.md), at the repository root, tells a coding agent when to use the tool, when to stop, how to choose a palette and a motif, and what to check after a file is written.

The visual rules are in [docs/aesthetic.md](docs/aesthetic.md). Historical sources and copyright are in [docs/references.md](docs/references.md).

## 测试 / Tests

```bash
python -m unittest discover -s tests
```

**中文**

在仓库根目录运行。测试检查渲染出的 SVG，并核对 `examples/` 里三张已提交的文件是否与当前输出一致。

**English**

Run it from the repository root. The tests check the rendered SVG, and compare the three committed files under `examples/` with the current output.

## 许可与致敬 / License and homage

**中文**

[MIT](LICENSE)。

几何纹样是程序里算出来的，不是从陶元庆的画上描的。不要把输出叫成《彷徨》原封面，也不要叫成乌合丛书原画。SVG 的 `<desc>` 里有 `not a facsimile`，留着。陶元庆卒于 1929 年，各国版权期限不同，后世扫描也可能另有权利。稳妥的用法是学语法，不复制画面。详见 [docs/references.md](docs/references.md)。

**English**

[MIT](LICENSE).

The ornaments are computed in the program. They are not traced from Tao Yuanqing’s paintings. Do not call an output the original cover of 《彷徨》, or an original 乌合丛书 drawing. The SVG `<desc>` contains the words `not a facsimile`. Do not delete them. Tao Yuanqing died in 1929. Copyright terms differ by country, and a later scan may carry rights of its own. The cautious practice is to learn the grammar and not to copy the picture. See [docs/references.md](docs/references.md).
