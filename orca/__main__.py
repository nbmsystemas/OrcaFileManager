import sys
import subprocess


def do_update():
    """Pull latest version from GitHub and reinstall."""
    repo = "https://github.com/nbmsystemas/OrcaFileManager.git"
    print("🐋 OrcaFileManager — Updating to latest version...")
    print(f"   Source: {repo}\n")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", f"git+{repo}"],
        check=False,
    )
    if result.returncode == 0:
        print("\n✅ Update complete! Run 'orca' to launch the new version.")
    else:
        print("\n❌ Update failed. Check your internet connection and try again.")
    sys.exit(result.returncode)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        do_update()

    from orca.app import OrcaApp
    app = OrcaApp()
    app.run()


if __name__ == "__main__":
    main()
