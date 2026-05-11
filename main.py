import asyncio
import sys

from loguru import logger
import click
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from config import load_cfg, Config
from copilot_proxy import CopilotProxy
from proxy_logger import ProxyLogger
from _version import __version__


PROXY_HOST_WHITE_LIST = [r"proxy\.individual\.githubcopilot\.com"]


async def start_proxy(config: Config):
    listen = config.listen

    opts = Options(
        listen_host=listen.host,
        listen_port=listen.port,
        allow_hosts=PROXY_HOST_WHITE_LIST,
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


@click.command()
@click.help_option("--help", "-h", help="显示此帮助信息并退出")
@click.version_option(
    __version__,
    "--version",
    "-v",
    prog_name="CopilotProxy",
    help="显示版本信息并退出",
)
@click.option(
    "--config-path",
    "-c",
    type=click.Path(dir_okay=False, resolve_path=True, readable=True),
    default="config.toml",
    show_default=True,
    help="配置文件路径",
)
@click.option(
    "--listen-host",
    "-lh",
    type=str,
    help="代理监听的主机地址，不存在时使用配置文件中的值",
)
@click.option(
    "--listen-port",
    "-lp",
    type=int,
    help="代理监听的端口，不存在时使用配置文件中的值",
)
def main(config_path: str, listen_host: str, listen_port: int):
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>{level:<7}</level>: {message}",
    )

    try:
        config = load_cfg(config_path)
    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.error(str(e))
        return

    if listen_host:
        config.listen.host = listen_host
    if listen_port:
        config.listen.port = listen_port

    try:
        asyncio.run(start_proxy(config))
    except KeyboardInterrupt:
        logger.info("已停止")


if __name__ == "__main__":
    main()
