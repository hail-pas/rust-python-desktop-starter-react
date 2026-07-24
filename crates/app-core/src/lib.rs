use app_contracts::HealthResponse;

pub const PROTOCOL_VERSION: u32 = 1;

pub fn health() -> HealthResponse {
    HealthResponse {
        application: "rust-python-desktop-starter".to_owned(),
        rust_core: env!("CARGO_PKG_VERSION").to_owned(),
        protocol_version: PROTOCOL_VERSION,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn health_reports_current_protocol() {
        let response = health();
        assert_eq!(response.application, "rust-python-desktop-starter");
        assert_eq!(response.protocol_version, PROTOCOL_VERSION);
    }
}
