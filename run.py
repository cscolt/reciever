#!/usr/bin/env python3
"""
Desktop Casting Receiver - Main Entry Point
Simple launcher for the application
"""

import sys
import os

# Add src directory to path for development mode
sys.path.insert(0, os.path.dirname(__file__))

from src import main

if __name__ == '__main__':
    # Check for headless mode argument
    headless = '--headless' in sys.argv or '-h' in sys.argv

    if headless:
        print("Starting in headless mode (no GUI)...")

    main(headless=headless)
