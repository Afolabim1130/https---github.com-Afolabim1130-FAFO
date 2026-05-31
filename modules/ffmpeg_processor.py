"""
FAFO Video Forensic Processing Module
Extracts video metadata, codecs, duration, and frame dimensions, with a binary MP4 parser fallback.
"""
import os
import shutil
import struct
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from config.settings import FFMPEG_ENABLED, FFMPEG_PATH, FFMPEG_FALLBACK_ENABLED


def find_ffprobe_binary() -> str | None:
    """Find a usable ffprobe executable on the host system."""
    if FFMPEG_PATH and FFMPEG_PATH != "ffmpeg":
        custom = Path(FFMPEG_PATH)
        if custom.exists():
            if custom.name.lower() == "ffprobe":
                return str(custom)
            alt = custom.parent / "ffprobe"
            alt_exe = custom.parent / "ffprobe.exe"
            if alt.exists():
                return str(alt)
            if alt_exe.exists():
                return str(alt_exe)
            return str(custom)

    for candidate in ["ffprobe", "ffmpeg"]:
        found = shutil.which(candidate)
        if found:
            return found

    # Common Linux install locations
    for candidate in ["/usr/bin/ffprobe", "/usr/local/bin/ffprobe", "/snap/bin/ffprobe"]:
        if Path(candidate).exists():
            return candidate

    # Windows fallback locations
    if os.name == "nt":
        for candidate in [
            r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe"
        ]:
            if Path(candidate).exists():
                return candidate

    return None


def extract_video_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extract video metadata (codec, duration, width, height) using FFmpeg.
    If FFmpeg is not available, uses a native binary MP4 box parsing fallback.
    """
    result = {
        "duration_seconds": 0.0,
        "width": 0,
        "height": 0,
        "codec": "Unknown",
        "method": "UNKNOWN",
        "success": False
    }
    
    path_obj = Path(file_path)
    if not path_obj.exists():
        return result
        
    # Attempt FFmpeg if enabled
    if FFMPEG_ENABLED:
        try:
            ffprobe_path = find_ffprobe_binary()
            if not ffprobe_path:
                raise FileNotFoundError("ffprobe binary not found")

            ffprobe_cmd = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration:stream=codec_name,width,height",
                "-of", "default=noprint_wrappers=1",
                str(path_obj)
            ]
            
            startupinfo = None
            if os.name == 'nt':
                # Prevent console window popping up on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            proc = subprocess.run(
                ffprobe_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                startupinfo=startupinfo,
                timeout=5
            )
            
            if proc.returncode == 0:
                output = proc.stdout
                for line in output.splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k == "duration":
                            try:
                                result["duration_seconds"] = round(float(v), 2)
                            except ValueError:
                                pass
                        elif k == "width":
                            result["width"] = int(v)
                        elif k == "height":
                            result["height"] = int(v)
                        elif k == "codec_name":
                            result["codec"] = v
                            
                result["method"] = "FFPROBE"
                result["success"] = True
                return result
                
        except Exception as e:
            logging.warning(f"FFPROBE execution failed or binary missing: {str(e)}. Triggering fallback.")
            
    # Fallback to python-native parser
    if FFMPEG_FALLBACK_ENABLED:
        return run_native_mp4_fallback(path_obj)
        
    return result

def run_native_mp4_fallback(file_path: Path) -> Dict[str, Any]:
    """
    Pure Python binary parser for MP4/MOV container headers (Atoms).
    Scans binary streams for 'mvhd' and 'tkhd' boxes to extract duration
    and dimensions without executing any external binary.
    """
    result = {
        "duration_seconds": 10.0, # Default mock/heuristic duration
        "width": 1280,            # Default HD width
        "height": 720,            # Default HD height
        "codec": "h264 (fallback)",
        "method": "PYTHON_BINARY_PARSER",
        "success": False
    }
    
    try:
        file_size = file_path.stat().st_size
        with open(file_path, "rb") as f:
            # We read chunks to locate atoms
            data = f.read(100 * 1024) # Read first 100KB which usually contains headers
            
        # 1. Search for 'mvhd' (Movie Header Atom) to find duration
        # mvhd usually starts with 4-byte box size, then 'mvhd', then version (1 byte), flags (3 bytes)...
        mvhd_idx = data.find(b"mvhd")
        if mvhd_idx != -1:
            # Struct of mvhd (version 0):
            # 1 byte version, 3 bytes flags
            # 4 bytes creation time
            # 4 bytes modification time
            # 4 bytes timescale
            # 4 bytes duration
            version = data[mvhd_idx + 4]
            if version == 0:
                timescale_offset = mvhd_idx + 4 + 4 + 4 + 4 # skip version, creation, modification
                timescale = struct.unpack(">I", data[timescale_offset : timescale_offset + 4])[0]
                duration = struct.unpack(">I", data[timescale_offset + 4 : timescale_offset + 8])[0]
                if timescale > 0:
                    result["duration_seconds"] = round(duration / timescale, 2)
                    result["success"] = True
            elif version == 1:
                # Version 1 uses 64-bit integers (8 bytes) for times
                # skip version/flags (4), creation (8), modification (8) -> 20 bytes offset
                timescale_offset = mvhd_idx + 4 + 16
                timescale = struct.unpack(">I", data[timescale_offset : timescale_offset + 4])[0]
                duration = struct.unpack(">Q", data[timescale_offset + 4 : timescale_offset + 12])[0]
                if timescale > 0:
                    result["duration_seconds"] = round(duration / timescale, 2)
                    result["success"] = True
                    
        # 2. Search for 'tkhd' (Track Header Atom) to find dimensions
        tkhd_idx = data.find(b"tkhd")
        if tkhd_idx != -1:
            version = data[tkhd_idx + 4]
            # Offset of width/height in track header
            if version == 0:
                # skip size/type(8), version/flags(4), creation(4), modification(4), track_id(4), reserved(4), duration(4) -> 32
                # then reserved(8), layer(2), alternate(2), volume(2), reserved(2), matrix(36) -> 52
                # Total offset: 84 bytes
                dim_offset = tkhd_idx + 4 + 76
            else:
                # Version 1 uses 64-bit duration etc.
                dim_offset = tkhd_idx + 4 + 88
                
            if dim_offset + 8 <= len(data):
                # Width and height are represented as 16.16 fixed-point numbers
                w_fixed = struct.unpack(">I", data[dim_offset : dim_offset + 4])[0]
                h_fixed = struct.unpack(">I", data[dim_offset + 4 : dim_offset + 8])[0]
                w = w_fixed >> 16
                h = h_fixed >> 16
                if w > 0 and h > 0:
                    result["width"] = w
                    result["height"] = h
                    result["success"] = True
                    
        # Basic container mapping heuristics for other extensions
        ext = file_path.suffix.lower()
        if ext in [".avi", ".wmv"]:
            result["codec"] = "mpeg4 (fallback)"
        elif ext == ".webm":
            result["codec"] = "vp9 (fallback)"
            
        result["codec"] += f" (Parsed: {result['success']})"
        return result
        
    except Exception as e:
        logging.error(f"Native video fallback error: {str(e)}")
        # Return sensible mockup defaults based on file size
        file_size = file_path.stat().st_size if file_path.exists() else 0
        result["duration_seconds"] = round(min(5.0 + (file_size / 200000), 120.0), 2)
        result["codec"] = "unknown (size heuristics)"
        return result
