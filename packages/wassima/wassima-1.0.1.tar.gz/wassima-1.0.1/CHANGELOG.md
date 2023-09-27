# Changelog

All notable changes to wassima will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 1.0.1 (2023-09-26)

### Added
- Expose `__version__`.
- Support for `certifi` fallback if you did not pick up a compatible wheel. Expose constant `RUSTLS_LOADED` as a witness.

## 1.0.0 (2023-09-20)

### Added
- Public functions `root_der_certificates`, `root_pem_certificates`, `generate_ca_bundle`, and `create_default_ssl_context`.
