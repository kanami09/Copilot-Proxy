use std::fs;

use rcgen::{
    BasicConstraints, CertificateParams, DistinguishedName, DnType, DnValue, IsCa, Issuer, KeyPair,
    KeyUsagePurpose,
};
use tracing::{info, trace, warn};

use crate::error::{Error, Result};

const CA_CERT_PATH: &str = "ca.crt";
const CA_KEY_PATH: &str = "ca.key";

pub fn load_ca() -> Result<Issuer<'static, KeyPair>> {
    /* 查询证书是否已存在 */
    let home = dirs::home_dir().ok_or(Error::PathNotFound("用户目录不存在".to_string()))?;
    let ca_path = home.join(".copilot_proxy_ca");
    let cert_path = ca_path.join(CA_CERT_PATH);
    let key_path = ca_path.join(CA_KEY_PATH);
    trace!("cert: {}", cert_path.to_str().map_or("None", |v| v));
    trace!("key: {}", key_path.to_str().map_or("None", |v| v));
    let (cert, key) = if cert_path.is_file() && key_path.is_file() {
        info!("读取到本地的 CA 证书");
        (
            fs::read_to_string(&cert_path)?,
            fs::read_to_string(&key_path)?,
        )
    } else {
        if ca_path.is_dir() {
            warn!("CA 证书损坏，正在重新生成 CA 证书");
        }
        let (cert, key) = generate_ca()?;
        fs::create_dir_all(&ca_path)?;
        fs::write(&cert_path, &cert)?;
        fs::write(&key_path, &key)?;
        trace!("写入新的CA证书");
        info!(
            "已生成 CA 证书 ({})，请信任该证书",
            cert_path.to_str().map_or("None", |v| v)
        );
        (cert, key)
    };

    let key = KeyPair::from_pem(&key)?;
    Ok(Issuer::from_ca_cert_pem(&cert, key)?)
}

fn generate_ca() -> Result<(String, String)> {
    let mut params = CertificateParams::default();

    params.distinguished_name = DistinguishedName::new();
    params.distinguished_name.push(
        DnType::CommonName,
        DnValue::Utf8String("Copilot-Proxy CA".to_string()),
    );
    params.key_usages = vec![KeyUsagePurpose::KeyCertSign, KeyUsagePurpose::CrlSign];
    params.is_ca = IsCa::Ca(BasicConstraints::Unconstrained);

    let key = KeyPair::generate()?;
    let cert = params.self_signed(&key)?;

    Ok((cert.pem(), key.serialize_pem()))
}
