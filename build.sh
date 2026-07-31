#!/usr/bin/env bash
set -e

python -m pip install --upgrade "pip<24.1" "setuptools<70.0.0" "wheel" "cython==0.29.33" "buildozer==1.5.0"

# Force NDK 25b in buildozer.spec
sed -i 's/^#\?\s*android.ndk_path.*/android.ndk_path =/' buildozer.spec
sed -i 's/^#\?\s*android.ndk =.*/android.ndk = 25b/' buildozer.spec

# Intercept pip upgrades inside p4a venv
mkdir -p /tmp/bin
cat << 'PYEOF' > /tmp/bin/pip
#!/usr/bin/env bash
if [[ "$*" == *"install -U pip"* ]] || [[ "$*" == *"install --upgrade pip"* ]]; then
    echo "Intercepted pip upgrade request to keep build stable."
    exit 0
fi
exec python -m pip "$@"
PYEOF

chmod +x /tmp/bin/pip
export PATH="/tmp/bin:$PATH"

buildozer -v android debug
