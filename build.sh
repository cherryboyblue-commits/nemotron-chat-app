#!/usr/bin/env bash
set -e

# Pre-install stable tooling globally
python -m pip install --upgrade "pip<24.1" "setuptools<70.0.0" "wheel" "cython==0.29.33" "buildozer==1.5.0"

# Force NDK 25b in buildozer.spec
sed -i 's/^#\?\s*android.ndk_path.*/android.ndk_path =/' buildozer.spec
sed -i 's/^#\?\s*android.ndk =.*/android.ndk = 25b/' buildozer.spec

# Create a global constraints file for PIP
mkdir -p /tmp/pip_constraints
echo "pip<24.1" > /tmp/pip_constraints/constraints.txt
echo "setuptools<70.0.0" >> /tmp/pip_constraints/constraints.txt

# Force EVERY pip invocation (even inside p4a activated venvs) to respect constraints
export PIP_CONSTRAINT="/tmp/pip_constraints/constraints.txt"

# Run buildozer
buildozer -v android debug
