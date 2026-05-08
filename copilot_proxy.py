import codecs
import json

from loguru import logger
from mitmproxy import http

from config import Config

COPILOT_EXTRA_FIELDS = {"extra", "code_annotations", "n"}
SENSITIVE_HEADERS = {"authorization"}


class CopilotProxy:
    def __init__(self, config: Config) -> None:
        self.config = config
        listen = self.config.listen
        logger.info(f"正在从 {listen.host}:{listen.port} 监听")

    def request(self, flow: http.HTTPFlow):
        req = flow.request

        # 只拦截代码补全的端点：/v1/engines/*/completions
        if req.host != "proxy.individual.githubcopilot.com":
            return
        if not req.path.startswith("/v1/engines/"):
            return
        if not req.path.endswith("/completions"):
            return

        # 尝试解析请求
        try:
            body = req.json()
        except json.decoder.JSONDecodeError as e:
            logger.error("请求解析失败")
            logger.exception(e)
            return

        # 删除 Copilot 的专有字段
        for field in COPILOT_EXTRA_FIELDS:
            body.pop(field, None)

        # 构造重定向请求
        t = self.config.target
        body["model"] = t.model_name
        req.content = json.dumps(body).encode("utf-8")
        req.scheme = t.scheme
        req.host = t.host
        req.port = t.port
        req.path = t.path
        headers = req.headers
        headers.clear()
        headers["Host"] = t.host
        headers["Authorization"] = f"Bearer {t.api_key}"
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(req.content))

        logger.info(f"{req.method} ({req.scheme}) {req.host}{req.path}")
        safe_headers = {
            k: ("***" if k.lower() in SENSITIVE_HEADERS else v)
            for k, v in req.headers.items()
        }
        logger.debug(f"Headers {safe_headers}")
        logger.debug(f"Content {json.dumps(body,ensure_ascii=False, indent=2)}")

    def responseheaders(self, flow: http.HTTPFlow):
        resp = flow.response
        if resp is None:
            return
        if flow.request.host != self.config.target.host:  # 只处理来自重定向主机的响应
            return

        content_type = resp.headers.get("content-type", "")
        logger.info(f"Response {resp.status_code} {content_type}")

        if resp.status_code >= 400:  # 非成功响应，直接返回
            return

        if "text/event-stream" not in content_type:
            return

        # 用闭包维护每个 flow 独立的缓冲区
        buf = bytearray()
        decoder = codecs.getincrementaldecoder("utf-8")("replace")

        def handle_chunk(chunk: bytes) -> bytes:
            nonlocal buf

            if not chunk:
                return chunk  # b"" 表示结束，直接透传

            buf.extend(chunk)

            # 按换行切割，保留末尾不完整的行
            last_newline = buf.rfind(b"\n")
            if last_newline == -1:  # 还没有完整行，等下一个 chunk
                return chunk

            complete = decoder.decode(bytes(buf[: last_newline + 1]))
            buf = bytearray(buf[last_newline + 1 :])

            for line in complete.splitlines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue

                logger.debug(line)

            return chunk  # 原样透传，不修改内容

        resp.stream = handle_chunk

    def response(self, flow: http.HTTPFlow):
        resp = flow.response
        if resp is None:
            return
        if flow.request.host != self.config.target.host:  # 只处理来自重定向主机的响应
            return
        if resp.status_code < 400:  # 成功的响应，直接返回
            return

        try:
            body = resp.json()
            logger.error(
                f"失败的响应 HTTP Code {resp.status_code}\n{json.dumps(body, ensure_ascii=False, indent=4)}"
            )
        except json.decoder.JSONDecodeError:
            logger.error(f"失败的响应 HTTP Code {resp.status_code} {resp.text}")
