import asyncio
import sys

from loguru import logger
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from config import load_cfg
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

    try:
        await master.run()
    except SystemExit as e:
        if e.code != 0:
            if ec := master.addons.get("errorcheck"):
                for record in ec.logger.has_errored:
                    logger.error(record.getMessage())
            else:
                logger.error(f"代理在 {listen.host}:{listen.port} 启动失败")


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("已停止")


if __name__ == "__main__":
    run()
