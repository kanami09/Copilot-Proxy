import tomllib
from dataclasses import dataclass
from pathlib import Path


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
class Config:
    target: Target
    listen: Listen


CONFIG_REQUIRE_FIELD = {
    "target": {"scheme", "host", "port", "path", "api_key", "model_name"},
    "listen": {"host", "port"},
}


def load_cfg(path: str) -> Config:
    cfg_path = Path(path)

    # 尝试读取和加载配置文件
    if not cfg_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {cfg_path.absolute()}")
    try:
        with open(cfg_path, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"无法加载配置文件: {e}") from e

    # 遍历每个 section 和它对应的必要 key 列表
    for section, keys in CONFIG_REQUIRE_FIELD.items():
        if section not in config:
            raise KeyError(f"缺少配置节: {section}")
        for key in keys:
            if key not in config[section]:
                raise KeyError(f"缺少配置项: {section}.{key}")

    # 返回最终配置
    t = config["target"]
    ls = config["listen"]
    target = Target(
        scheme=t["scheme"],
        host=t["host"],
        port=t["port"],
        path=t["path"],
        api_key=t["api_key"],
        model_name=t["model_name"],
    )
    listen = Listen(
        host=ls["host"],
        port=ls["port"],
    )

    return Config(
        target=target,
        listen=listen,
    )
