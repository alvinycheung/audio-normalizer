#!/usr/bin/env python3
"""
Audio Normalizer - Normalize MP3 files to broadcast standard loudness levels

This script normalizes all MP3 files in the /mp3s directory to -16 LUFS,
preserving the folder structure in the /normalized directory.

Usage: python3 normalize_audio.py
"""

# ASCII Art for DFW Chinese Youth Camp
ASCII_LOGO = """
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░                                                            ░░
    ░░       ██████╗██╗   ██╗ ██████╗                           ░░
    ░░      ██╔════╝╚██╗ ██╔╝██╔════╝                           ░░
    ░░      ██║      ╚████╔╝ ██║                                ░░
    ░░      ██║       ╚██╔╝  ██║                                ░░
    ░░      ╚██████╗   ██║   ╚██████╗                           ░░
    ░░       ╚═════╝   ╚═╝    ╚═════╝                           ░░
    ░░                                                            ░░
    ░░        DFW Chinese Youth Camp Audio Normalizer            ░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Target loudness parameters (broadcast standard)
TARGET_LUFS = -16.0
TARGET_LRA = 7.0
TARGET_TP = -1.0

def print_header():
    """Print script header"""
    print(f"{Colors.CYAN}{ASCII_LOGO}{Colors.RESET}")
    print(f"\n{Colors.BOLD}{Colors.CYAN}Audio Normalizer{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"Target: {TARGET_LUFS} LUFS (Broadcast Standard)")
    print(f"{'='*50}\n")

def find_audio_files(source_dir: Path) -> List[Path]:
    """Find all audio files in the source directory recursively"""
    audio_extensions = {'.mp3', '.m4a', '.mp4', '.wav', '.flac', '.aac', '.ogg', '.wma'}
    audio_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(Path(root) / file)
    return sorted(audio_files)

def create_output_path(source_file: Path, source_dir: Path, output_dir: Path) -> Path:
    """Create the output path maintaining folder structure, converting to .mp3"""
    relative_path = source_file.relative_to(source_dir)
    # Change extension to .mp3 for output
    output_path = output_dir / relative_path.with_suffix('.mp3')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path

def analyze_loudness(input_file: Path) -> Dict:
    """First pass: Analyze audio loudness using ffmpeg"""
    cmd = [
        'ffmpeg', '-i', str(input_file),
        '-af', f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json',
        '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # Extract JSON from stderr
        stderr_lines = result.stderr.split('\n')
        json_start = None
        json_data = []
        
        for i, line in enumerate(stderr_lines):
            if '{' in line and json_start is None:
                json_start = i
            if json_start is not None:
                json_data.append(line)
            if '}' in line and json_start is not None:
                break
        
        if json_data:
            json_str = '\n'.join(json_data)
            # Extract just the JSON part
            json_str = json_str[json_str.find('{'):json_str.rfind('}')+1]
            return json.loads(json_str)
        else:
            return None
            
    except Exception as e:
        print(f"{Colors.RED}Error analyzing {input_file}: {e}{Colors.RESET}")
        return None

def normalize_audio(input_file: Path, output_file: Path, loudness_data: Dict) -> bool:
    """Second pass: Apply normalization based on analysis"""
    if not loudness_data:
        # Fallback to single-pass if analysis failed
        cmd = [
            'ffmpeg', '-i', str(input_file),
            '-af', f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}',
            '-ar', '44100',  # Standard sample rate
            '-b:a', '192k',  # Good quality bitrate
            '-y',  # Overwrite output
            str(output_file)
        ]
    else:
        # Two-pass normalization with measured values
        measured_i = loudness_data.get('input_i', '-99.0')
        measured_tp = loudness_data.get('input_tp', '-99.0')
        measured_lra = loudness_data.get('input_lra', '0.0')
        measured_thresh = loudness_data.get('input_thresh', '-99.0')
        target_offset = loudness_data.get('target_offset', '0.0')
        
        cmd = [
            'ffmpeg', '-i', str(input_file),
            '-af', f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}:'
                   f'measured_I={measured_i}:measured_TP={measured_tp}:'
                   f'measured_LRA={measured_lra}:measured_thresh={measured_thresh}:'
                   f'offset={target_offset}:linear=true',
            '-ar', '44100',
            '-b:a', '192k',
            '-y',
            str(output_file)
        ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Error normalizing {input_file}: {e}{Colors.RESET}")
        return False

def format_progress(current: int, total: int, filename: str) -> str:
    """Format progress indicator"""
    percentage = (current / total) * 100
    progress_bar_length = 30
    filled_length = int(progress_bar_length * current // total)
    bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    
    return (f"{Colors.YELLOW}[{current}/{total}]{Colors.RESET} "
            f"{Colors.BLUE}[{bar}]{Colors.RESET} "
            f"{percentage:3.0f}% - {filename}")

def main():
    """Main function"""
    print_header()
    
    # Define directories
    base_dir = Path(__file__).parent
    source_dir = base_dir / 'mp3s'
    output_dir = base_dir / 'normalized'
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"{Colors.RED}Error: Source directory '{source_dir}' not found!{Colors.RESET}")
        sys.exit(1)
    
    # Check for single file argument
    if len(sys.argv) > 1:
        # Single file mode
        file_path = sys.argv[1]
        audio_extensions = {'.mp3', '.m4a', '.mp4', '.wav', '.flac', '.aac', '.ogg', '.wma'}
        if not any(file_path.lower().endswith(ext) for ext in audio_extensions):
            print(f"{Colors.RED}Error: File must be an audio file (mp3, m4a, mp4, etc.)!{Colors.RESET}")
            sys.exit(1)
        
        # Find the file in source directory
        audio_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file == os.path.basename(file_path) or str(Path(root) / file).endswith(file_path):
                    audio_files.append(Path(root) / file)
                    break
        
        if not audio_files:
            print(f"{Colors.RED}Error: File '{file_path}' not found in {source_dir}!{Colors.RESET}")
            sys.exit(1)
        
        print(f"{Colors.CYAN}Single file mode: {audio_files[0].relative_to(source_dir)}{Colors.RESET}")
    else:
        # Find all audio files
        print(f"{Colors.CYAN}Scanning for audio files...{Colors.RESET}")
        audio_files = find_audio_files(source_dir)
    
    if not audio_files:
        print(f"{Colors.YELLOW}No audio files found in '{source_dir}'!{Colors.RESET}")
        sys.exit(0)
    
    print(f"Found {Colors.GREEN}{len(audio_files)}{Colors.RESET} audio files\n")
    
    # Process each file
    successful = 0
    failed = 0
    skipped = 0
    
    for i, input_file in enumerate(audio_files, 1):
        relative_path = input_file.relative_to(source_dir)
        print(format_progress(i, len(audio_files), str(relative_path)))
        
        # Create output path
        output_file = create_output_path(input_file, source_dir, output_dir)
        
        # Check if output file already exists
        if output_file.exists():
            print(f"  {Colors.BLUE}↷ Already normalized, skipping...{Colors.RESET}")
            skipped += 1
            print()  # Empty line between files
            continue
        
        # First pass: Analyze
        print(f"  {Colors.CYAN}↳ Analyzing loudness...{Colors.RESET}", end='', flush=True)
        loudness_data = analyze_loudness(input_file)
        
        if loudness_data:
            current_lufs = float(loudness_data.get('input_i', '-99'))
            print(f" Current: {Colors.YELLOW}{current_lufs:.1f} LUFS{Colors.RESET}")
        else:
            print(f" {Colors.YELLOW}Using single-pass mode{Colors.RESET}")
        
        # Second pass: Normalize
        print(f"  {Colors.CYAN}↳ Normalizing...{Colors.RESET}", end='', flush=True)
        if normalize_audio(input_file, output_file, loudness_data):
            print(f" {Colors.GREEN}✓ Done{Colors.RESET}")
            successful += 1
        else:
            print(f" {Colors.RED}✗ Failed{Colors.RESET}")
            failed += 1
        
        print()  # Empty line between files
    
    # Print summary
    print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  {Colors.GREEN}✓ Successful: {successful}{Colors.RESET}")
    if skipped > 0:
        print(f"  {Colors.BLUE}↷ Skipped (already normalized): {skipped}{Colors.RESET}")
    if failed > 0:
        print(f"  {Colors.RED}✗ Failed: {failed}{Colors.RESET}")
    print(f"  Total files: {len(audio_files)}")
    print(f"\nNormalized files saved to: {Colors.BLUE}{output_dir}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")

if __name__ == '__main__':
    main()