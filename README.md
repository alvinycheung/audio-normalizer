# Audio Normalizer - DFW Chinese Youth Camp

Automatically normalize all audio files to broadcast standard loudness levels for consistent playback during stage performances at DFW Chinese Youth Camp.

## Quick Start - macOS/Linux

```bash
# Prerequisites: Python 3 and ffmpeg must be installed
# If not installed: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)

# Clone and set up
git clone https://github.com/alvinycheung/audio-normalizer.git
cd audio-normalizer
mkdir -p mp3s normalized

# Add your audio files to the mp3s folder, then:
python3 normalize_audio.py

# Verify results
python3 verify_audio.py
```

## Quick Start - Windows

```cmd
# Prerequisites: Python and ffmpeg must be installed
# If not installed, see Prerequisites section below

# Clone and set up
git clone https://github.com/alvinycheung/audio-normalizer.git
cd audio-normalizer
mkdir mp3s
mkdir normalized

# Add your audio files to the mp3s folder, then:
python normalize_audio.py

# Verify results
python verify_audio.py
```

## What This Does

This tool ensures all your audio files have consistent perceived loudness (-16 LUFS broadcast standard), so you can play them in sequence without adjusting volume levels. Perfect for stage performances, presentations, or any event where you need seamless audio playback.

## Prerequisites

- Python 3.x (Windows users: download from [python.org](https://www.python.org/downloads/))
- ffmpeg with loudnorm filter support
- Git (Windows users: download from [git-scm.com](https://git-scm.com/download/win))

### Installing ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
1. Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the zip file to `C:\ffmpeg`
3. Add ffmpeg to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add `C:\ffmpeg\bin`
   - Click "OK" to save
4. Open Command Prompt and verify: `ffmpeg -version`

## Usage

1. Place your audio files in the `mp3s` folder (you can create subfolders)
2. Run the normalizer script
3. Find normalized files in the `normalized` folder with the same structure

### Advanced Usage

```bash
# Process a single file
python3 normalize_audio.py "filename.mp3"    # macOS/Linux
python normalize_audio.py "filename.mp3"     # Windows

# Verify a single file
python3 verify_audio.py "filename.mp3"       # macOS/Linux
python verify_audio.py "filename.mp3"        # Windows

# Check loudness of original source files
python3 verify_audio.py --source             # macOS/Linux
python verify_audio.py --source              # Windows
```

## Folder Structure

```
audio-normalizer/
├── mp3s/                 # Place your source audio files here
│   ├── folder1/
│   │   ├── track1.mp3
│   │   └── track2.m4a
│   └── folder2/
│       └── track3.mp4
├── normalized/           # Normalized files appear here (same structure)
│   ├── folder1/
│   │   ├── track1.mp3
│   │   └── track2.mp3   # All outputs are MP3
│   └── folder2/
│       └── track3.mp3
├── normalize_audio.py    # Main normalization script
├── verify_audio.py       # Verification script
└── README.md
```

## Supported Audio Formats

### Input
- **MP3** (.mp3, .MP3)
- **M4A** (.m4a) - Apple's audio format
- **MP4** (.mp4) - When containing audio
- **WAV** (.wav) - Uncompressed audio
- **FLAC** (.flac) - Lossless compression
- **AAC** (.aac) - Advanced Audio Coding
- **OGG** (.ogg) - Open source format
- **WMA** (.wma) - Windows Media Audio

### Output
All files are converted to MP3 format (192 kbps, 44.1 kHz) for maximum compatibility.

## Technical Details

- **Target Loudness**: -16 LUFS (integrated)
- **Loudness Range**: 7 LU
- **True Peak**: -1 dBTP (prevents clipping)
- **Output Format**: MP3, 192 kbps, 44.1 kHz

## Features

- **LUFS Normalization**: Uses broadcast standard -16 LUFS for consistent loudness
- **Preserves Folder Structure**: Mirrors your organization from `/mp3s` to `/normalized`
- **Non-Destructive**: Original files remain untouched
- **Progress Tracking**: Clear visual feedback during processing
- **Two-Pass Processing**: Analyzes then normalizes for best quality
- **Skip Existing**: Won't re-process already normalized files
- **Real-time Verification**: See compliance status for each file

## Troubleshooting

### "No audio files found"
- Make sure your files are in the `/mp3s` folder
- Check that files have supported extensions

### "ffmpeg not found"
- Install ffmpeg using the instructions above
- Make sure ffmpeg is in your system PATH

### "JSON parsing error" or corrupted metadata
- Some files may have corrupted metadata. The script will attempt single-pass normalization
- For persistent issues, try cleaning the file:
```bash
ffmpeg -i "input.mp3" -c:a mp3 -map_metadata -1 "output.mp3"
```

### Silent or -99 LUFS files
- These files have no detectable audio content
- Check if the source file is corrupted or intentionally silent

## Contributing

Feel free to submit issues or pull requests. This tool was created for DFW Chinese Youth Camp but can be used by anyone needing consistent audio normalization.

## License

This project is open source and available under the MIT License.