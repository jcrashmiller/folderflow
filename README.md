# Folder Flow

Cross-desktop “smart folders” for Linux built on native filesystem features.
Works across distributions, desktop environments, and even in terminal-only setups.

Folder Flow lets you define dynamic file collections using filters (age, size, type, etc.) and exposes them as regular files via symlinks — no special file manager required.

This project started as an experiment in making “smart folders” portable across Linux environments without requiring custom file managers or desktop integrations.

## Screenshots

![Folder Flow Main Window](assets/images/screenshots/main_window.png)

## How it works (high level)

1. Define filters using a simple GUI (file type, age, size, exclusions)
2. Folder Flow scans the filesystem and creates symlinks in a target folder
3. A background monitor watches for file changes and updates symlinks in near real time
4. File previews (audio, video, images, text) are generated on demand and cached for fast reuse

## Features

- Distribution-, desktop-, and file-manager-agnostic
- Uses native Linux primitives (symlinks, filesystem searches)
- Background monitor keeps smart folders up to date automatically
- Preview system with configurable cache for responsive browsing

## Supported Filters

- **Age**
  - Modified within the last _X_ days
- **Size**
  - Larger or smaller than _X_ MB
- **Type**
  - Documents
  - Images
  - Audio
  - Video
  - Scripts
- Optional exclusion of common system files and directories

## Preview & Caching Behavior

- Previews are generated on demand the first time a file is viewed
- Generated previews are stored in a cache for reuse
- Cached previews are reused as long as the source file has not changed
- Default cache expiration is 30 minutes (user-configurable)
- Initial preview generation averages ~2 seconds; cached previews are near-instant

## Roadmap / In Development

- Finalize `requirements.txt`
- Installer to register the background monitor as a service
- Expanded filter options
- Improved preview handling and format support

