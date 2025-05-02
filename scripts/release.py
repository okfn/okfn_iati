#!/usr/bin/env python3
"""
Release script to build and upload okfn-iati to PyPI.

Usage:
    python scripts/release.py [--test]

Options:
    --test: Upload to Test PyPI instead of PyPI
"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    # Determine if we're uploading to Test PyPI
    use_testpypi = "--test" in sys.argv

    # Paths
    project_root = Path(__file__).parent.parent.absolute()
    dist_dir = project_root / "dist"

    # Clean dist directory if it exists
    print("Cleaning dist directory...")
    if os.path.exists(dist_dir):
        for file in os.listdir(dist_dir):
            os.remove(dist_dir / file)
    else:
        os.makedirs(dist_dir)

    # Build the package
    print("Building the package...")
    subprocess.run(
        [sys.executable, "-m", "build", "--sdist", "--wheel", project_root],
        check=True
    )

    # Upload to PyPI or Test PyPI
    print(f"Uploading to {'Test PyPI' if use_testpypi else 'PyPI'}...")
    cmd = [sys.executable, "-m", "twine", "upload"]

    if use_testpypi:
        cmd.extend(["--repository", "testpypi"])

    cmd.append(str(dist_dir / "*"))

    # Using shell=True because we need glob expansion
    subprocess.run(" ".join(cmd), shell=True, check=True)

    print("Done!")


if __name__ == "__main__":
    main()
