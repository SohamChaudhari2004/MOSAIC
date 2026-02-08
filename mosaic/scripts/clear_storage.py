#!/usr/bin/env python3
"""
Clear Storage Script for Mosaic Video Analyzer

This script clears all storage directories in the Mosaic codebase including:
- Uploaded videos (mosaic-api/app/storage/uploads/)
- Extracted frames (mosaic-mcp/src/storage/frames/)
- ChromaDB vector database (mosaic-mcp/src/chroma_db/)
- Generated video clips (mosaic-mcp/src/clips_output/)
- Additional extracted frames directories

Usage:
    python clear_storage.py [--dry-run] [--confirm]
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List, Dict

# Get the base directory (mosaic root)
SCRIPT_DIR = Path(__file__).parent.absolute()
BASE_DIR = SCRIPT_DIR.parent

# Define all storage directories relative to the base directory
STORAGE_DIRS = [
    # API storage
    "mosaic-api/app/storage/uploads",
    "mosaic-api/app/storage/media_uploads",
    "mosaic-api/uploads",
    
    # MCP storage
    "mosaic-mcp/src/storage/frames",
    "mosaic-mcp/src/chroma_db",
    "mosaic-mcp/src/clips_output",
    "mosaic-mcp/src/mosaic/extracted_frames",
    
    # Root level extracted frames
    "extracted_frames",
]

# Files to preserve (e.g., .gitkeep files)
PRESERVE_FILES = [".gitkeep", ".gitignore"]


def get_dir_size(path: Path) -> int:
    """Calculate the total size of a directory in bytes."""
    total = 0
    if path.exists() and path.is_dir():
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def clear_directory(dir_path: Path, preserve_files: List[str] = None, dry_run: bool = False) -> Dict:
    """
    Clear contents of a directory while optionally preserving certain files.
    
    Args:
        dir_path: Path to the directory to clear
        preserve_files: List of filenames to preserve
        dry_run: If True, don't actually delete anything
        
    Returns:
        Dictionary with statistics about the operation
    """
    preserve_files = preserve_files or []
    stats = {
        "path": str(dir_path),
        "exists": dir_path.exists(),
        "files_deleted": 0,
        "dirs_deleted": 0,
        "size_freed": 0,
        "preserved": [],
        "errors": []
    }
    
    if not dir_path.exists():
        return stats
    
    if not dir_path.is_dir():
        stats["errors"].append(f"{dir_path} is not a directory")
        return stats
    
    # Calculate size before clearing
    stats["size_freed"] = get_dir_size(dir_path)
    
    # Get all items in the directory
    try:
        for item in dir_path.iterdir():
            if item.name in preserve_files:
                stats["preserved"].append(item.name)
                continue
            
            try:
                if item.is_dir():
                    if not dry_run:
                        shutil.rmtree(item)
                    stats["dirs_deleted"] += 1
                else:
                    if not dry_run:
                        item.unlink()
                    stats["files_deleted"] += 1
            except Exception as e:
                stats["errors"].append(f"Error deleting {item}: {e}")
    except Exception as e:
        stats["errors"].append(f"Error accessing {dir_path}: {e}")
    
    return stats


def clear_all_storage(base_dir: Path = None, dry_run: bool = False, silent: bool = False) -> Dict:
    """
    Clear all storage directories in the Mosaic codebase.
    
    Args:
        base_dir: Base directory of the mosaic project (defaults to parent of scripts/)
        dry_run: If True, don't actually delete anything
        silent: If True, don't print output
        
    Returns:
        Dictionary with overall statistics
    """
    if base_dir is None:
        base_dir = BASE_DIR
    
    overall_stats = {
        "base_dir": str(base_dir),
        "dry_run": dry_run,
        "directories_processed": 0,
        "total_files_deleted": 0,
        "total_dirs_deleted": 0,
        "total_size_freed": 0,
        "directory_stats": [],
        "errors": []
    }
    
    if not silent:
        mode = "[DRY RUN] " if dry_run else ""
        print(f"\n{mode}Clearing Mosaic storage directories...")
        print(f"Base directory: {base_dir}\n")
        print("-" * 60)
    
    for rel_path in STORAGE_DIRS:
        dir_path = base_dir / rel_path
        
        if not silent:
            print(f"\nProcessing: {rel_path}")
        
        stats = clear_directory(dir_path, PRESERVE_FILES, dry_run)
        overall_stats["directory_stats"].append(stats)
        
        if stats["exists"]:
            overall_stats["directories_processed"] += 1
            overall_stats["total_files_deleted"] += stats["files_deleted"]
            overall_stats["total_dirs_deleted"] += stats["dirs_deleted"]
            overall_stats["total_size_freed"] += stats["size_freed"]
            
            if not silent:
                print(f"  Status: Found")
                print(f"  Files deleted: {stats['files_deleted']}")
                print(f"  Directories deleted: {stats['dirs_deleted']}")
                print(f"  Size freed: {format_size(stats['size_freed'])}")
                if stats["preserved"]:
                    print(f"  Preserved: {', '.join(stats['preserved'])}")
                if stats["errors"]:
                    for error in stats["errors"]:
                        print(f"  ERROR: {error}")
        else:
            if not silent:
                print(f"  Status: Not found (skipped)")
        
        overall_stats["errors"].extend(stats["errors"])
    
    if not silent:
        print("\n" + "-" * 60)
        print(f"\n{mode}Summary:")
        print(f"  Directories processed: {overall_stats['directories_processed']}")
        print(f"  Total files deleted: {overall_stats['total_files_deleted']}")
        print(f"  Total directories deleted: {overall_stats['total_dirs_deleted']}")
        print(f"  Total space freed: {format_size(overall_stats['total_size_freed'])}")
        
        if overall_stats["errors"]:
            print(f"\n  Errors encountered: {len(overall_stats['errors'])}")
        
        print()
    
    return overall_stats


def main():
    parser = argparse.ArgumentParser(
        description="Clear all storage directories in the Mosaic Video Analyzer"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base directory of the Mosaic project"
    )
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir) if args.base_dir else BASE_DIR
    
    if not args.dry_run and not args.confirm:
        print("\n⚠️  WARNING: This will permanently delete all stored data including:")
        print("   - Uploaded videos")
        print("   - Extracted frames")
        print("   - Vector database (ChromaDB)")
        print("   - Generated video clips")
        print()
        response = input("Are you sure you want to continue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    stats = clear_all_storage(base_dir, dry_run=args.dry_run)
    
    if stats["errors"]:
        exit(1)


if __name__ == "__main__":
    main()
