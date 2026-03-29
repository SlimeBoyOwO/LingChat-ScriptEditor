import os
import sys
import yaml
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from ..models import ScriptConfig, Chapter, CreateScriptRequest

# Custom YAML handling for proper formatting
# 1. Removing null fields and duration with value 0.0, convert duration to number
def remove_null_fields(obj):
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # Skip null values
            if v is None:
                continue
            # Handle duration field specially
            if k == 'duration':
                # Convert to float if it's a string
                if isinstance(v, str):
                    try:
                        v = float(v)
                    except (ValueError, TypeError):
                        # drop the invalid value
                        v = 0.0
                # Skip if duration is 0 or 0.0
                if v == 0:
                    continue
            result[k] = remove_null_fields(v)
        return result
    elif isinstance(obj, list):
        return [remove_null_fields(item) for item in obj]
    return obj


# 2. Register custom representers
def str_representer(dumper, data):
    # Add | if there is multiline string
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_representer)

# 3. Add blank lines between list items (events) in YAML for better readability
def format_yaml_with_blank_lines(yaml_str: str) -> str:
    lines = yaml_str.split('\n')
    result = []
    
    for i, line in enumerate(lines):
        # Check if this line is a list item (starts with '- ')
        if line.startswith('- ') and i > 0:
            # Look back to find if there was a previous list item at the same level
            prev_idx = i - 1
            found_previous_list_item = False
            
            while prev_idx >= 0:
                prev_line = lines[prev_idx]
                if prev_line.startswith('- '):
                    # Found a previous list item at the same level
                    found_previous_list_item = True
                    break
                elif prev_line.strip() == '':
                    # Skip blank lines
                    prev_idx -= 1
                elif prev_line.startswith('  ') and not prev_line.startswith('- '):
                    # This is a nested property of a previous list item, keep looking back
                    prev_idx -= 1
                elif prev_line == 'events:':
                    # We've reached the events: header, no previous list item
                    break
                else:
                    # Some other line, stop looking
                    break
            
            # If we found a previous list item, add blank line before this one
            if found_previous_list_item:
                result.append('')
        
        result.append(line)
    
    return '\n'.join(result)

def convert_multiline_strings(obj):
    if isinstance(obj, dict):
        return {k: convert_multiline_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_multiline_strings(item) for item in obj]
    return obj

router = APIRouter(
    prefix="/api/scripts",
    tags=["scripts"]
)

# Determine the base directory for scripts
# When running as PyInstaller exe, look for scripts folder at the main app level
# When running from source, use the project's scripts folder
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
        # print(f"[Scripts] Checking for scripts at: {p}")
        if p.exists():
            BASE_DIR = p
            # print(f"[Scripts] Found scripts at: {p}")
            break
    
    if BASE_DIR is None:
        BASE_DIR = exe_dir.parent.parent / "scripts"
        # print(f"[Scripts] Defaulting scripts path to: {BASE_DIR}")
else:
    # Running from source
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
    #print(f"[Scripts] Running from source. Scripts directory: {BASE_DIR}")

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
    chapters_dir = script_dir / "Chapters"
    chapter_file = chapters_dir / chapter_path
    
    if not chapter_file.name.lower().endswith(".yaml") and not chapter_file.name.lower().endswith(".yml"):
        chapter_file = chapter_file.with_suffix(".yaml")
        
    chapter_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        chapter_data = chapter.model_dump()
        
        # 1. Remove all null fields from events
        chapter_data = remove_null_fields(chapter_data)
        
        # 2. Convert multiline strings to use literal block scalar
        chapter_data = convert_multiline_strings(chapter_data)
        
        # Generate YAML string first
        yaml_str = yaml.dump(chapter_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        # Add blank lines between events for readability
        yaml_str = format_yaml_with_blank_lines(yaml_str)
        
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(yaml_str)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{script_id}/chapters/{chapter_path:path}")
async def delete_chapter(script_id: str, chapter_path: str):
    script_dir = get_script_dir(script_id)
    
    chapters_dir = script_dir / "Chapters"
    if not chapters_dir.exists():
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
        (script_dir / "Assets").mkdir(exist_ok=True)

        # Create Assets subdirectories
        (script_dir / "Assets" / "Backgrounds").mkdir(exist_ok=True)
        (script_dir / "Assets" / "Musics").mkdir(exist_ok=True)
        (script_dir / "Assets" / "Sounds").mkdir(exist_ok=True)

        (script_dir / "Characters").mkdir(exist_ok=True)
        (script_dir / "Chapters").mkdir(exist_ok=True)
        
        # Create the intro chapter directory and file
        intro_chapter_path = Path(request.intro_chapter)
        intro_chapter_dir = script_dir / "Chapters" / intro_chapter_path.parent
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
            "intro_chapter": request.intro_chapter,
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
