#!/bin/bash -e

if [[ $EUID -ne 0 ]]; then
	echo "Please re-run with sudo (or as root)"
	exit 1
fi

base_url="https://dl.cloudsmith.io/public/moonlight-game-streaming/moonlight-qt"
gpg_keyring_path="/usr/share/keyrings/moonlight-game-streaming-moonlight-qt-archive-keyring.gpg"
gpg_url="$base_url/gpg.2F6AE14E1C660D44.key"
list_path='/etc/apt/sources.list.d/moonlight-game-streaming-moonlight-qt.list'

curl -1sLf "$gpg_url" | gpg --dearmor >> "$gpg_keyring_path"

cat > "$list_path" <<EOF

deb [signed-by=$gpg_keyring_path] $base_url/deb/debian bookworm main

#deb-src [signed-by=$gpg_keyring_path] $base_url/deb/debian bookworm main
EOF

apt-get update
apt-get install moonlight-qt
