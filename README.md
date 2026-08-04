# Jellyfin Batch Renamer

Jellyfin Batch Renamer is a desktop application for organizing TV series libraries by renaming video and subtitle files to a consistent, Jellyfin-compatible format.


## Main Features

- Batch renaming for video and subtitle files.
- Automatic matching of videos and subtitles by list order.
- Jellyfin-compatible episode names such as `S02E01` and `Series Name - S02E01`.
- Support for common video formats: `mp4`, `mkv`, `avi`, `mov`, `wmv`, `flv`, `webm`, `m4v`, and `ts`.
- Support for common subtitle formats: `srt`, `ass`, `vtt`, `sub`, `ssa`, and `idx`.
- Optional recursive scanning of subfolders.
- Natural filename sorting for correctly ordering numbered episodes.
- Manual drag-and-drop reordering of video and subtitle lists.
- Rename preview before applying changes.
- Conflict detection and safe transactional renaming.
- Persistent undo for the latest rename operation.
- English and Arabic interface languages.
- Light and dark themes with saved preferences.

## Installation

### Requirements

- Python 3.10 or newer
- Windows, Linux, or macOS

### 1. Download the Project

Download and extract the project folder, then open a terminal inside it.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

```bat
.venv\Scripts\activate.bat
```

**Linux or macOS**

```bash
source .venv/bin/activate
```

### 4. Install the Requirements

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

## Usage

1. Select the folder containing the season or episode files.
2. Enable **Search subfolders** if the files are stored inside subfolders.
3. Review the video and subtitle lists after they are sorted automatically.
4. Drag items to correct their order when necessary.
5. Enter a season value such as `S02`, then optionally enter the series name.
6. Click **Rename files** and review the complete preview.
7. Confirm the operation to rename the files.
8. Use **Undo last rename** to restore the previous filenames. Undo remains available after restarting the application.

## Local Database

A SQLite database named `rename_history.db` is stored inside the application folder. It contains:

- The latest successful rename history.
- The last selected language.
- The last selected light or dark theme.

The rename history is cleared after a successful undo. SQLite is included with Python, so no additional database package is required.

## Safety Notes

- Files are renamed inside their original folders and are never moved.
- Unrelated files, such as images and NFO files, are ignored.
- The operation is blocked when a target filename conflicts with an existing file.
- Temporary filenames are used to prevent collisions while filenames are exchanged.
- If a rename step fails, the application attempts to restore the original filenames.

## Arabic Documentation

See `README_AR.md` for the Arabic version of this documentation.
