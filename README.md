# token-relay-list

Token 中转平台导航页，按 `relay`、`source`、`github` 三类展示平台，并定期检查可访问性。GitHub Action 会在更新数据后单独部署到 Cloudflare Pages。

## 目录说明

- `data/all_platforms.json`：平台源数据，手工维护。
- `data/checked.json`：检查脚本生成的最新状态数据。
- `src/index.html`：前端页面，读取 `src/data/checked.json` 渲染列表。
- `scripts/check_platforms.py`：检查平台是否可访问。
- `scripts/build_seo.py`：生成 `src/sitemap.xml` 和 `src/robots.txt`。
- `.github/workflows/update.yml`：GitHub Action 自动更新与部署流程。

## 怎么更新平台状态

平台状态不是手工改的，而是脚本检查后生成的。

本地更新方式：

```bash
python3 scripts/check_platforms.py
cp data/checked.json src/data/
python3 scripts/build_seo.py
```

如果只是让前端显示最新结果，核心是更新 `data/checked.json`，再同步到 `src/data/checked.json`。`src/index.html` 读取的是 `src/data/checked.json`。

## 怎么添加新的中转站

新的平台统一加到 `data/all_platforms.json`。

每一项至少包含这四个字段：

```json
{
  "name": "平台名称",
  "url": "https://example.com",
  "desc": "简短说明",
  "type": "relay"
}
```

`type` 目前支持：

- `relay`：中转平台
- `source`：源头模型平台
- `github`：开源自建项目

添加完以后，重新执行：

```bash
python3 scripts/check_platforms.py
cp data/checked.json src/data/
python3 scripts/build_seo.py
```

## GitHub Action 怎么配置

当前工作流在 `.github/workflows/update.yml`。

它做的事情是：

1. 每天自动触发一次。
2. 也支持手动触发。
3. 安装 Python 依赖。
4. 运行 `scripts/check_platforms.py` 生成最新 `checked.json`。
5. 复制数据到 `src/data/`。
6. 运行 `scripts/build_seo.py` 生成 `sitemap.xml` 和 `robots.txt`。
7. 如果文件有变化，就提交并推送回仓库。
8. 通过 `cloudflare/pages-action` 单独部署 `src/` 目录。

### 维护方式

推荐的日常流程是：

1. 更新 `data/all_platforms.json` 或运行检查脚本。
2. 生成最新的 `data/checked.json` 和 `src/data/checked.json`。
3. 运行 `scripts/build_seo.py` 更新 `sitemap.xml` 和 `robots.txt`。
4. 提交并 push 到 GitHub。
5. 让 GitHub Action 触发 Cloudflare Pages 部署。

### 站点地址

当前正式域名是：

```text
https://token.waitli.top
```

这个地址同时用于：

- 页面 canonical
- `robots.txt`
- `sitemap.xml`
- GitHub Action 里的 `SITE_URL`

如果以后换域名，需要同步改这些位置：

- `src/index.html`
- `scripts/build_seo.py`
- `.github/workflows/update.yml`
- `src/robots.txt`
- `src/sitemap.xml`

## 本地依赖

脚本只依赖 `requests`：

```bash
pip install requests
```
