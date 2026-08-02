# Shadowrocket 配置镜像仓库

把 [yfamilys 配置一](https://yfamilys.com/config/shadowrocket_basic.conf) 镜像到自己的 GitHub 仓库，由 GitHub Actions **每天自动同步**上游更新，并自动注入自定义规则生成最终配置。Shadowrocket 订阅一个链接即可，自定义规则永不受上游更新影响。

## 仓库结构

```
shadowrocket-config-mirror/
├── .github/workflows/sync-upstream.yml   # 每日定时同步 + 注入 workflow
├── shadowrocket_basic.conf                # 上游纯镜像（Actions 覆盖更新，勿手动改）
├── shadowrocket_final.conf                # 最终配置 = basic + 注入 RULE-SET（Actions 生成，订阅这个）
├── custom_reject.list                     # 自定义 REJECT 规则源（增删规则只改这里）
├── scripts/merge.py                       # 注入脚本：basic → final
├── custom_ad_block.sgmodule               # 可选：模块版自定义规则（与 list 内容相同，二选一）
├── .gitattributes                         # 强制 LF 行尾
└── README.md
```

## 工作原理

```
上游 yfamilys  ──(每天 CST 02:00 Actions)──▶  basic.conf  ──(merge.py 注入)──▶  final.conf
                                                                                 │
custom_reject.list  ◀── 增删规则只改这里                                        │ raw 链接
      └──────────── RULE-SET 引用 ────────────────────────────────────────────┘
                                                                    ▼
                                                          Shadowrocket 订阅 final.conf
```

- **basic.conf**：上游的纯镜像，Actions 每天覆盖，保持原样不篡改。
- **final.conf**：merge.py 在 basic 的 `[Rule]` 段开头注入一行 `RULE-SET,<custom_reject.list 链接>,REJECT` 后生成。自定义规则排在所有上游规则之前，优先匹配。
- **custom_reject.list**：你的自定义规则源（纯规则列表，每行 `类型,值`，策略由 RULE-SET 行统一指定为 REJECT）。改规则只改这里，Actions 会自动重新生成 final.conf。
- **外部 list 层**：配置里引用的上游 ~30 个 `RULE-SET`（yfamilys.com/rule/*.list）Shadowrocket 订阅时实时拉最新，无需镜像。

## Shadowrocket 订阅

**只需订阅一个链接**（配置 → 右上角 ➕ → 粘贴链接 → 类型选「配置」→ 下载）：

```
https://raw.githubusercontent.com/TomGrantHart/shadowrocket-config-mirror/main/shadowrocket_final.conf
```

订阅后建议在配置项里设「自动更新」周期（如每天），Shadowrocket 会自动拉最新版。自定义规则已通过 final.conf 里的 RULE-SET 引用生效，**无需再单独装模块**。

## 增删自定义规则

只改 `custom_reject.list`，commit 后 Actions 下次运行会自动重新生成 final.conf。想立即生效，手动触发一次 workflow：Actions → Sync Upstream Config → Run workflow。

每行格式 `类型,值`，例如：
```
DOMAIN-SUFFIX,example.com
DOMAIN-KEYWORD,ads
```

## 自定义

### 改同步频率

编辑 `.github/workflows/sync-upstream.yml` 的 cron：

| 频率 | cron (UTC) | 对应 CST |
|------|-----------|---------|
| 每天 1 次 | `0 18 * * *` | 次日 02:00 |
| 每 6 小时 | `0 */6 * * *` | 每 6 小时 |
| 每小时 | `0 * * * *` | 每小时 |

### 改上游源

改 workflow 里的 `UPSTREAM_URL` 即可镜像别的配置。

### 模块方案（可选）

`custom_ad_block.sgmodule` 是等价的自定义规则模块。如果你更想用「配置 + 模块」分离的方案，订阅 `shadowrocket_basic.conf` 再装这个模块即可。与 final.conf 方案**二选一**，不要同时用（规则会重复）。

## 注意事项

- 上游配置的 `#RULE-SET,...AntiAD.list,REJECT` 是注释状态（AntiAD 广告拦截未启用）。basic.conf 保持纯镜像不篡改。如需启用，在 `custom_reject.list` 里加一行 `RULE-SET,https://yfamilys.com/rule/AntiAD.list`（策略由 final.conf 的 RULE-SET 行指定为 REJECT，list 内不带策略）。
- GitHub raw 链接有约 5 分钟缓存，Actions 推送后稍等再刷新订阅。
- 仓库须为 public，raw 链接才能被 Shadowrocket 直接访问。
- Actions 对个人公开仓库免费无限，每天跑一次毫无压力。
