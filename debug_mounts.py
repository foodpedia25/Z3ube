import os
try:
    print(f"Current CWD: {os.getcwd()}")
except Exception as e:
    print(f"CWD Error: {e}")

try:
    print(f"Votes in /Volumes: {os.listdir('/Volumes')}")
except Exception as e:
    print(f"List /Volumes Error: {e}")
