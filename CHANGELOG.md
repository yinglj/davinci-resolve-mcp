# Changelog

All notable changes to the DaVinci Resolve MCP Server project will be documented in this file.

## [1.1.0] - 2025-03-26

### Added
- Claude Desktop integration with claude_desktop_config.json support
- Consolidated server management script (scripts/server.sh)
- Project structure reorganization for better maintenance
- Configuration templates for easier setup

### Changed
- Moved scripts to dedicated scripts/ directory
- Organized example files into examples/ directory
- Updated README with Claude Desktop instructions
- Updated FEATURES.md to reflect Claude Desktop compatibility

### Fixed
- Environment variable handling in server scripts
- Path references in documentation

## [1.0.0] - 2025-03-24

### Added
- Initial release with Cursor integration
- DaVinci Resolve connection functionality
- Project management features (list, open, create projects)
- Timeline operations (create, list, switch timelines)
- Marker functionality with advanced frame detection
- Media Pool operations (import media, create bins)
- Comprehensive setup scripts
- Pre-launch check script

### Changed
- Switched from original MCP framework to direct JSON-RPC for improved reliability

### Fixed
- Save Project functionality with multi-method approach
- Environment variable setup for consistent connection

## [0.1.0] - 2025-03-26

### Added
- Initial release with core functionality
- Connection to DaVinci Resolve via MCP
- Project management features (list, open, create projects)
- Timeline operations (list, create, switch timelines, add markers)
- Media pool operations (list clips, import media, create bins)
- Setup script for easier installation and configuration
- Comprehensive documentation

### Implemented Features
- [x] **Get Resolve Version** – Resource that returns the Resolve version string
- [x] **Get Current Page** – Resource that identifies which page is currently open in the UI
- [x] **Switch Page** – Tool to change the UI to a specified page

- [x] **List Projects** – Resource that lists available project names
- [x] **Get Current Project Name** – Resource that retrieves the name of the currently open project
- [x] **Open Project** – Tool to open a project by name
- [x] **Create New Project** – Tool to create a new project with a given name
- [x] **Save Project** – Tool to save the current project

- [x] **List Timelines** – Resource that lists all timeline names in the current project
- [x] **Get Current Timeline** – Resource that gets information about the current timeline
- [x] **Create Timeline** – Tool to create a new timeline
- [x] **Set Current Timeline** – Tool to switch to a different timeline by name
- [x] **Add Marker** – Tool to add a marker at a specified time on the current timeline

- [x] **List Media Pool Clips** – Resource that lists clips in the media pool
- [x] **Import Media** – Tool to import a media file into the current project
- [x] **Create Bin** – Tool to create a new bin/folder in the media pool

### Future Work
- [ ] Move Clip to Timeline – Tool to take a clip from the media pool and place it on the timeline
- [ ] Windows and Linux Support
- [ ] Claude Desktop Integration
- [ ] Color Page Operations
- [ ] Fusion Operations

## [0.3.0] - 2025-03-26
### Changed
- Cleaned up project structure by removing redundant test scripts and log files
- Removed duplicate server implementations to focus on the main MCP server
- Consolidated server startup scripts to simplify usage
- Created backup directories for removed files (cleanup_backup and logs_backup)
- Improved marker functionality with better frame detection and clip-aware positioning

### Added
- Implemented "Add Clip to Timeline" feature to allow adding media pool clips to timelines
- Added test script for validating timeline operations
- Added comprehensive marker testing to improve functionality

## [0.3.1] - 2025-03-27
### Enhanced
- Completely overhauled marker functionality:
  - Added intelligent frame selection when frame is not specified
  - Improved error handling for marker placement
  - Added collision detection to avoid overwriting existing markers
  - Added suggestions for alternate frames when a marker already exists
  - Implemented validation to ensure markers are placed on actual clips
  - Better debugging and detailed error messages

### Fixed
- Resolved issue with markers failing silently when trying to place on invalid frames
- Fixed marker placement to only allow adding markers on actual media content

## [0.2.0] - 2025-03-25

### Added
- Added new features and improvements
- Updated documentation

### Implemented Features
- [x] **New Feature 1** – Description of the new feature
- [x] **New Feature 2** – Description of the new feature

### Future Work
- [ ] Task 1 – Description of the task
- [ ] Task 2 – Description of the task 