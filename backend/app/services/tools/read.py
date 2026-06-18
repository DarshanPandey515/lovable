from pathlib import Path
from app.services.config import safe_path


def read_file(path):
    
    path = safe_path(path)
    
    if not path.exists():
        raise FileNotFoundError(path)
    
    return path.read_text()


def get_tree(root="."):
    
    lines = []
    
    for path in Path(root).rglob("*"):
        
        if ".git" in path.parts:
            continue
        
        if "__pycache__" in path.parts:
            continue
        
        if "env" in path.parts:
            continue
        
        lines.append(str(path))
        
        
    return "\n".join(lines)