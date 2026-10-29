"""Build automation script for Aegis AI.

Supports:
1. Python wheel and sdist package build (PEP 517).
2. Standalone portable binary build using PyInstaller.
3. Test suite verification.
4. Build artifact cleanup.
"""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def run_cmd(cmd_list, desc="Command"):
    """Execute a command list and print status."""
    print(f"\n[Aegis Build] >>> Running: {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, cwd=str(PROJECT_ROOT))
    if res.returncode != 0:
        print(f"[Aegis Build] ERROR: {desc} failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    print(f"[Aegis Build] SUCCESS: {desc} completed.\n")


def clean_artifacts():
    """Remove previous build directories and caches."""
    print("[Aegis Build] Cleaning build artifacts...")
    for folder in ["build", "dist", ".pytest_cache", "aegis_ai.egg-info"]:
        p = PROJECT_ROOT / folder
        if p.exists() and p.is_dir():
            print(f"  Removing {folder}/")
            shutil.rmtree(p, ignore_errors=True)
    print("[Aegis Build] Clean complete.\n")


def run_tests():
    """Run full automated test suite."""
    print("[Aegis Build] Executing test suite...")
    run_cmd([sys.executable, "-m", "pytest", "-q"], desc="Unit and Integration Tests")


def build_package():
    """Build PEP 517 sdist and wheel."""
    print("[Aegis Build] Building wheel and sdist...")
    run_cmd([sys.executable, "-m", "build"], desc="Package Build")
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        print(f"[Aegis Build] Built packages in {dist_dir}:")
        for f in dist_dir.iterdir():
            print(f"  - {f.name} ({f.stat().st_size:,} bytes)")


def build_standalone():
    """Build standalone executable with PyInstaller."""
    print("[Aegis Build] Building standalone binary with PyInstaller...")

    # Separator for --add-data is ';' on Windows, ':' on Unix
    sep = ";" if os.name == "nt" else ":"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name", "aegis-ai",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--add-data", f"frontend{sep}frontend",
        "--add-data", f"skills{sep}skills",
        "--hidden-import", "uvicorn",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "main.py",
    ]

    run_cmd(cmd, desc="PyInstaller Standalone Build")

    exe_dir = PROJECT_ROOT / "dist" / "aegis-ai"
    print(f"\n[Aegis Build] SUCCESS: Standalone executable created at {exe_dir}")


def main():
    parser = argparse.ArgumentParser(description="Aegis AI Build System")
    parser.add_argument("--clean", action="store_true", help="Clean build directories")
    parser.add_argument("--test", action="store_true", help="Run tests before building")
    parser.add_argument("--package", action="store_true", help="Build wheel and source tarball")
    parser.add_argument("--standalone", action="store_true", help="Build standalone executable with PyInstaller")
    parser.add_argument("--all", action="store_true", help="Run tests, build package, and build standalone binary")

    args = parser.parse_args()

    # Default action if no arguments provided
    if not any([args.clean, args.test, args.package, args.standalone, args.all]):
        args.test = True
        args.package = True

    if args.clean or args.all:
        clean_artifacts()

    if args.test or args.all:
        run_tests()

    if args.package or args.all:
        build_package()

    if args.standalone or args.all:
        build_standalone()


if __name__ == "__main__":
    main()
