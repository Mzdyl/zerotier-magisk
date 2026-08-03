#!/system/bin/sh

ZTROOT=/data/adb/zerotier

# See zerotier-cli.sh. Keep the NDK C++ runtime private to ZeroTier commands.
export LD_LIBRARY_PATH="$ZTROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

exec "$ZTROOT/zerotier-idtool" "$@"
