#!/system/bin/sh

ZTROOT=/data/adb/zerotier

# The NDK build ships libc++_shared.so inside the module.  A shell launched by
# the user does not inherit service.sh's environment, so set the search path
# here before delegating to the real multicall binary.
export LD_LIBRARY_PATH="$ZTROOT/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

exec "$ZTROOT/zerotier-cli" "$@"
