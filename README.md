# luxun-cover-skill

给人和编程代理用的一套民国书衣工具：一份 Agent Skill，加上一个本地 Python 生成器。它按陶元庆为鲁迅书籍建立的封面语法作图——几何纹样、暖纸、墨加一个强调色、大块余白、书名与纹样分开。

English: an agent skill and a local SVG generator for Republican-era Chinese book covers in the Tao Yuanqing idiom. Geometric ornament, paper, ink, one accent, wide margins. Homage layouts, not facsimiles.

## 这是什么

1926 年前后，陶元庆为鲁迅做书衣。《彷徨》是其中最有名的一张：色地带、大片空纸、几何块面、书名排在一边。后来的印刷变过色，画面也被反复翻印。这个项目不复刻那张画，也不复刻乌合丛书上的人物。它把那套语法收成可以重复运行的规则：

- 封面是一本书，有书口，不是一张海报
- 纹样只占一角或一条边
- 纸色、墨色，最多再加一个强调色
- 书名是一块字，直排靠右上，横排落在下方

《呐喊》初版封面是鲁迅自己做的，《野草》封面是孙福熙做的。下面的示例只用这些书名，版式是新的。

## 安装

需要 Python 3.10 或更新版本。

```bash
pip install -e .
```

书名默认转成轮廓路径再写入 SVG（`--outline-text`，加 `--no-outline-text` 则改回 `<text>`）。轮廓取自本机的中文字体，字体文件不放进仓库。这样另一台没有中文字体的机器打开 SVG，或用 cairosvg 导出 PNG，看到的仍是汉字，而不是方框。

查找顺序是宋体在前、黑体垫后：Noto Serif CJK SC、Source Han Serif SC / CN、Songti SC、STSong、SimSun、AR PL UMing CN、PingFang SC、Noto Sans CJK SC、Source Han Sans SC、Microsoft YaHei、WenQuanYi Zen Hei、WenQuanYi Micro Hei、Droid Sans Fallback。命中的字体必须真有「鲁」这个字，避免 fontconfig 退回到不含汉字的 Noto Sans。

Noto CJK 与思源宋体 / 思源黑体是 SIL Open Font License。本仓库不附带字体文件。

Linux：

```bash
sudo apt install fonts-noto-cjk
```

这个包里同时有 Noto Serif CJK SC 和 Noto Sans CJK SC。

macOS 自带 Songti SC、PingFang SC，也可以 `brew install --cask font-noto-serif-cjk`。Windows 自带宋体（SimSun）和微软雅黑（Microsoft YaHei），也可以安装 [Noto Serif CJK](https://github.com/notofonts/noto-cjk) 或思源宋体。

一款都找不到时，轮廓模式会报错并提示安装，不会画出空心方框。`--no-outline-text` 仍写活字，字体栈与上面相同，最后落到 `serif`；那条路径依赖查看器和 fontconfig，没有中文字体时会变成方框。

## 生成一张封面

```bash
luxun-cover --title 彷徨 --out panghuang.svg
```

或：

```bash
python -m luxun_cover --title 彷徨 --out panghuang.svg
```

| 参数 | 含义 |
| --- | --- |
| `--title` | 书名，必填，宜短 |
| `--author` | 著者，默认「鲁迅」。不要署名就传空字符串 |
| `--subtitle` | 副题，可空 |
| `--motif` | `lattice` 窗格、`cloud` 云头、`frame` 角框、`meander` 回纹 |
| `--palette` | `cinnabar` 朱砂（默认）、`ochre` 赭黄、`indigo` 暗蓝、`ink` 纯墨 |
| `--layout` | `auto`、`vertical`、`horizontal`。auto 时窗格和角框直排，云头和回纹横排 |
| `--seed` | 整数。相同种子得到相同 SVG |
| `--outline-text` / `--no-outline-text` | 默认把汉字转成轮廓。关掉之后写 `<text>`，依赖查看器字体 |
| `--out` | 输出的 `.svg` 路径 |
| `--png` | 同时写 PNG。需要可选依赖，见下 |

PNG 不是 v0.1 的默认能力。需要时：

```bash
pip install 'luxun-cover-skill[png]'
luxun-cover --title 彷徨 --out panghuang.svg --png
```

系统要有 cairo。没有的话，用浏览器打开 SVG 即可。

## 示例

下面三张都是本工具画的致敬构图，不是历史封面的扫描或复刻。预览 PNG 只为了在 README 里能看见；以 SVG 为准。

### 彷徨

赭黄纸，朱红书口，窗格在左下，书名直排在右上。

![彷徨致敬构图](examples/panghuang.png)

```bash
luxun-cover --title 彷徨 --author 鲁迅 --palette ochre --motif lattice --layout vertical --seed 0 --out examples/panghuang.svg
```

### 呐喊

纯墨。上端一条云头边饰，书名落在下方双线之间。这不是 1923 年那张红地黑块的初版封面。

![呐喊致敬构图](examples/nahan.png)

```bash
luxun-cover --title 呐喊 --author 鲁迅 --palette ink --motif cloud --layout horizontal --seed 1 --out examples/nahan.svg
```

### 野草

暗蓝书口，角框，书名直排。这不是孙福熙那张山水封面。

![野草致敬构图](examples/yecao.png)

```bash
luxun-cover --title 野草 --author 鲁迅 --palette indigo --motif frame --layout vertical --seed 1 --out examples/yecao.svg
```

回纹可以这样试：

```bash
luxun-cover --title 呐喊 --palette cinnabar --motif meander --layout horizontal --seed 1 --out nahan-meander.svg
```

## 给 Agent

仓库根目录的 [SKILL.md](SKILL.md) 是给编程代理的操作说明：什么时候用、什么时候停、怎么选色板和纹样、生成之后按什么清单自检。

视觉规则的细目在 [docs/aesthetic.md](docs/aesthetic.md)。历史参照和版权在 [docs/references.md](docs/references.md)。

## 测试

```bash
python -m unittest discover -s tests
```

## 许可与致敬

[MIT](LICENSE)。

几何纹样是程序里算出来的，不是从陶元庆的画上描的。不要把输出叫成《彷徨》原封面。陶元庆卒于 1929 年，各国版权期限不同，后世扫描也可能另有权利。稳妥的用法是学语法，不复制画面。详见 [docs/references.md](docs/references.md)。
