#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3:4 卡片生成器模板（1080×1440）。

用法：
    python3 gen_cards.py            重出全部卡片
    python3 gen_cards.py cover      只出单张（卡名或文件名都可以）
    CHECK=1 python3 gen_cards.py    只测内容高度是否溢出，不出图

复制到帖子目录的 build/gen.py 后使用，配色、cards、ORDER 都按帖子改。
输出目录默认 out/xiaohongshu/，可用 OUT_DIR 覆盖。
"""

import os
import shutil
import signal
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.environ.get("OUT_DIR", os.path.join(ROOT, "out", "xiaohongshu"))

CARD_W, CARD_H = 1080, 1440
SAFE_BOTTOM = 1330          # 内容底边上限，超过就会被页脚或裁切吃掉
BG = (243, 242, 238)        # 与 CSS 里的页面底色一致，溢出检查用
FOOT = '<div class="foot"><span>系列名 · YYYY-MM-DD</span><span>{{N}} / {{TOTAL}}</span></div>'

CSS = """
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#F3F2EE}
body{width:1080px;height:1440px;overflow:hidden;font-family:"PingFang SC","Hiragino Sans","Noto Sans CJK SC",sans-serif;color:#1B1F24;font-size:30px;line-height:1.5;-webkit-font-smoothing:antialiased;text-wrap:pretty}
.card{width:1080px;height:1440px;padding:64px 64px 110px;position:relative;display:flex;flex-direction:column}
.kicker{font-size:25px;color:#C8412B;letter-spacing:.1em;margin-bottom:14px;font-weight:600}
h1{font-size:56px;line-height:1.22;margin:0 0 22px;font-weight:700;letter-spacing:-.015em}
.lead{font-size:32px;color:#3D4247;line-height:1.6;margin-bottom:26px}
.foot{position:absolute;left:64px;right:64px;bottom:40px;font-size:22px;color:#8A8F95;display:flex;justify-content:space-between}

/* 深色封面：首帧就是封面，不淡入 */
.dark{width:1080px;height:1440px;background:#14181D;position:relative;overflow:hidden;padding:0}
.dark .top{position:absolute;left:64px;top:66px;font-size:25px;color:#F0A58F;letter-spacing:.1em;font-weight:600}
.dark .pill{position:absolute;right:64px;top:60px;font-size:23px;color:#14181D;background:#F0A58F;padding:8px 20px;border-radius:999px;font-weight:600}
.dark .inner{position:absolute;left:64px;right:64px;top:250px;color:#fff}
.dark h1{font-size:104px;line-height:1.1;color:#fff;margin:0 0 30px;letter-spacing:-.02em}
.dark .sub{font-size:33px;color:#B9C2CB;line-height:1.55}
.dark .foot{color:#6E7780}

/* 白卡与要点 */
.box{background:#fff;border:2px solid #E1DFD9;border-radius:18px;padding:28px 32px;margin-bottom:22px}
.box .h{font-size:24px;font-weight:700;letter-spacing:.06em;color:#C8412B;margin-bottom:10px}
.box p{font-size:32px;line-height:1.6;margin:0}
.li{display:flex;gap:22px;align-items:flex-start;padding:26px 0;border-top:1px solid #E1DFD9}
.li:last-of-type{border-bottom:1px solid #E1DFD9}
.li .ic{width:64px;height:64px;flex:none;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;color:#fff;background:#C8412B;margin-top:4px}
.li b{display:block;font-size:34px;line-height:1.3;margin-bottom:6px}
.li span{font-size:29px;color:#3D4247;line-height:1.55}
.note{margin-top:auto;border-left:8px solid #C8412B;background:#fff;padding:24px 28px;border-radius:0 16px 16px 0;font-size:30px;line-height:1.55}
.note b{color:#C8412B}
code{font-family:"SF Mono",ui-monospace,Menlo,monospace;font-size:.92em;background:#EBE9E4;padding:2px 8px;border-radius:6px}
"""


def page(body):
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


cards = {}

cards["cover"] = page(f"""<div class="dark">
<div class="top">系列名 · 一句话说明主题</div>
<div class="pill">YYYY-MM-DD</div>
<div class="inner">
<h1>示例标题<br>两行以内<br>写结论</h1>
<div class="sub">副标题一句话交代读者能得到什么。这张封面承担全部点击率，标题和主图一起放在视觉中心。</div>
</div>
{FOOT}</div>""")

cards["point"] = page(f"""<div class="card">
<div class="kicker">一个小标题</div>
<h1>一张卡只讲一件事</h1>
<div class="box"><div class="h">先给场景</div>
<p>用一两句话交代读者为什么要往下看，例如一个具体的时间、地点或一次意外结果。</p></div>
<div class="li"><div class="ic">1</div><div><b>要点写结论</b><span>每条一句话，句子里的数字前后留空格，例如 3 次、50 米、20%。</span></div></div>
<div class="li"><div class="ic">2</div><div><b>解释只留必要的</b><span>读者不懂的过程性细节放进素材目录，不上卡片。</span></div></div>
<div class="li"><div class="ic">3</div><div><b>一张卡一个重点</b><span>放不下就拆成两张，不要缩字号硬塞。</span></div></div>
<div class="note"><b>页脚一行</b>　写系列名与页码，和封面保持一致。</div>
{FOOT}</div>""")

cards["end"] = page(f"""<div class="card">
<div class="kicker">结尾</div>
<h1>读者能带走什么</h1>
<p class="lead">结尾停在具体的事上，不写口号，也不写「你怎么看」之类的呼吁。</p>
<div class="box"><div class="h">一句可执行的建议</div>
<p>或者留一个入口：原始数据、复现方法、代码仓库，按平台规则决定放不放链接。</p></div>
<div class="note"><b>别忘了</b>　用了 AI 生成的画面、配音或配乐，正文和发布页都要声明。</div>
{FOOT}</div>""")

ORDER = ["cover", "point", "end"]

# 深色封面的背景不是 BG，跳过自动溢出检查
SKIP_CHECK = {"cover"}


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    sys.exit("找不到 Chrome，设置 CHROME 环境变量指向可执行文件。")


CHROME = find_chrome()


def shot(html_path, png_path, height=CARD_H, max_wait=60):
    cmd = [
        CHROME, "--headless", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars",
        "--disable-extensions", "--user-data-dir=" + os.path.join(BUILD, "chrome-profile"),
        f"--window-size={CARD_W},{height}", "--force-device-scale-factor=1",
        "--screenshot=" + png_path, "file://" + html_path,
    ]
    if os.path.exists(png_path):
        os.remove(png_path)
    proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    # Chrome 截完图不一定退出；等文件大小连续稳定三次就收工
    started = time.time()
    stable, last = 0, -1
    while time.time() - started < max_wait:
        if os.path.exists(png_path):
            size = os.path.getsize(png_path)
            stable = stable + 1 if size > 0 and size == last else 0
            last = size
            if stable >= 3:
                break
        time.sleep(0.3)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        # 进程可能已经退出，或进程组已被回收
        try:
            proc.kill()
        except Exception:
            pass
    proc.wait()
    return os.path.exists(png_path)


def check_height(name, fname, html):
    from PIL import Image

    html = html.replace(
        "</head>",
        "<style>body{height:auto;overflow:visible}"
        ".card{height:auto;min-height:1440px}.foot{display:none}</style></head>",
    )
    hp = os.path.join(BUILD, f"check-{fname}.html")
    png = os.path.join(BUILD, f"check-{fname}.png")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(html)
    if not shot(hp, png, height=2400):
        print(f"{fname}: 渲染失败")
        return
    im = Image.open(png).convert("RGB")
    width, height = im.size
    px = im.load()
    last_row = 0
    for y in range(height):
        if any(
            abs(px[x, y][0] - BG[0]) + abs(px[x, y][1] - BG[1]) + abs(px[x, y][2] - BG[2]) > 18
            for x in range(0, width, 4)
        ):
            last_row = y
    status = "OK" if last_row <= SAFE_BOTTOM else f"OVERFLOW by {last_row - SAFE_BOTTOM}"
    print(f"{fname}: content bottom {last_row}px  {status}")
    os.remove(png)
    os.remove(hp)


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    check = os.environ.get("CHECK") == "1"
    os.makedirs(BUILD, exist_ok=True)
    if not check:
        os.makedirs(OUT, exist_ok=True)

    names = [(key, f"{i:02d}-{key}") for i, key in enumerate(ORDER, 1)]
    for key, fname in names:
        if only and key not in only and fname not in only:
            continue
        html = cards[key].replace("{{N}}", str(int(fname[:2]))).replace("{{TOTAL}}", str(len(ORDER)))
        if check:
            if key in SKIP_CHECK:
                continue
            check_height(key, fname, html)
        else:
            hp = os.path.join(BUILD, f"{fname}.html")
            with open(hp, "w", encoding="utf-8") as f:
                f.write(html)
            ok = shot(hp, os.path.join(OUT, f"{fname}.png"))
            print(fname, "ok" if ok else "FAIL")


if __name__ == "__main__":
    main()
