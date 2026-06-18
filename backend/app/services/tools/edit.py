from pathlib import Path
from app.services.config import safe_path

def edit_file(path, old_text, new_text):
    
    path = safe_path(path)
    content = path.read_text()
    
    if old_text not in content:
        return {
            "success": False,
            "error": "text not found"
        }
    
    updated = content.replace(
        old_text,
        new_text,
        1
    )
    
    path.write_text(updated)
    
    return {
        "success": True,
        "path": str(path)
    }