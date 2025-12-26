"""
Automated script to replace deprecated use_container_width with width parameter
"""

import os
import re

def fix_file(filepath):
    """Fix use_container_width in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace width="stretch" with width="stretch"
        content = re.sub(
            r'use_container_width\s*=\s*True',
            'width="stretch"',
            content
        )
        
        # Replace width="content" with width="content"  
        content = re.sub(
            r'use_container_width\s*=\s*False',
            'width="content"',
            content
        )
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def fix_all_files():
    """Fix all Python files in components, calender directories"""
    fixed_count = 0
    
    directories = [
        'components',
        'calender',
        '.'  # Root directory for app.py
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for root, dirs, files in os.walk(directory):
            # Skip __pycache__ and other unnecessary directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if fix_file(filepath):
                        print(f"✅ Fixed: {filepath}")
                        fixed_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("🔧 Fixing deprecated use_container_width parameters...")
    print(f"{'='*60}\n")
    fix_all_files()
    print("\n✅ All done! You can now commit the changes.")
