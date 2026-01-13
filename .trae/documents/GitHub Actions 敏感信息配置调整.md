# GitHub Actions 配置方案

您的做法非常正确，敏感信息确实不应该直接写入代码或提交到仓库中。`.env` 文件已经在 `.gitignore` 中被忽略，因此不会被上传，但为了确保 GitHub Actions 能正常工作，我们需要更新 workflow 文件以支持新的环境变量配置。

## 核心原则
1.  **本地开发**：使用 `.env` 文件（不提交到 Git）。
2.  **GitHub Actions**：使用 GitHub Secrets 注入环境变量。

## 执行计划

### 1. 确认 .gitignore 配置
检查发现 `.env` 已经被包含在 `.gitignore` 中，这意味着您本地创建的 `.env` 文件是安全的，**不会**被 git 追踪或上传。您可以在本地保留它用于测试。

### 2. 更新 GitHub Workflow 文件
我需要修改 `.github/workflows/daily_fetch.yml`，在环境变量部分添加 `OPENAI_BASE_URL`，以支持自定义 API 地址。

当前配置：
```yaml
    - name: Fetch Data and Generate Markdown
      env:
        PRODUCTHUNT_CLIENT_ID: ${{ secrets.PRODUCTHUNT_CLIENT_ID }}
        PRODUCTHUNT_CLIENT_SECRET: ${{ secrets.PRODUCTHUNT_CLIENT_SECRET }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        PRODUCTHUNT_DEVELOPER_TOKEN: ${{ secrets.PRODUCTHUNT_DEVELOPER_TOKEN }}
      run: python scripts/product_hunt_list_to_md.py
```

修改后：
```yaml
    - name: Fetch Data and Generate Markdown
      env:
        PRODUCTHUNT_CLIENT_ID: ${{ secrets.PRODUCTHUNT_CLIENT_ID }}
        PRODUCTHUNT_CLIENT_SECRET: ${{ secrets.PRODUCTHUNT_CLIENT_SECRET }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        OPENAI_BASE_URL: ${{ secrets.OPENAI_BASE_URL }}  # 新增
        PRODUCTHUNT_DEVELOPER_TOKEN: ${{ secrets.PRODUCTHUNT_DEVELOPER_TOKEN }}
      run: python scripts/product_hunt_list_to_md.py
```

### 3. 清理本地敏感文件 (可选)
如果您担心误操作，我可以帮您删除本地的 `.env` 文件，只保留 `.env.example`。

## 您需要在 GitHub 上执行的操作
代码更新后，请前往您的 GitHub 仓库：
1.  点击 **Settings** -> **Secrets and variables** -> **Actions**。
2.  点击 **New repository secret**，添加以下变量：
    -   `OPENAI_API_KEY`
    -   `OPENAI_BASE_URL` (如果使用自定义接口)
    -   `PRODUCTHUNT_CLIENT_ID`
    -   `PRODUCTHUNT_CLIENT_SECRET`
    -   `PRODUCTHUNT_DEVELOPER_TOKEN`

我将立即为您更新 workflow 文件。
