# Audio Normalizer Project Plan

## Overview
Build a Python script that normalizes MP3 files to broadcast standard loudness levels, maintaining folder structure from source to destination.

## Requirements
- [x] LUFS normalization to -16 LUFS (broadcast standard)
- [x] Preserve folder structure from `/mp3s` to `/normalized`
- [x] Progress indicators in console
- [x] Non-destructive (keep originals)
- [x] Batch processing capability

## Implementation Checklist

### 1. Project Setup
- [x] Create project_plan.md (this file)
- [x] Create `/normalized` directory
- [x] Verify ffmpeg is installed
- [x] Verify Python 3 is installed

### 2. Core Implementation
- [x] Create `normalize_audio.py` script
- [x] Implement recursive directory scanning
- [x] Add folder structure mirroring logic
- [x] Implement LUFS normalization using ffmpeg

### 3. Audio Processing Features
- [x] Two-pass loudnorm processing:
  - [x] First pass: Analyze audio levels
  - [x] Second pass: Apply normalization
- [x] Target parameters:
  - [x] Integrated loudness: -16 LUFS
  - [x] Loudness range: 7 LU
  - [x] True peak: -1 dBTP

### 4. User Experience
- [x] Progress indicators showing:
  - [x] Current file being processed
  - [x] File count (e.g., [23/45])
  - [x] Percentage complete
- [x] Colored console output for better readability
- [x] Summary statistics at completion

### 5. Error Handling
- [x] Handle missing source directory
- [x] Handle corrupted MP3 files
- [x] Handle file permission issues
- [x] Log errors without stopping batch processing

### 6. Testing
- [x] Test with single file
- [x] Test with multiple files
- [x] Test with nested folder structure
- [x] Test error scenarios

### 7. Documentation
- [x] Usage instructions in script header
- [x] Command examples
- [x] Troubleshooting guide

### 8. Verification Tool
- [x] Create `verify_audio.py` script
- [x] Check LUFS compliance (±0.5 tolerance)
- [x] Verify file counts match
- [x] Check peak levels compliance
- [x] Provide clear pass/fail status

## Technical Details

### LUFS Normalization Parameters
```
Target integrated loudness: -16.0 LUFS
Loudness range: 7.0 LU  
Max true peak: -1.0 dBTP
```

### Directory Structure Example
```
/mp3s/
  ├── show1/
  │   ├── intro.mp3
  │   └── main.mp3
  └── show2/
      └── track.mp3

/normalized/
  ├── show1/
  │   ├── intro.mp3 (normalized)
  │   └── main.mp3 (normalized)
  └── show2/
      └── track.mp3 (normalized)
```

## Usage
```bash
python3 normalize_audio.py
```

## Dependencies
- Python 3.x
- ffmpeg (with loudnorm filter support)
- Python packages: subprocess, pathlib, colorama (for colored output)