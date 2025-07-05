#!/usr/bin/env python3
"""
Audio Verification - Verify normalized audio files meet broadcast standards

This script checks that all normalized files are properly normalized to -16 LUFS
and ensures no files are missing or have quality issues.

Usage: python3 verify_audio.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Target parameters with tolerance
TARGET_LUFS = -16.0
LUFS_TOLERANCE = 0.5
TARGET_TP = -1.0

def print_header(check_source=False):
    """Print script header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}Audio Verification{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    if check_source:
        print(f"Analyzing source files loudness levels")
    else:
        print(f"Checking normalized files against broadcast standards")
    print(f"{'='*50}\n")

def find_audio_files(directory: Path) -> List[Path]:
    """Find all audio files in directory recursively"""
    audio_extensions = {'.mp3', '.m4a', '.mp4', '.wav', '.flac', '.aac', '.ogg', '.wma'}
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(Path(root) / file)
    return sorted(audio_files)

def analyze_file(file_path: Path) -> Dict:
    """Analyze audio file and return loudness data"""
    cmd = [
        'ffmpeg', '-i', str(file_path),
        '-af', 'loudnorm=print_format=json',
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
            json_str = json_str[json_str.find('{'):json_str.rfind('}')+1]
            data = json.loads(json_str)
            return {
                'lufs': float(data.get('input_i', '-99')),
                'peak': float(data.get('input_tp', '-99')),
                'lra': float(data.get('input_lra', '0'))
            }
        else:
            return None
            
    except Exception as e:
        return None

def check_file_compliance(loudness_data: Dict) -> Tuple[bool, List[str]]:
    """Check if file meets broadcast standards"""
    issues = []
    
    if loudness_data is None:
        return False, ["Failed to analyze file"]
    
    lufs = loudness_data['lufs']
    peak = loudness_data['peak']
    
    # Check LUFS within tolerance
    if abs(lufs - TARGET_LUFS) > LUFS_TOLERANCE:
        issues.append(f"LUFS {lufs:.1f} (target: {TARGET_LUFS}±{LUFS_TOLERANCE})")
    
    # Check peak doesn't exceed limit
    if peak > TARGET_TP:
        issues.append(f"Peak {peak:.1f} dBTP exceeds {TARGET_TP} dBTP")
    
    return len(issues) == 0, issues

def main():
    """Main function"""
    # Check for --source flag
    check_source = '--source' in sys.argv
    if check_source:
        sys.argv.remove('--source')  # Remove flag from argv for file processing
    
    print_header(check_source)
    
    # Define directories
    base_dir = Path(__file__).parent
    source_dir = base_dir / 'mp3s'
    normalized_dir = base_dir / 'normalized'
    
    # Set target directory based on flag
    target_dir = source_dir if check_source else normalized_dir
    dir_name = "source" if check_source else "normalized"
    
    # Check directories exist
    if not target_dir.exists():
        print(f"{Colors.RED}Error: {dir_name.capitalize()} directory '{target_dir}' not found!{Colors.RESET}")
        if not check_source:
            print("Run normalize_audio.py first.")
        sys.exit(1)
    
    # Check for single file argument
    if len(sys.argv) > 1:
        # Single file mode
        file_path = sys.argv[1]
        audio_extensions = {'.mp3', '.m4a', '.mp4', '.wav', '.flac', '.aac', '.ogg', '.wma'}
        if not any(file_path.lower().endswith(ext) for ext in audio_extensions):
            print(f"{Colors.RED}Error: File must be an audio file (mp3, m4a, mp4, etc.)!{Colors.RESET}")
            sys.exit(1)
        
        # Find the file in target directory
        target_files = []
        # Look for the file with .mp3 extension (since all outputs are mp3)
        if check_source:
            # For source files, look for exact match
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file == os.path.basename(file_path) or str(Path(root) / file).endswith(file_path):
                        target_files.append(Path(root) / file)
                        break
        else:
            # For normalized files, look for .mp3 version
            search_name = Path(file_path).stem + '.mp3'
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file == search_name or file == os.path.basename(file_path) or str(Path(root) / file).endswith(file_path):
                        target_files.append(Path(root) / file)
                        break
        
        if not target_files:
            print(f"{Colors.RED}Error: File '{file_path}' not found in {target_dir}!{Colors.RESET}")
            sys.exit(1)
        
        print(f"{Colors.CYAN}Single file mode ({dir_name}): {target_files[0].relative_to(target_dir)}{Colors.RESET}")
        source_files = []  # Skip source comparison in single file mode
        normalized_files = target_files
    else:
        # Find files in directories
        print(f"{Colors.CYAN}Scanning {dir_name} directory...{Colors.RESET}")
        if check_source:
            normalized_files = find_audio_files(source_dir)
            source_files = []  # No comparison when checking source
        else:
            source_files = find_audio_files(source_dir) if source_dir.exists() else []
            normalized_files = find_audio_files(normalized_dir)
    
    # Check file counts
    if check_source:
        print(f"\n{dir_name.capitalize()} files: {Colors.BLUE}{len(normalized_files)}{Colors.RESET}")
    else:
        print(f"\nSource files: {Colors.BLUE}{len(source_files)}{Colors.RESET}")
        print(f"Normalized files: {Colors.BLUE}{len(normalized_files)}{Colors.RESET}")
    
    if len(normalized_files) == 0:
        print(f"\n{Colors.YELLOW}No {dir_name} files found!{Colors.RESET}")
        sys.exit(0)
    
    # Analyze each file
    print(f"\n{Colors.CYAN}Analyzing {dir_name} files...{Colors.RESET}\n")
    
    compliant_files = 0
    non_compliant_files = []
    failed_files = []
    
    for i, file_path in enumerate(normalized_files, 1):
        relative_path = file_path.relative_to(target_dir)
        print(f"{Colors.YELLOW}[{i}/{len(normalized_files)}]{Colors.RESET} {relative_path}")
        
        # Analyze file
        loudness_data = analyze_file(file_path)
        is_compliant, issues = check_file_compliance(loudness_data)
        
        if loudness_data is None:
            print(f"  {Colors.RED}✗ Failed to analyze{Colors.RESET}")
            failed_files.append(str(relative_path))
        elif is_compliant:
            lufs = loudness_data['lufs']
            peak = loudness_data['peak']
            print(f"  {Colors.GREEN}✓{Colors.RESET} LUFS: {Colors.GREEN}{lufs:.1f}{Colors.RESET} (target: {TARGET_LUFS}±{LUFS_TOLERANCE}) | Peak: {Colors.GREEN}{peak:.1f}{Colors.RESET} dBTP")
            compliant_files += 1
        else:
            lufs = loudness_data['lufs']
            peak = loudness_data['peak']
            print(f"  {Colors.RED}✗{Colors.RESET} LUFS: {Colors.RED}{lufs:.1f}{Colors.RESET} (target: {TARGET_LUFS}±{LUFS_TOLERANCE}) | Peak: {Colors.RED if peak > TARGET_TP else Colors.YELLOW}{peak:.1f}{Colors.RESET} dBTP")
            for issue in issues:
                print(f"    {Colors.YELLOW}→ {issue}{Colors.RESET}")
            non_compliant_files.append((str(relative_path), issues, loudness_data))
        
        print()  # Empty line between files
    
    # Print summary
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}Summary:{Colors.RESET}\n")
    
    # File count check
    if source_files and len(source_files) == len(normalized_files):
        print(f"{Colors.GREEN}✓ File count matches source ({len(normalized_files)} files){Colors.RESET}")
    elif source_files:
        print(f"{Colors.YELLOW}⚠ File count mismatch: {len(source_files)} source, {len(normalized_files)} normalized{Colors.RESET}")
    
    # Compliance check
    total_checked = len(normalized_files) - len(failed_files)
    if compliant_files == total_checked and total_checked > 0:
        print(f"{Colors.GREEN}✓ All files at target loudness (-16 LUFS ±{LUFS_TOLERANCE}){Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ {compliant_files}/{total_checked} files compliant{Colors.RESET}")
    
    # Peak check (included in compliance)
    print(f"{Colors.GREEN}✓ Peak levels checked (limit: {TARGET_TP} dBTP){Colors.RESET}")
    
    # Don't repeat non-compliant files since we already showed them above
    
    # Show failed files if any
    if failed_files:
        print(f"\n{Colors.RED}Failed to analyze:{Colors.RESET}")
        for file_path in failed_files[:5]:
            print(f"  • {file_path}")
        if len(failed_files) > 5:
            print(f"  ... and {len(failed_files) - 5} more")
    
    # Summary
    print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
    if compliant_files == len(normalized_files):
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All files ready for stage performance!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some files need attention{Colors.RESET}")
        print(f"Consider re-running normalize_audio.py")
    print()

if __name__ == '__main__':
    main()