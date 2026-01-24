import os
import toml
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(
    prefix="/api/scripts/{script_id}/characters",
    tags=["characters"]
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"

@router.get("/", response_model=List[Dict[str, Any]])
async def list_characters(script_id: str):
    script_dir = BASE_DIR / script_id
    chars_dir = script_dir / "Characters"
    
    if not chars_dir.exists():
        return []
        
    characters = []
    
    for root, dirs, files in os.walk(chars_dir):
        for file in files:
            if file.endswith(".toml"):
                full_path = Path(root) / file
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = toml.load(f)
                        
                    # Extract [role] table
                    if "role" in data:
                        role_info = data["role"]
                        role_info["_path"] = str(full_path.relative_to(chars_dir)).replace("\\", "/")
                        
                        # Ensure id exists
                        if "id" not in role_info:
                             role_info["id"] = "unknown_" + file
                             
                        characters.append(role_info)
                except Exception as e:
                    print(f"Error parsing {full_path}: {e}")
                    
    return characters
