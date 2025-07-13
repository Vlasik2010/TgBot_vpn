#!/usr/bin/env python3
"""
Run the VPN Telegram Bot
Usage: python run.py
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import main

if __name__ == '__main__':
    main()