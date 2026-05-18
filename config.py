import tomllib
from dataclasses import dataclass
from pathlib import Path

from paths import LOGS_DIR


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


def load_cfg(cfg_path: Path) -> Config:
    # 尝试读取和加载配置文件
    if not cfg_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {cfg_path.absolute()}")
    try:
        with open(cfg_path, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"无法加载配置文件: {e}") from e

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
        target=Target(**config["target"]),
        listen=Listen(**config["listen"]),
        log=Log(**config["log"]),
    )
