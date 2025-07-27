import time
import os
import sys

while True:
    exit_code = os.system(f"{sys.executable} main.py")
    print(f"\n[restarter] Bot exited with code {exit_code}. Restarting in 5 seconds...\n")
    time.sleep(5)