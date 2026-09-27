"""
Shadow Strike — Main Entry Point
Run: python main.py
"""
import os
import sys

# Ensure the game root is in the Python path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    try:
        import numpy  # check numpy is available for audio
    except ImportError:
        print("[Shadow Strike] Installing numpy for procedural audio...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy

    from core.game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
