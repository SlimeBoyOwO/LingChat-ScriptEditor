import os
import yaml
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from ..models import ScriptConfig, Chapter, CreateScriptRequest
router = APIRouter(
    prefix="/api/scripts",
    tags=["scripts"]
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"

def get_script_dir(script_id: str) -> Path:
    script_dir = BASE_DIR / script_id
    if not script_dir.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    return script_dir

@router.get("/", response_model=List[ScriptConfig])
async def list_scripts():
    scripts = []
    if not BASE_DIR.exists():
        return []
    
    for item in BASE_DIR.iterdir():
        print(item)
        if item.is_dir():
            config_path = item / "story_config.yaml"
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            data['id'] = item.name
                            scripts.append(data)
                except Exception as e:
                    print(f"Failed to load {config_path}: {e}")
    return scripts

@router.get("/{script_id}", response_model=ScriptConfig)
async def get_script(script_id: str):
    script_dir = get_script_dir(script_id)
    config_path = script_dir / "story_config.yaml"
    
    if not config_path.exists():
         raise HTTPException(status_code=404, detail="Config not found")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            data['id'] = script_id
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{script_id}/chapters")
async def list_chapters(script_id: str):
    script_dir = get_script_dir(script_id)
    # Check for likely names, user has 'Charpters' on disk, but we should be robust
    chapters_dir = script_dir / "Charpters"
    if not chapters_dir.exists():
        # Fallback check
        if (script_dir / "Chapters").exists():
            chapters_dir = script_dir / "Chapters"
    
    if not chapters_dir.exists():
        return []
    
    chapters = []
    for root, dirs, files in os.walk(chapters_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(chapters_dir)
                chapters.append(str(rel_path).replace("\\", "/"))
    return chapters

@router.get("/{script_id}/chapters/{chapter_path:path}")
async def get_chapter(script_id: str, chapter_path: str):
    script_dir = get_script_dir(script_id)
    
    # Try Charpters/ first
    chapters_dir = script_dir / "Charpters"
    if not chapters_dir.exists():
        chapters_dir = script_dir / "Chapters"
    
    chapter_file = chapters_dir / chapter_path
    
    if not chapter_file.name.lower().endswith(".yaml") and not chapter_file.name.lower().endswith(".yml"):
        chapter_file = chapter_file.with_suffix(".yaml")

    if not chapter_file.exists():
         # Try yml if yaml failed
         if chapter_file.suffix == ".yaml":
             chapter_file = chapter_file.with_suffix(".yml")
         
         if not chapter_file.exists():
            raise HTTPException(status_code=404, detail=f"Chapter file not found: {chapter_path}")

    try:
        with open(chapter_file, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{script_id}/chapters/{chapter_path:path}")
async def save_chapter(script_id: str, chapter_path: str, chapter: Chapter):
    script_dir = get_script_dir(script_id)
    
    chapters_dir = script_dir / "Charpters"
    if not chapters_dir.exists():
        if (script_dir / "Chapters").exists():
            chapters_dir = script_dir / "Chapters"
        else:
            # Default to Charpters if creating new? Or stick to existing? 
            # If neither exists, create Charpters as per user spec
            chapters_dir = script_dir / "Charpters"
    
    chapter_file = chapters_dir / chapter_path
    
    if not chapter_file.name.lower().endswith(".yaml") and not chapter_file.name.lower().endswith(".yml"):
        chapter_file = chapter_file.with_suffix(".yaml")
        
    chapter_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(chapter_file, "w", encoding="utf-8") as f:
            # Use allow_unicode=True for Chinese support
            yaml.dump(chapter.model_dump(), f, allow_unicode=True, sort_keys=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{script_id}/chapters/{chapter_path:path}")
async def delete_chapter(script_id: str, chapter_path: str):
    script_dir = get_script_dir(script_id)
    
    chapters_dir = script_dir / "Charpters"
    if not chapters_dir.exists():
        if (script_dir / "Chapters").exists():
            chapters_dir = script_dir / "Chapters"
        else:
            raise HTTPException(status_code=404, detail="Chapters directory not found")
    
    chapter_file = chapters_dir / chapter_path
    
    if not chapter_file.name.lower().endswith(".yaml") and not chapter_file.name.lower().endswith(".yml"):
        chapter_file = chapter_file.with_suffix(".yaml")
    
    if not chapter_file.exists():
        # Try .yml extension if .yaml didn't work
        if chapter_file.suffix == ".yaml":
            chapter_file = chapter_file.with_suffix(".yml")
        
        if not chapter_file.exists():
            raise HTTPException(status_code=404, detail=f"Chapter file not found: {chapter_path}")
    
    try:
        chapter_file.unlink()
        return {"status": "success", "message": f"Chapter {chapter_path} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chapter: {str(e)}")

@router.post("/create")
async def create_script(request: CreateScriptRequest):
    script_name = request.name
    script_dir = BASE_DIR / script_name
    
    # Check if script already exists
    if script_dir.exists():
        raise HTTPException(status_code=400, detail="Script with this name already exists")
    
    try:
        # Create directory structure
        script_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (script_dir / "Assests").mkdir(exist_ok=True)
        (script_dir / "Characters").mkdir(exist_ok=True)
        (script_dir / "Charpters").mkdir(exist_ok=True)
        
        # Create the intro chapter directory and file
        intro_chapter_path = Path(request.intro_chapter)
        intro_chapter_dir = script_dir / "Charpters" / intro_chapter_path.parent
        intro_chapter_dir.mkdir(parents=True, exist_ok=True)
        
        # Create empty YAML file for the intro chapter
        intro_chapter_file = intro_chapter_dir / intro_chapter_path.name
        if not intro_chapter_file.suffix:
            intro_chapter_file = intro_chapter_file.with_suffix(".yaml")
        
        # Create empty chapter with events array
        empty_chapter = {"events": []}
        with open(intro_chapter_file, "w", encoding="utf-8") as f:
            yaml.dump(empty_chapter, f, allow_unicode=True, sort_keys=False)
        
        # Create story_config.yaml with the specified format
        story_config_path = script_dir / "story_config.yaml"
        story_config = {
            "script_name": script_name,
            "intro_charpter": request.intro_chapter,
            "description": request.description,
            "script_settings": {
                "user_name": request.user_name,
                "user_subtitle": request.user_subtitle
            }
        }
        
        with open(story_config_path, "w", encoding="utf-8") as f:
            yaml.dump(story_config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        
        return {
            "status": "success",
            "message": f"Script '{script_name}' created successfully",
            "script_id": script_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create script: {str(e)}")
