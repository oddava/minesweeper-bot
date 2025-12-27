# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-27

### Added
- Added professional versioning and changelog system.
- Added `/version` and `/changelog` bot commands.
- Added version display footer to the Minesweeper WebApp.

### Fixed
- Fixed inconsistent statistics in `/admin` and `/stats` commands caused by SQL cross-joins.
- Fixed `ModuleNotFoundError` for `sentry_sdk` and `uvloop` when running locally.
- Fixed local database and Redis connectivity by exposing ports and updating `.env` hosts.
- Fixed inflated `total_games` count by implementing backend de-duplication (3s cooldown) and frontend re-entry protection.

### Changed
- Improved robustness of i18n middleware when database sessions are missing.
- Made Sentry and uvloop optional for easier local development.

## [1.0.0] - 2024-12-25
- Initial production release.
- Core Minesweeper gameplay and Telegram integration.
