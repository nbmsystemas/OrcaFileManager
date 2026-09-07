import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/nbmsystemas/OrcaFileManager.git"


def build_update_command(
    *,
    pipx: bool,
    python_executable: str = sys.executable,
    pipx_executable: str = "pipx",
) -> list[str]:
    """Build an update command that installs the current GitHub revision."""
    source = f"git+{REPOSITORY}"
    if pipx:
        return [
            pipx_executable,
            "install",
            "--force",
            "--pip-args=--no-cache-dir",
            source,
        ]

    return [
        python_executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--force-reinstall",
        "--no-cache-dir",
        source,
    ]


def _running_under_pipx(executable: str | None = None) -> bool:
    executable = executable or sys.executable
    return "pipx" in str(Path(executable)).lower()


def do_update():
    """Fetch and reinstall the latest GitHub revision."""
    print("🐋 OrcaFileManager — Updating to latest version...")

    if _running_under_pipx():
        print("   Detected pipx environment. Reinstalling from GitHub...\n")
        pipx_executable = shutil.which("pipx")
        if pipx_executable is None:
            print("   ❌ 'pipx' command not found in PATH.")
            print(
                "   Please reinstall manually with: pipx install --force git+"
                + REPOSITORY
            )
            sys.exit(1)
        command = build_update_command(
            pipx=True,
            pipx_executable=pipx_executable,
        )
    else:
        print(f"   Source: {REPOSITORY}\n")
        command = build_update_command(pipx=False)

    try:
        result = subprocess.run(command, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"\n❌ Update failed: {exc}")
        sys.exit(1)

    if result.returncode == 0:
        print("\n✅ Update complete! Run 'orca' to launch the new version.")
    else:
        print(
            "\n❌ Update failed. Check your internet connection or try upgrading manually."
        )
    sys.exit(result.returncode)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        do_update()

    from orca.app import OrcaApp

    app = OrcaApp()
    app.run()


if __name__ == "__main__":
    main()
