#!/usr/bin/env python3
# 把上游镜像 shadowrocket_basic.conf 注入自定义 RULE-SET 后生成 shadowrocket_final.conf
# 注入位置：[Rule] 段标签行之后（所有规则之前），使自定义 REJECT 优先匹配
import io
import os

BASIC = "shadowrocket_basic.conf"
FINAL = "shadowrocket_final.conf"

# 仓库地址由 GitHub Actions 注入；本地运行时用默认值
REPO = os.environ.get("GITHUB_REPOSITORY", "TomGrantHart/shadowrocket-config-mirror")
CUSTOM_LIST_URL = f"https://raw.githubusercontent.com/{REPO}/main/custom_reject.list"

INJECT = (
    "# === 自定义规则（自动注入，勿手动编辑 final.conf）===\n"
    f"RULE-SET,{CUSTOM_LIST_URL},REJECT\n"
    "# === 自定义规则结束 ===\n"
)

with io.open(BASIC, encoding="utf-8") as f:
    content = f.read()

if "[Rule]" in content:
    idx = content.index("[Rule]")
    nl = content.index("\n", idx) + 1
    content = content[:nl] + INJECT + content[nl:]
else:
    content = content.rstrip("\n") + "\n\n[Rule]\n" + INJECT

with io.open(FINAL, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print(f"已生成 {FINAL}")
print(f"注入 RULE-SET -> {CUSTOM_LIST_URL}")
