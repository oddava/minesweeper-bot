# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-12-27

### Added
- **New Year Eve Theme**: Festive gold & purple theme with glow effects 🎆
- Renamed game to "oddava's minesweeper"

### Changed
- Simplified title styling (removed gradient)
- **Performance**: CSS reduced from 870 to 180 lines
- **Performance**: JavaScript reduced from 550 to 250 lines
- Lighter weight, faster loading webapp

## [1.3.0] - 2025-12-27

### Added
- **Theme System**: 4 visual themes (Classic, Neon, Ocean, Retro)
- **Settings Modal**: Access via ⚙️ button with theme selector and vibration toggle
- **Game Stats Display**: Shows time, best time, clicks, and flags after game ends
- **Settings Persistence**: Theme and vibration preferences saved to localStorage

### Changed
- Replaced game-end popup modal with inline stats container
- Board now scrollable for Expert mode (16×30)
- Mode buttons centered on main menu

### Fixed
- Fixed black background appearing when scrolling game board
- Fixed viewport zoom restrictions
- Improved cell sizing for different screen sizes

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
