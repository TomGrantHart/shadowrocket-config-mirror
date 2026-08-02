# Shadowrocket 配置镜像仓库

把 [yfamilys 配置一](https://yfamilys.com/config/shadowrocket_basic.conf) 镜像到自己的 GitHub 仓库，由 GitHub Actions **每天自动同步**上游更新，Shadowrocket 订阅本仓库的 raw 链接即可。自定义规则通过独立模块叠加，永不受配置更新影响。

## 仓库结构

```
shadowrocket-config-mirror/
├── .github/workflows/sync-upstream.yml   # 每日定时同步 workflow
├── shadowrocket_basic.conf                # 镜像文件（由 Actions 覆盖更新，勿手动改）
├── custom_ad_block.sgmodule               # 自定义广告拦截模块（你自己的，不受上游影响）
└── README.md
```

## 工作原理

```
上游 yfamilys.com  ──(每天 CST 02:00)──▶  GitHub Actions 下载覆盖  ──▶  本仓库 shadowrocket_basic.conf
                                                                              │
                                                              raw 链接  ──────┴─────▶  Shadowrocket 订阅刷新
                                                                                      │
                                                              custom_ad_block.sgmodule ─▶ 模块叠加自定义规则
```

- **主配置层**：本仓库 `shadowrocket_basic.conf` 每日跟随上游，Shadowrocket 订阅 raw 链接即可拿到最新结构。
- **自定义规则层**：`custom_ad_block.sgmodule` 是你自己的模块，在 Shadowrocket 里启用，规则优先级高于配置，上游怎么更新都不影响它。
- **外部 list 层**：配置里引用的 ~30 个 `RULE-SET`（yfamilys.com/rule/*.list）Shadowrocket 订阅时会实时拉取最新版，无需镜像，属于准实时更新。

## 使用步骤

### 1. 创建并推送仓库

```bash
cd shadowrocket-config-mirror
git init
git add .
git commit -m "init: shadowrocket config mirror"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

### 2. 确认 Actions 已启用

GitHub 仓库 → Settings → Actions → General → 确认 "Allow all actions"，Workflow permissions 选 **Read and write**。

推送后 `sync-upstream.yml` 会自动出现。可手动跑一次验证：Actions → Sync Upstream Config → Run workflow。

### 3. Shadowrocket 订阅本仓库链接

```
配置 → 右上角 ➕ → 粘贴链接 → 类型选「配置」→ 下载
https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/shadowrocket_basic.conf
```

订阅后建议在配置项里设「自动更新」周期（如每天），Shadowrocket 会自动拉最新版。

### 4. 安装自定义规则模块

`custom_ad_block.sgmodule` 也托管在本仓库，两种装法：

- **URL 安装（推荐）**：配置 → 模块 → 右上角 ➕ → 填下面链接 → 下载
  ```
  https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/custom_ad_block.sgmodule
  ```
- **本地导入**：把 `custom_ad_block.sgmodule` 文件传到手机，配置 → 模块 → ➕ → 从文件导入。

模块和配置是分离的，互不影响。

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

### 加 / 改自定义规则

只改 `custom_ad_block.sgmodule` 的 `[Rule]` 段，commit 后在 Shadowrocket 模块页点更新即可，**完全不用碰配置文件**。

## 注意事项

- 上游配置第 90 行 `#RULE-SET,...AntiAD.list,REJECT` 是被注释的（AntiAD 广告拦截实际未启用）。本仓库是**纯镜像**，不篡改上游内容。如需启用，可在 `custom_ad_block.sgmodule` 模块里自行加一条 `RULE-SET,https://yfamilys.com/rule/AntiAD.list,REJECT`。
- GitHub raw 链接有缓存（约 5 分钟），Actions 推送后稍等再刷新订阅。
- 仓库设为 public，raw 链接才能被 Shadowrocket 直接访问；private 仓库需配 token，不推荐。
- Actions 免费额度对个人公开仓库无限，每天跑一次毫无压力。
