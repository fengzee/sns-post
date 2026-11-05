# sns-post

把一件事做成小红书或抖音的帖子、图文与视频。这是一份给 AI agent 用的技能，也适合人直接照着做。

A skill for turning one finished project into ready-to-publish Xiaohongshu and Douyin posts: copy, 3:4 cards, vertical video, covers, safe areas and pre-publish checks.

## 里面有什么

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 主流程：定角度、写作原则、两渠道规格、素材目录、卡片与视频管线、安全区、平台规则、发布前检查 |
| `references/writing.md` | 通用文案规范、中文标点和小红书文案的完整要求 |
| `scripts/gen_cards.py` | 1080×1440 卡片生成器模板：HTML 排版、Chrome headless 截图、溢出检查 |
| `scripts/render_cards.sh` | 调用生成器的 shell 入口 |

技能覆盖的几条主线：

- 动笔前先定角度。过程向讲经过，结果向直接摆发现，两种都不写成报告的通俗版。
- 读者分两层。普通人看得懂，内行挑不出错；保留几处靠常识就能懂的工程细节。
- 不写成吹捧。留下 AI 出错、结论被推翻的部分，或者用结果本身的反差。
- 两个渠道各自独立。同一内容共用一套素材与生成器，各渠道按自己的画布和安全区出成品。
- 图卡、视频、封面都有可执行的尺寸与检查方法，不靠肉眼估。
- 发布前查隐私、平台规则和 AI 内容声明。

## 安装

克隆到你的 agent 技能目录。常见的几个位置：

```sh
# 跨框架技能库
git clone https://github.com/fengzee/sns-post.git ~/.agents/skills/sns-post

# Claude Code
git clone https://github.com/fengzee/sns-post.git ~/.claude/skills/sns-post

# 项目内
git clone https://github.com/fengzee/sns-post.git .claude/skills/sns-post
```

`SKILL.md` 带 `name` 和 `description` 的 frontmatter，按各框架的技能加载约定读取即可。不依赖特定 agent，直接读 Markdown 也能用。

## 用法

对 agent 说：

> 把这次排查做成小红书和抖音的帖子。
>
> 这篇内容要发小红书，先定角度再写标题和正文。
>
> 这组数据做成 6 张 3:4 图卡，最后检查文字有没有溢出。

做视频或图卡时，先把模板复制到帖子目录，再改内容：

```sh
mkdir -p posts/sns-example-2026-01-01/build
cp scripts/gen_cards.py posts/sns-example-2026-01-01/build/gen.py
cp scripts/render_cards.sh posts/sns-example-2026-01-01/build/render.sh
cd posts/sns-example-2026-01-01
build/render.sh              # 重出全部
build/render.sh cover        # 只出封面
CHECK=1 build/render.sh      # 只测高度，不出图
```

生成器默认输出到 `out/xiaohongshu/`，可以用 `OUT_DIR` 改。Chrome 路径可用 `CHROME` 指定。

## 依赖

- 图卡：Chrome 或 Chromium；溢出检查需要 Pillow（`python3 -m pip install pillow`）。
- 视频：ffmpeg、Playwright，按需 rubberband、whisper、demucs。
- 核对：ffprobe、ImageMagick。

脚本按 macOS 和 Linux 的常见路径查找 Chrome，其他环境设置 `CHROME`。

## 关于数字

安全区、画布比例、字数限制和码率来自 2026 年对主流机型和平台公开规范的实测与推算。平台会改版，机型会更新，用之前按当次设备复测一遍。`SKILL.md` 里标了哪些是官方规范、哪些是实测结论。

## 许可

MIT，见 [LICENSE](LICENSE)。可以自由使用、修改和分发，保留版权声明即可。
