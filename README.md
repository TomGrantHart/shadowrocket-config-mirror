# Shadowrocket 配置镜像仓库（全自托管）

把 [yfamilys 配置一](https://yfamilys.com/config/shadowrocket_basic.conf) 镜像到自己的 GitHub 仓库，由 GitHub Actions **每天自动同步**上游配置 + RULE/ 下所有规则文件，并自动注入自定义策略组与规则，生成最终配置。Shadowrocket 订阅一个链接即可，**所有 RULE-SET 全部指向本仓库自托管的 RULE/**，不再依赖 yfamilys 的 list 服务器。

## 仓库结构

```
shadowrocket-config-mirror/
├── .github/workflows/sync-upstream.yml   # 每日同步 basic + RULE/ + 生成 final
├── shadowrocket_basic.conf                # 上游纯镜像（Actions 覆盖，勿手改）
├── shadowrocket_final.conf                # 最终配置（Actions 生成，订阅这个）
├── custom_reject.list                     # 自定义规则源（增删规则只改这里）
├── RULE/                                  # 自托管的所有规则 list（34 个，Actions 同步）
│   ├── ai.list  Apple.list  Netflix.list  ...  AntiAD.list(27万行) ...
├── scripts/merge.py                       # 注入脚本：basic → final
├── custom_ad_block.sgmodule               # 可选模块版（与 list 二选一）
├── .gitattributes
└── README.md
```

## 工作原理

```
上游 yfamilys ──(每天 02:00 Actions)──▶ basic.conf
                      │
                      ├──▶ RULE/*.list（34 个 list 全部镜像到本地，自托管）
                      │
basic.conf + RULE/ ──(merge.py)──▶ final.conf
   ├─ ① URL 替换：yfamilys.com/rule/* → 本仓库 RULE/*
   ├─ ② [Proxy Group] 注入「自定义」策略组
   └─ ③ [Rule] 注入 RULE-SET,<custom_reject.list>,自定义
                      │
                      ▼ raw 链接
              Shadowrocket 订阅 final.conf
```

- **basic.conf**：上游纯镜像，每天覆盖。
- **RULE/**：上游引用的 34 个 list 全部镜像到本地，Actions 每天重新下载同步。final.conf 里所有 RULE-SET 指向本仓库的 RULE/，**yfamilys 的 list 服务器挂了也不影响你**。
- **final.conf**：merge.py 三步处理后的最终配置。
- **custom_reject.list**：你的自定义规则源，策略统一走「自定义」策略组。
- **「自定义」策略组**：在 [Proxy Group] 注入，可选 REJECT / DIRECT / 各分流策略组。当前广告规则建议在 Shadowrocket 里把「自定义」组选为 REJECT；后期加非广告规则时，可按需改选其他策略。

## Shadowrocket 订阅

**只需订阅一个链接**（配置 → 右上角 ➕ → 粘贴链接 → 类型选「配置」→ 下载）：

```
https://raw.githubusercontent.com/TomGrantHart/shadowrocket-config-mirror/main/shadowrocket_final.conf
```

订阅后，到「代理分组」里找到「自定义」策略组，按当前需求选 REJECT（广告拦截）。

## 增删自定义规则

只改 `custom_reject.list`（每行 `类型,值`），commit 后下次 Actions 自动重新生成 final.conf。规则统一走「自定义」策略组，在 Shadowrocket 里改该组的策略即可批量切换。

## 自定义

### 改同步频率

编辑 `.github/workflows/sync-upstream.yml` 的 cron：

| 频率 | cron (UTC) | 对应 CST |
|------|-----------|---------|
| 每天 1 次 | `0 18 * * *` | 次日 02:00 |
| 每 6 小时 | `0 */6 * * *` | 每 6 小时 |

### 改上游源

改 workflow 里的 `UPSTREAM_URL`。

## 注意事项

- `RULE/AntiAD.list` 约 27 万行（数 MB），首次 clone/订阅加载稍慢，属正常。该 list 在上游配置里是被注释的，如需启用可在 `custom_reject.list` 加 `RULE-SET,https://raw.githubusercontent.com/TomGrantHart/shadowrocket-config-mirror/main/RULE/AntiAD.list`。
- GitHub raw 有约 5 分钟缓存，Actions 推送后稍等再刷新订阅。
- 仓库须为 public，raw 链接才能被 Shadowrocket 直接访问。
- 上游新增/删除 list 时，Actions 的 RULE/ 同步步骤会自动跟着 basic.conf 里引用的 URL 增删对应文件（旧文件不会自动删，需手动清理或偶尔重置 RULE/）。
