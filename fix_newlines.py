import os
import glob

base_dir = r"c:\xampp\htdocs\ARN 2026\api"
files = glob.glob(os.path.join(base_dir, "**", "*.php"), recursive=True)
count = 0

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clean up right side completely
    # First rstrip all whitespace
    cleaned = content.rstrip(' \n\r\t')
    
    # Then repeatedly remove literal \n if present
    while cleaned.endswith('\\n'):
        cleaned = cleaned[:-2]
        
    cleaned = cleaned.rstrip(' \n\r\t')
    
    if content != cleaned:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        count += 1

print(f"Archivos corregidos: {count}")
