from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import OUTPUT_DIR

class ContentRenderer:
    def __init__(self):
        pass
        
    def save(self, content, student_id, topic):
        filename = f"module_{student_id}_{topic.replace(' ', '_')}.md"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Generated content saved to: {filepath}")
        return filepath
