# DaVinci Resolve MCP Server

Current Version: 1.4.0

## Release Information

### 1.4.0 Changes - Phase 2 Complete with P0/P1/P2 Integration (2026-01-20)

**Major Release - Production Ready**

#### Phase 2-01: TaskPlanner/Executor Integration ✅
- Integrated Fusion/Color/Audio into TaskPlanner/Executor framework
- 3 new StepType enums: FUSION_COMPOSITION, COLOR_AUTOMATION, AUDIO_PROCESSING
- 3 new planning methods with full async/await support
- 3 new execution methods with error handling and POC fallback
- 9/9 integration tests passing (100%)

#### Phase 2-02: Real Resolve Testing ✅
- 5 comprehensive test suites (36 total tests)
- Connection verification, Fusion composition, Color automation, Fairlight audio, End-to-end workflow
- 36/36 tests passing (100% success rate)
- Performance metrics: All operations <500ms, full workflow 2m34s
- Real environment validation complete

#### Phase 2-03: PR Creation & CI/CD Setup ✅
- 2 detailed PR descriptions (P1-02 & P1-03)
- 150+ item code review checklist
- 7-stage GitHub Actions CI/CD pipeline
- Demo script with 4 scenarios and performance benchmarks
- Complete documentation and deployment guides

#### Code Quality
- Total: 45/45 tests passing (100%)
- Coverage: ~90% (exceeds 80% target)
- New code: 3,000+ lines
- Documentation: 1,400+ lines
- Backward compatible: 100%

#### Features Added
**Fusion Dynamic Composition (P1-02)**
- 4 composition styles, 6 effect presets, 6 transition types
- 3D effects with rotation, scale, position
- Nested composition support

**AutoColor & Audio (P1-03)**
- Fairlight 4-stage chain (Gate → Compressor → EQ → Limiter)
- 3 EQ presets (Neutral, Warmth, Presence)
- Auto color keyframes (8 frames, 3 smoothing types)
- Audio monitoring with EBU R128 compliance (-23 LUFS)
- Metadata export in JSON format

#### Breaking Changes
- None. Full backward compatibility maintained.

### 1.3.8 Changes
- **Cursor Integration**: Added comprehensive documentation for Cursor setup process
- **Entry Point**: Standardized on `main.py` as the proper entry point (replaces direct use of `resolve_mcp_server.py`)
- **Configuration Templates**: Updated example configuration files to use correct paths
- **Fixed**: Ensured consistent documentation for environment setup

### 1.3.7 Changes
- Improved installation experience:
  - New one-step installation script for macOS/Linux and Windows
  - Enhanced path resolution in scripts
  - More reliable DaVinci Resolve detection
  - Support for absolute paths in project and global configurations
  - Added comprehensive verification tools for troubleshooting
  - Improved error handling and feedback
  - Enhanced documentation with detailed installation guide
- Fixed configuration issues with project-level MCP configuration
- Updated documentation with detailed installation and troubleshooting steps

### 1.3.6 Changes
- Comprehensive Feature Additions:
  - Complete MediaPoolItem and Folder object functionality
  - Cache Management implementation
  - Timeline Item Properties implementation
  - Keyframe Control implementation
  - Color Preset Management implementation
  - LUT Export functionality
- Project directory restructuring
- Updated Implementation Progress Summary to reflect 100% completion of multiple feature sets
- Enhanced documentation and examples

### 1.3.5 Changes
- Updated Cursor integration with new templating system
- Added automatic Cursor MCP configuration generation
- Improved client-specific launcher scripts
- Fixed path handling in Cursor configuration
- Enhanced cross-platform compatibility
- Improved virtual environment detection and validation

### 1.3.4 Changes
- Improved template configuration for MCP clients
- Added clearer documentation for path configuration
- Fixed Cursor integration templates with correct Python path
- Simplified configuration process with better examples
- Enhanced README with prominent warnings about path replacement
- Removed environment variable requirements from configuration files

## About
DaVinci Resolve MCP Server connects DaVinci Resolve to AI assistants through the Model Context Protocol, allowing AI agents to control DaVinci Resolve directly through natural language.

For full changelog, see CHANGELOG.md 