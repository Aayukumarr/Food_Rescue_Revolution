#!/usr/bin/env python3
"""
Main launcher for Food Rescue ML Desktop Application.
Run with:
    python3 main.py
or:
    python3 app.py
"""

from app import FoodRescueApp

if __name__ == '__main__':
    app = FoodRescueApp()
    app.mainloop()
