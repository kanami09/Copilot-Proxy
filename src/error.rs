use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Error)]
pub enum Error {
    #[error("路径不存在：{0}")]
    PathNotFound(String),
    #[error("IO 错误：{0}")]
    Io(#[from] std::io::Error),
    #[error("证书错误：{0}")]
    Cert(#[from] rcgen::Error),
    #[error("配置反文件序列化失败：{0}")]
    ConfigDeserialize(#[from] toml::de::Error),
    #[error("配置文件序列化失败：{0}")]
    ConfigSerialize(#[from] toml::ser::Error),
    #[error("配置版本 {found} 低于最低支持版本 {min}")]
    ConfigVersionTooLow { found: u32, min: u32 },
}
