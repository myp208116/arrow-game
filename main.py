"""Run with python main.py. --smoke-test renders a short non-interactive session."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="一箭又一箭")
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    from arrow_game.app import App
    App().run(max_frames=5 if args.smoke_test else None)


if __name__ == "__main__":
    main()
