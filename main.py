import asyncio
import sys

from loguru import logger
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from config import load_cfg, check_port
from copilot_proxy import CopilotProxy
from proxy_logger import ProxyLogger


async def main():
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>{level:<7}</level>: {message}",
    )

    try:
        config = load_cfg()
    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.error(str(e))
        return

    listen = config.listen

    try:
        check_port(listen.host, listen.port)
    except RuntimeError as e:
        logger.error(str(e))
        return

    opts = Options(
        listen_host=listen.host,
        listen_port=listen.port,
    )
    master = DumpMaster(
        opts,
        with_dumper=False,
        with_termlog=False,
    )
    master.addons.add(CopilotProxy(config))
    master.addons.add(ProxyLogger())

    await master.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("已停止")
