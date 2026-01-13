# Product Hunt 内容中文化方案

根据代码分析，项目目前已经内置了使用 OpenAI 进行翻译的功能，但可能因为缺少配置导致没有生效。

## 现状分析
1.  **现有代码支持翻译**：`scripts/product_hunt_list_to_md.py` 文件中已经包含了 `translate_text` 方法，使用 `gpt-4o-mini` 模型将 `tagline`（标语）和 `description`（描述）翻译成中文。
2.  **配置缺失**：代码依赖 `OPENAI_API_KEY` 环境变量来启用翻译功能。如果没有设置该环境变量，代码会打印警告并直接返回英文原文。
3.  **关键词生成**：代码同样使用 OpenAI 生成中文关键词，如果未配置 API Key，会使用简单的分词作为备用方案。

## 解决方案

不需要重新开发，只需要配置正确的环境变量即可启用翻译功能。

### 步骤 1：准备 OpenAI API Key
您需要一个有效的 OpenAI API Key（或其他兼容 OpenAI 格式的 API Key，如 DeepSeek、Moonshot 等，如果使用非 OpenAI 官方 API，可能需要修改 `base_url`）。

### 步骤 2：配置环境变量
由于您是在本地运行（或通过 GitHub Actions 运行），有两种配置方式：

**方式 A：本地运行 (使用 .env 文件)**
1.  在项目根目录创建一个名为 `.env` 的文件。
2.  在文件中添加以下内容：
    ```env
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    PRODUCTHUNT_DEVELOPER_TOKEN=your_producthunt_token
    # 如果使用非 OpenAI 官方接口（如 DeepSeek），可能还需要修改代码中的 client 初始化部分添加 base_url
    ```

**方式 B：GitHub Actions 运行**
1.  在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中添加 `OPENAI_API_KEY`。

### 步骤 3：验证翻译
1.  配置好 `.env` 文件后。
2.  运行 `python3 scripts/product_hunt_list_to_md.py`。
3.  检查生成的 `data/producthunt-daily-YYYY-MM-DD.md` 文件，内容应自动变为中文。

## 待确认事项
- 您是否已经拥有 OpenAI API Key？
- 如果您使用的是国内的大模型 API（如 DeepSeek、Kimi 等），我们需要微调一下代码中的 `openai.Client` 初始化部分，添加 `base_url` 参数。

确认后，我可以帮您创建 `.env` 文件模板或修改代码以支持其他大模型 API。
