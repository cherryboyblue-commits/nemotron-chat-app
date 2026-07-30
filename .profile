# ~/.profile: executed by Bourne-compatible login shells.

if [ "$BASH" ]; then
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
fi

# Created by `pipx` on 2026-07-30 01:03:18
export PATH="$PATH:/root/.local/bin"
