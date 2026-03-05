import os
import sys
import toml
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(
    prefix="/api/scripts/{script_id}/characters",
    tags=["characters"]
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
        # print(f"[Characters] Checking for scripts at: {p}")
        if p.exists():
            BASE_DIR = p
            # print(f"[Characters] Found scripts at: {p}")
            break
    
    if BASE_DIR is None:
        BASE_DIR = exe_dir.parent.parent / "scripts"
        # print(f"[Characters] Defaulting scripts path to: {BASE_DIR}")
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
    # print(f"[Characters] Running from source. Scripts directory: {BASE_DIR}")

@router.get("/", response_model=List[str])
async def list_characters(script_id: str):
    script_dir = BASE_DIR / script_id
    chars_dir = script_dir / "Characters"

    # print(f"chars_dir:, ${chars_dir}")
    
    if not chars_dir.exists():
        return []
        
    characters = [name for name in os.listdir(chars_dir)]
    
    # for root, dirs, files in os.walk(chars_dir):
    #     for file in files:
    #         print(f"file:, ${file}")
    #         if file.endswith(".txt"):
    #             full_path = Path(root) / file
    #             try:
    #                 with open(full_path, "r", encoding="utf-8") as f:
    #                     data = toml.load(f)
                        
    #                 # Extract [role] table
    #                 if "role" in data:
    #                     role_info = data["role"]
    #                     role_info["_path"] = str(full_path.relative_to(chars_dir)).replace("\\", "/")
                        
    #                     # Ensure id exists
    #                     if "id" not in role_info:
    #                          role_info["id"] = "unknown_" + file
                             
    #                     characters.append(role_info)
    #             except Exception as e:
    #                 print(f"Error parsing {full_path}: {e}")
                    
    return characters