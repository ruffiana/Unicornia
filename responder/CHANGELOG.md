# Changelog

## [0.1.7] - 2025-01-19

### Changed

- Long Cat responder now accepts 'short' cat. It also keeps the current cat length, increasing or decreasing it with more 'o's
- All responder classes are now initialized when the cog is. This allows us to store property values while the cog is running.

## [0.1.6] - 2025-01-18

### Added

- Berry Rate
- Added module docstrings

### Changed

- Responder classes all now use a match pattern list for simplicity and clarity
- Only attempt to get a discord.Member object once we have a valid match to a responder pattern. This should help with false positives and error messages.
- Changed always/never respond lists to be in .const. They can be extended/overwritten in the init method in each responder class
- Fixed bug in Dom/Sub rate responder

### Fixed

- Restored dimbo thumnail

## [0.1.5] - 2025-01-17

### Changed

- Added allowed channel set

### Fixed

- Changed regex for discord ids to only trigger on integers 17-19 long

## [0.1.4] - 2025-01-17

### Changed

- Changed regex pattern for 'rate' to avoid more common words
- Organization and renaming of responder modules/classes


## [0.1.3] - 2025-01-17

### Fixed

- Fixed display message for user overrides in dom/sub rate

### Changed

- Organization and renaming of responder modules/classes

## [0.1.2] - 2025-01-17

## Added

- Responder for Dom/Sub rate

## Changed

- Organization and renaming of responder modules/classes

## [0.1.1] - 2025-01-17

## Added

- Responder for 'the game'
- Responder for table unflip

### Changed

- Rate responder will ignore common words that contain 'rate', such as "Separate", "Celebrate", "Operate", etc.
- Added whitespace to regex pattern for "[trigger] [target member]"

### Fixed

- Changed rate anything to use target member display name instead of user name

## [0.1.0] - 2025-01-15

### Added

- Created initial project setup.
- Implemented basic functionality for a bot that responds to messages.
