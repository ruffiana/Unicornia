# Changelog

## Upcoming Features
 - Add support for for pronouns. Currently, there is no way to retrieve pronouns from a discord.User profile
 - UI interface for editing settings. This may require creating an app command ('/settings') in order to utilize discords interaction objects and ephemeral messaging

## [2.5.1] - 2021-12-20

### Added
- Added CustomMessagePredicate subclass to allow for more types of yes/no responses. It can also accept multiple users for check (allows reuse for owners, owner, or member to member)

### Changed
- Fixed bug that would allow interactions between a command invoker and other member to skip consent if the invoker owner consented (You don't own everyone!!)

## [2.5.0] - 2021-12-19

### Added
- Added "download" admin command. This caches all action gifs to a subfolder under the cog's config data folder

### Changed
- Action commands will look for local cached image directories and use a random image from those instead of the URLs when available

## [2.4.0] - 2021-12-16

### Added
- Added "Servant" flag to user settings. "Servants" will automatically consent to any request for them to perform an action on other members.

## [2.3.5] - 2021-12-16

### Fixed
- Fixed bug that would cause owner to be asked for consent twice (Are you *really* sure?)

### Added
- Error handling for operation that caches spoilered images

## [2.3.4] - 2021-12-16

### Changed
- Ask commands will ignore public use flag and ask the target member for consent when required

## [2.3.3] - 2021-12-16

### Added
- Added admin commands group
- Added logger_settings command group and logger_set_level command

## [2.3.2] - 2021-12-16

### Changed
- Changed some of the consent messages back to member.mention

### Fixed
- Fixed formatting issues in action YAML files
- made Action.aliases an optional property
- fixed interaction allowing consent to be skipped

## [2.3.1] - 2021-12-15

### Changed
- Changed many member.mention uses to member.display_name to reduce notifications
- Changed spoilered command images to use description as text message with cached spoiler image as attachment
- Simplified docstring for ask command function

### Fixed
- Fixed extra space in state settings checks (Ex: &roleplay settings public)

## [2.3.0] - 2021-12-14

### Added
- "ask" command. Ask another member to perform an action on yourself
- Added cooldown reset whenever an interaction is not successful

### Changed
- Major refactor of action command data
- Action consent messages all standardized to use the member who needs to respond as the first person in the messages
- Added 'active' and 'passive' consent messaging
- Added Action manager class and dataclasses for action properties
- Added Embed class for assembling embed objects in a cleaner way
- Embed can handle caching and attaching spoilered images to embed messages for a bit nicer presentation
- Changed consent validation to accommodate both owner and target having owners. Consent can only be obtained if both respond yes

### Fixed
- Fixed various typos in messages

## [1.0.0] - 2024-11-26

### Added
- Initial release with basic features and commands

### Changed
- Initial setup and configuration

### Fixed
- Initial bug fixes and improvements
