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
}
