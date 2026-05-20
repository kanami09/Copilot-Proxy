import tomllib
from dataclasses import dataclass
from pathlib import Path

import click

from paths import ROOT_PATH, LOGS_DIR, TEMPLATE_PATH


@dataclass
class Target:
    scheme: str
    host: str
    port: int
    path: str
    api_key: str
    model_name: str


@dataclass
class Listen:
    host: str
    port: int


@dataclass
class Log:
    save_path: str
    level: str


@dataclass
class Config:
    ver: int
    target: Target
    listen: Listen
    log: Log


CONFIG_REQUIRE_FIELD = {
    "target": {"scheme", "host", "port", "path", "api_key", "model_name"},
    "listen": {"host", "port"},
}

CONFIG_OPTIONAL_FIELD = {
    "log": {
        "save_path": str(LOGS_DIR),
        "level": "INFO",
    }
}

MIN_SUPPORTED_CFG_VER = 1


class ConfigRecreatedError(Exception):
    """配置文件已重新创建，需要用户修改后重新运行"""


class UserAbortConfigCreateError(Exception):
    """用户终止创建配置文件"""


def make_cfg_from_template(template_path: Path, cfg_path: Path) -> bool:
    if not template_path.exists():
        return False

    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_bytes(template_path.read_bytes())
    return True


def load_cfg(cfg_path: Path) -> Config:
    # 尝试读取和加载配置文件
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"配置文件不存在: {cfg_path.absolute()}，使用 `config` 命令创建配置文件"
        )
    try:
        with open(cfg_path, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"无法加载配置文件: {e}") from e

    # 验证配置版本
    ver = config.get("ver", 0)
    if ver < MIN_SUPPORTED_CFG_VER:
        if click.confirm(
            "当前配置文件版本过低，是否重新创建 (原有配置文件将会被备份)？",
            default=True,
        ):
            old_cfg_path = cfg_path.with_name(cfg_path.name + ".old")
            old_cfg_path.write_bytes(cfg_path.read_bytes())
            if make_cfg_from_template(TEMPLATE_PATH, cfg_path):
                click.echo(f"已重新创建配置文件: {cfg_path}")
                click.echo(f"已为旧版本配置文件创建了备份: {old_cfg_path}")
                raise ConfigRecreatedError("配置文件已重新创建，使用 `config` 命令编辑")
            else:
                old_cfg_path.unlink()
                raise FileNotFoundError(f"模板文件不存在: {TEMPLATE_PATH}")
        else:
            raise UserAbortConfigCreateError(
                "当前配置文件版本过低，重新创建后才能继续运行"
            )

    # 遍历必要参数的每个 section 和它对应的 key
    for section, keys in CONFIG_REQUIRE_FIELD.items():
        if section not in config:
            raise KeyError(f"缺少配置节: {section}")
        for key in keys:
            if key not in config[section]:
                raise KeyError(f"缺少配置项: {section}.{key}")

    # 填充可选配置的默认值
    for section, defaults in CONFIG_OPTIONAL_FIELD.items():
        config.setdefault(section, {})
        for key, default in defaults.items():
            config[section].setdefault(key, default)

    return Config(
        ver=ver,
        target=Target(**config["target"]),
        listen=Listen(**config["listen"]),
        log=Log(**config["log"]),
    )


@click.command(
    name="config",
    help="编辑配置文件",
)
@click.pass_context
def handle_config_cmd(ctx: click.Context):
    cfg_path: Path = ROOT_PATH / ctx.obj["config_path"]
    cfg_path = cfg_path.resolve()

    if not cfg_path.exists():
        if click.confirm(
            "配置文件不存在，是否使用模板文件创建?",
            default=True,
        ):
            if make_cfg_from_template(TEMPLATE_PATH, cfg_path):
                click.echo(f"已创建配置文件: {cfg_path}")
            else:
                click.echo("模板文件不存在，创建失败", err=True)
                return
        else:
            return

    click.edit(filename=str(cfg_path))
