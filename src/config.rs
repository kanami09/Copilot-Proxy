use std::{fs, path::Path};

use serde::{Deserialize, Serialize};
use tracing::{Level, info, warn};

use crate::{Error, error::Result};

const TEMPLATE: &str = include_str!("../config.template.toml");
const MIN_SUPPORT_CONFIG_VER: u32 = 1;

#[derive(Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub ver: u32,
    pub target: TargetConfig,
    pub listen: ListenConfig,
    pub log: LogConfig,
}

#[derive(Serialize, Deserialize)]
pub struct TargetConfig {
    pub scheme: String,
    pub host: String,
    pub port: u16,
    pub path: String,
    pub api_key: String,
    pub model_name: String,
}

#[derive(Serialize, Deserialize)]
pub struct ListenConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Serialize, Deserialize)]
pub struct LogConfig {
    pub save_path: String,
    pub level: LogLevel,
}

#[derive(Serialize, Deserialize, Clone, Copy)]
#[serde(rename_all = "lowercase")]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

impl From<LogLevel> for Level {
    fn from(level: LogLevel) -> Self {
        match level {
            LogLevel::Trace => Level::TRACE,
            LogLevel::Debug => Level::DEBUG,
            LogLevel::Info => Level::INFO,
            LogLevel::Warn => Level::WARN,
            LogLevel::Error => Level::ERROR,
        }
    }
}

impl Config {
    pub fn load_or_new(path: &Path) -> Result<Self> {
        if !path.is_file() {
            warn!(
                "{} 不是一个有效路径，使用模板创建默认配置",
                std::path::absolute(path)
                    .unwrap_or_else(|_| path.to_path_buf())
                    .display()
            );

            // 路径无效，尝试从模板复制
            Self::create_from_template(path)?;
            info!("已创建默认配置");
        }

        let mut config: Config = toml::from_str(&fs::read_to_string(path)?)?;
        info!("Config Ver: {}", config.ver);

        if config.ver < MIN_SUPPORT_CONFIG_VER {
            warn!("Config 版本低于最低支持版本: {}", MIN_SUPPORT_CONFIG_VER);
            let old_path = path
                .parent()
                .ok_or_else(|| Error::PathNotFound(path.display().to_string()))?
                .join("config.old.toml");
            fs::copy(path, &old_path)?;
            Self::create_from_template(path)?;
            info!("创建了新的默认参数，旧配置已备份: {}", old_path.display());
            config = toml::from_str(&fs::read_to_string(path)?)?;

            // 重建后理应来自模板，版本必然达标；若仍不达标说明模板本身有问题
            if config.ver < MIN_SUPPORT_CONFIG_VER {
                return Err(Error::ConfigVersionTooLow {
                    found: config.ver,
                    min: MIN_SUPPORT_CONFIG_VER,
                });
            }
        }

        Ok(config)
    }

    pub fn create_from_template(path: &Path) -> Result<()> {
        fs::write(path, TEMPLATE)?;

        Ok(())
    }

    pub fn save(&self, path: &Path) -> Result<()> {
        let contents = toml::to_string_pretty(self)?;
        fs::write(path, contents)?;

        Ok(())
    }
}
