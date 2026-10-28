"""
Shadow Strike - Main Entry Point
Run: python main.py
"""
import os
import sys
import traceback

# Ensure the game root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _log_crash():
    """A packaged build has no console, so write crashes to a log file."""
    try:
        from core.paths import user_data_dir
        path = os.path.join(user_data_dir(), "crash.log")
        with open(path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        return path
    except Exception:
        return None


def main():
    from core.game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        log = _log_crash()
        traceback.print_exc()
        if log:
            print(f"[Shadow Strike] Crash details saved to: {log}")
        sys.exit(1)
