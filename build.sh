#!/usr/bin/env bash
set -e

# Pre-install stable tooling globally
python -m pip install --upgrade "pip<24.1" "setuptools<70.0.0" "wheel" "cython==0.29.33" "buildozer==1.5.0"

# Force NDK 25b in buildozer.spec
sed -i 's/^#\?\s*android.ndk_path.*/android.ndk_path =/' buildozer.spec
sed -i 's/^#\?\s*android.ndk =.*/android.ndk = 25b/' buildozer.spec

# Create global pip config to enforce pip version capping everywhere
mkdir -p ~/.config/pip
cat << 'PIPEOF' > ~/.config/pip/pip.conf
[global]
disable-pip-version-check = true
PIPEOF

# Global Python script wrapper to prevent pip from updating itself past 24.0
mkdir -p /tmp/bin
cat << 'PYEOF' > /tmp/bin/pip
#!/usr/bin/env bash
if [[ "$*" == *"install -U pip"* ]] || [[ "$*" == *"install --upgrade pip"* ]] || [[ "$*" == *"pip install -U pip"* ]]; then
    echo "Intercepted pip self-upgrade attempt. Enforcing pip<24.1."
    exec python -m pip install "pip<24.1"
fi
exec python -m pip "$@"
PYEOF

chmod +x /tmp/bin/pip
export PATH="/tmp/bin:$PATH"

# Run buildozer with debug logging enabled
buildozer -v android debug
