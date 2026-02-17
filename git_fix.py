import os
import subprocess
import sys

target_dir = "/Volumes/BUFFALO/Z3ube"

try:
    print(f"Attempting to switch to {target_dir}")
    os.chdir(target_dir)
    print(f"Successfully changed to: {os.getcwd()}")
    
    commands = [
        ["git", "add", "core/reasoning_engine.py", "DEPLOYMENT.md", "README.md"],
        ["git", "commit", "-m", "feat: Upgrade to Gemini 3 Flash model"],
        ["git", "push", "origin", "main"]
    ]
    
    for cmd in commands:
        print(f"\nRunning: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
            
except Exception as e:
    print(f"Critical Error: {e}")
    sys.exit(1)
