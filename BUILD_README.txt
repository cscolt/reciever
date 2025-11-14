================================================================================
  BUILDING DESKTOP CASTING RECEIVER - QUICK START
================================================================================

IMPORTANT: Run these commands from Windows PowerShell, NOT from WSL/Linux!

================================================================================
  QUICK BUILD (Python 3.11 or 3.12 recommended)
================================================================================

1. Open Windows PowerShell

2. Navigate to this folder:
   cd C:\Users\control\Documents\reciever-master\reciever-master

3. Run the build script:
   .\build_windows.ps1

   OR for Command Prompt:
   build_windows_simple.bat

================================================================================
  IF YOU HAVE PYTHON 3.14
================================================================================

Python 3.14 is too new. Most packages don't have pre-built wheels yet.

SOLUTION: Install Python 3.11
  1. Download: https://www.python.org/downloads/release/python-3119/
  2. Install (check "Add to PATH")
  3. Run: py -3.11 build_windows.ps1

================================================================================
  ALTERNATIVE: RUN WITHOUT BUILDING
================================================================================

If building fails, you can run directly from source:

  1. Open Windows PowerShell
  2. cd C:\Users\control\Documents\reciever-master\reciever-master
  3. .\venv\Scripts\Activate.ps1
  4. pip install -r requirements.txt
  5. python run.py

================================================================================
  FILES CREATED FOR YOU
================================================================================

  build_windows.ps1         - PowerShell build script (recommended)
  build_windows_simple.bat  - Batch file build script
  BUILD_GUIDE.md            - Complete build instructions
  BUILD_SUMMARY.md          - Detailed explanation of the situation
  TROUBLESHOOTING.md        - Common issues and solutions

================================================================================
  WHY NOT BUILD FROM WSL?
================================================================================

1. Python 3.14 is too new (needs older version or C++ compiler)
2. tkinter GUI doesn't work well in WSL
3. Cross-compilation from Linux to Windows is complex

================================================================================
  NEED HELP?
================================================================================

Read BUILD_GUIDE.md for detailed instructions and troubleshooting.

================================================================================
