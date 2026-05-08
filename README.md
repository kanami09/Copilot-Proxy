# Copilot-Proxy

允许将 VSCode 扩展 GitHub Copilot 的流量重定向到自定义的URL（仅代码补全，不包含 chat）

## 兼容性

本项目仅在 `deepseek-v4-flash` 模型（官方API）上经过测试，但理论上支持任何兼容 **OpenAI FIM 格式**的接口。

> **注意：** 此处应使用的是 `/completions`（代码补全）接口，而非 `/chat/completions`（对话）接口，请确保所使用的 API 提供商支持 FIM 格式的补全端点。

DeepSeek 对应的端点为 `/beta/completions`，可参考[配置模板](./config.toml.template)。

## 如何使用

由于使用了 `mitmproxy` 作为中间人，在正式使用之前必须先信任其 CA 证书，程序才能正常运行，证书会在第一次运行程序后自动生成<br>
Windows 平台上，证书生成在: `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer`<br>
macOS / Linux 平台上，证书生成在: `~/.mitmproxy/mitmproxy-ca-cert.pem`

你可以选择下面的方法来运行程序

### 使用预构建的二进制文件

1. 从 GitHub Releases 下载预构建的发布版

2. 从[配置模板](./config.toml.template)中创建一份配置文件，命名为 `config.toml`，并放置在与二进制文件相同的目录下

3. 运行程序

4. 携带环境变量 `HTTPS_PROXY` 启动 VSCode

    对于不同的 shell，你可以使用不同的方式写入环境变量，以下是几种常用的终端写入临时变量的方法：

    PowerShell

    ```pwsh
    $env:HTTPS_PROXY = "http://127.0.0.1:8080"
    ```

    cmd

    ```bat
    set HTTPS_PROXY="http://127.0.0.1:8080"
    ```

    bash / zsh

    ```bash
    export HTTPS_PROXY="http://127.0.0.1:8080"
    ```

    `127.0.0.1` 和 `8080` 可以分别用实际使用的主机和端口号替代（与配置文件中的配置项相同）

    最后在相同的 shell 中启动 VSCode:

    ```bash
    code .
    ```

### 自行构建运行

本项目使用 `uv` 作为包管理器，你可以使用 `uv` 构建并运行本项目

1. 安装 `uv`

    Windows (使用PowerShell运行):

    ```pwsh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    macOS / Linux:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

    详情请参阅: [uv的官方文档](https://docs.astral.sh/uv/)

2. 创建运行环境

    ```bash
    uv sync --no-dev
    ```

3. 从[配置模板](./config.toml.template)中创建一份配置文件，命名为 `config.toml`，并放置在项目根目录下

4. 构建并运行程序

    ```bash
    uv run main.py
    ```

5. 携带环境变量 `HTTPS_PROXY` 启动 VSCode，此步骤与[使用预构建的二进制文件](#使用预构建的二进制文件)的第 4 步相同
