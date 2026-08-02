#!/usr/bin/env python3
# 把上游镜像 shadowrocket_basic.conf 注入自定义规则后生成 shadowrocket_final.conf
# 三步处理：
#   1. URL 替换：所有 yfamilys.com/rule/*.list -> 仓库 RULE/*.list（自托管）
#   2. 在 [Proxy Group] 段注入「自定义」策略组（供 RULE-SET 引用）
#   3. 在 [Rule] 段注入 RULE-SET,<custom_reject.list>,自定义（优先匹配）
import io
import os

BASIC = "shadowrocket_basic.conf"
FINAL = "shadowrocket_final.conf"

REPO = os.environ.get("GITHUB_REPOSITORY", "TomGrantHart/shadowrocket-config-mirror")
RULE_BASE = f"https://raw.githubusercontent.com/{REPO}/main/RULE"
CUSTOM_LIST_URL = f"https://raw.githubusercontent.com/{REPO}/main/custom_reject.list"

# 「自定义」策略组：可选 REJECT / DIRECT / 各分流策略组，用户在 Shadowrocket 手动选
CUSTOM_GROUP = (
    "自定义 = select, REJECT, DIRECT, 🚀 策略选择, 🌐 全球直连, "
    "🤖️ 人工智能, 📲 Telegram, 📹 YouTube, 🎥 Netflix, 🎬 Disney+, 🎻 Spotify, "
    "📄 Twitter, 🪙 Paypal, 👤 Facebook, 📖 Reddit, 🐦 Discord, 📽 哔哩哔哩, "
    "🍿 国外媒体, 🍔 国内媒体, 🍟 新浪微博, Ⓜ️ 微软服务, 🍎 苹果服务, 🎮 游戏平台\n"
)

INJECT_RULE = (
    "# === 自定义规则（自动注入，勿手动编辑 final.conf）===\n"
    f"RULE-SET,{CUSTOM_LIST_URL},自定义\n"
    "# === 自定义规则结束 ===\n"
)

with io.open(BASIC, encoding="utf-8") as f:
    content = f.read()

# 1. URL 替换：yfamilys list -> 仓库自托管 RULE/
content = content.replace("https://yfamilys.com/rule/", RULE_BASE + "/")

# 2. 在 [Proxy Group] 段开头注入「自定义」策略组
if "[Proxy Group]" in content:
    idx = content.index("[Proxy Group]")
    nl = content.index("\n", idx) + 1
    content = content[:nl] + CUSTOM_GROUP + content[nl:]

# 3. 在 [Rule] 段开头注入自定义 RULE-SET
if "[Rule]" in content:
    idx = content.index("[Rule]")
    nl = content.index("\n", idx) + 1
    content = content[:nl] + INJECT_RULE + content[nl:]
else:
    content = content.rstrip("\n") + "\n\n[Rule]\n" + INJECT_RULE

with io.open(FINAL, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print(f"已生成 {FINAL}")
print(f"  1) URL 替换 -> {RULE_BASE}/")
print(f"  2) 注入策略组「自定义」")
print(f"  3) 注入 RULE-SET -> {CUSTOM_LIST_URL}")
