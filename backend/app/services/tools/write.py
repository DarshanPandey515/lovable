from pathlib import Path
from app.services.config import safe_path


def write_file(path, content):
    
    path = safe_path(path)
    
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    
    path.write_text(content)
    
    
    return {
        "success": True,
        "path": str(path),
        "content_preview": content[:500]
    }