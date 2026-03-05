import os
import yaml
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import sys

router = APIRouter(
    prefix="/api/preview",
    tags=["preview"]
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
        # print(f"[Preview] Checking for scripts at: {p}")
        if p.exists():
            BASE_DIR = p
            # print(f"[Preview] Found scripts at: {p}")
            break
    
    if BASE_DIR is None:
        BASE_DIR = exe_dir.parent.parent / "scripts"
        # print(f"[Preview] Defaulting scripts path to: {BASE_DIR}")
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
    # print(f"[Preview] Running from source. Scripts directory: {BASE_DIR}")

def get_script_dir(script_id: str) -> Path:
    script_dir = BASE_DIR / script_id
    if not script_dir.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    return script_dir

@router.get("/{script_id}/data")
async def get_preview_data(script_id: str):
    """Get all data needed for preview: config, chapters, and assets list"""
    script_dir = get_script_dir(script_id)
    
    # Load story config
    config_path = script_dir / "story_config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    
    # Load all chapters
    chapters_dir = script_dir / "Chapters"
    chapters = {}
    if chapters_dir.exists():
        for root, dirs, files in os.walk(chapters_dir):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    full_path = Path(root) / file
                    rel_path = str(full_path.relative_to(chapters_dir)).replace("\\", "/")
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            chapters[rel_path] = yaml.safe_load(f) or {"events": []}
                    except Exception as e:
                        chapters[rel_path] = {"events": [], "error": str(e)}
    
    # Get assets (images, music, etc.) from both Assets and Characters folders
    assets = {}
    
    # Scan Assets folder if exists
    assets_dir = script_dir / "Assets"
    if assets_dir.exists():
        for root, dirs, files in os.walk(assets_dir):
            rel_root = Path(root).relative_to(assets_dir)
            for file in files:
                full_rel_path = str((rel_root / file).as_posix())
                assets[full_rel_path] = f"/api/preview/{script_id}/assets/{full_rel_path}"
    
    # Scan Characters folder for avatar images
    characters_dir = script_dir / "Characters"
    if characters_dir.exists():
        for char_folder in characters_dir.iterdir():
            if char_folder.is_dir():
                char_name = char_folder.name
                avatar_dir = char_folder / "avatar"
                if avatar_dir.exists():
                    for file in avatar_dir.iterdir():
                        if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                            # Store with multiple keys for easy lookup
                            emotion = file.stem  # filename without extension
                            key = f"Characters/{char_name}"
                            assets[key] = f"/api/preview/{script_id}/character/{char_name}"
                            assets[f"{char_name}"] = f"/api/preview/{script_id}/character/{char_name}"
                            assets[f"Characters/{char_name}/avatar/{emotion}"] = f"/api/preview/{script_id}/character/{char_name}/{emotion}"
    
    # Get character definitions
    characters = []
    if characters_dir.exists():
        for char_folder in characters_dir.iterdir():
            if char_folder.is_dir():
                char_name = char_folder.name
                # Check for settings.txt or any config file
                settings_file = char_folder / "settings.txt"
                character_info = {"id": char_name, "name": char_name}
                
                # Also add any avatar images info
                avatar_dir = char_folder / "avatar"
                if avatar_dir.exists():
                    emotions = [f.stem for f in avatar_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
                    character_info["emotions"] = emotions
                
                characters.append(character_info)
    
    return {
        "config": config,
        "chapters": chapters,
        "assets": assets,
        "characters": characters
    }

@router.get("/{script_id}/assets/{asset_path:path}")
async def get_asset(script_id: str, asset_path: str):
    """Serve an asset file"""
    script_dir = get_script_dir(script_id)
    asset_file = script_dir / "Assets" / asset_path
    
    if asset_file.exists():
        return FileResponse(asset_file)
    
    # Try to find in subdirectories
    for root, dirs, files in os.walk(script_dir / "Assets"):
        for file in files:
            if file == asset_path or file.endswith(asset_path):
                return FileResponse(Path(root) / file)
    
    raise HTTPException(status_code=404, detail=f"Asset not found: {asset_path}")


@router.get("/{script_id}/character/{character_id}/{emotion}")
async def get_character_emotion_image(script_id: str, character_id: str, emotion: str = "正常"):
    """Serve a character emotion image"""
    script_dir = get_script_dir(script_id)
    
    # Try Characters/{character_id}/avatar/{emotion}.png
    avatar_path = script_dir / "Characters" / character_id / "avatar" / f"{emotion}.png"
    if avatar_path.exists():
        return FileResponse(avatar_path)
    
    # Try with .jpg extension
    avatar_path_jpg = script_dir / "Characters" / character_id / "avatar" / f"{emotion}.jpg"
    if avatar_path_jpg.exists():
        return FileResponse(avatar_path_jpg)
    
    # Fallback to "正常" or first available emotion
    avatar_dir = script_dir / "Characters" / character_id / "avatar"
    if avatar_dir.exists():
        # Try "正常" first as default
        normal_path = avatar_dir / "正常.png"
        if normal_path.exists():
            return FileResponse(normal_path)
        
        # Find first available image
        for file in avatar_dir.iterdir():
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                return FileResponse(file)
    
    raise HTTPException(status_code=404, detail=f"Character image not found: {character_id}/{emotion}")


@router.get("/{script_id}/character/{character_id}")
async def get_character_image(script_id: str, character_id: str):
    """Serve a character's default image"""
    script_dir = get_script_dir(script_id)
    
    # Try Characters/{character_id}/avatar/正常.png (or similar default)
    avatar_dir = script_dir / "Characters" / character_id / "avatar"
    
    if avatar_dir.exists():
        # Try common default emotions
        for default_name in ["正常"]:
            for ext in [".png", ".jpg", ".jpeg"]:
                default_path = avatar_dir / f"{default_name}{ext}"
                if default_path.exists():
                    return FileResponse(default_path)
        
        # Fallback to first available image
        for file in avatar_dir.iterdir():
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                return FileResponse(file)
    
    raise HTTPException(status_code=404, detail=f"Character image not found: {character_id}")

@router.get("/{script_id}/character/{character_id}/{emotion}")
async def get_character_image(script_id: str, character_id: str, emotion: str):
    script_dir = get_script_dir(script_id)
    avatar_dir = script_dir / "Characters" / character_id / "avatar"
    
    if avatar_dir.exists():
        for ext in [".png", ".jpg", ".jpeg"]:
            default_path = avatar_dir / f"{emotion}{ext}"
            if default_path.exists():
                return FileResponse(default_path)

    raise HTTPException(status_code=404, detail=f"Character image not found: {character_id}")