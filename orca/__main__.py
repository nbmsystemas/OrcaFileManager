import sys
import subprocess


def do_update():
    """Pull latest version from GitHub and reinstall."""
    import shutil
    
    print("🐋 OrcaFileManager — Updating to latest version...")
    
    # Check if running under pipx
    if "pipx" in sys.executable:
        print("   Detected pipx environment. Upgrading via pipx...\n")
        if shutil.which("pipx"):
            result = subprocess.run(["pipx", "upgrade", "orca-filemanager"], check=False)
        else:
            print("   ❌ 'pipx' command not found in PATH.")
            print("   Please upgrade manually by running: pipx upgrade orca-filemanager")
            sys.exit(1)
    else:
        repo = "https://github.com/nbmsystemas/OrcaFileManager.git"
        print(f"   Source: {repo}\n")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", f"git+{repo}"],
            check=False,
        )

    if result.returncode == 0:
        print("\n✅ Update complete! Run 'orca' to launch the new version.")
    else:
        print("\n❌ Update failed. Check your internet connection or try upgrading manually.")
    sys.exit(result.returncode)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        do_update()

    from orca.app import OrcaApp
    app = OrcaApp()
    app.run()


if __name__ == "__main__":
    main()
