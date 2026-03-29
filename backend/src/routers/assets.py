import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, List

router = APIRouter(
    prefix="/api/scripts/{script_id}/assets",
    tags=["assets"]
)

# Determine the base directory for scripts - same logic as scripts.py
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    exe_dir = Path(sys.executable).parent
    
    # Try multiple possible locations for scripts folder
    possible_paths = [
        exe_dir.parent.parent / "scripts",  # win-unpacked/scripts/ (portable)
        exe_dir / "scripts",                 # resources/backend/scripts/
        exe_dir.parent / "scripts",          # resources/scripts/
    ]
    
    BASE_DIR = None
    for p in possible_paths:
        # print(f"[Assets] Checking for scripts at: {p}")
        if p.exists():
            BASE_DIR = p
            # print(f"[Assets] Found scripts at: {p}")
            break
    
    if BASE_DIR is None:
        BASE_DIR = exe_dir.parent.parent / "scripts"
        # print(f"[Assets] Defaulting scripts path to: {BASE_DIR}")
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
    # print(f"[Assets] Running from source. Scripts directory: {BASE_DIR}")

@router.get("/", response_model=Dict[str, List[str]])
async def list_assets(script_id: str):
    script_dir = BASE_DIR / script_id
    if not script_dir.exists():
         raise HTTPException(status_code=404, detail="Script not found")
         
    assets_dir = script_dir / "Assets"
    assets = {
        "Backgrounds": [],
        "Musics": [],
        "Sounds": [],
        "Effects": [],
        "Other": []
    }
    
    if not assets_dir.exists():
         return assets

    for root, dirs, files in os.walk(assets_dir):
        rel_root = Path(root).relative_to(assets_dir)
        parts = rel_root.parts
        
        category = "Other"
        if len(parts) > 0:
            top_folder = parts[0]
            # Use top folder as category
            category = top_folder
            if category not in assets:
                assets[category] = []
        
        # Files in root of Assets go to 'Other' unless we mapped them
        if len(parts) == 0:
            category = "Other"

        for file in files:
            # Full path relative to Assets root
            full_rel_path = (rel_root / file).as_posix()
            if full_rel_path.startswith("./"):
                full_rel_path = full_rel_path[2:]
            
            assets[category].append(full_rel_path)
            
    return assets
