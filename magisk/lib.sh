# variables

ZTROOT=/data/adb/zerotier
APPROOT=/data/data/com.eventlowop.zerotier_magisk_app/app_flutter

ZT_LOG=$ZTROOT/run/zerotier.log
DAEMON_LOG=$ZTROOT/run/daemon.log

PIPE_CLI=$ZTROOT/run/pipe
PIPE_APP=$APPROOT/run/pipe

# LD_LIBRARY_PATH for NDK
export LD_LIBRARY_PATH=/system/lib64:/data/adb/zerotier/lib

# Remove all pref 1 rules pointing to main so restarts never stack duplicates
_del_rules() {
  local spec
  ip -4 rule show 2>/dev/null | awk '/^1:.*lookup main/{sub(/^1:[ \t]*/, ""); print}' | while IFS= read -r spec; do
    [ -n "$spec" ] && ip -4 rule del $spec pref 1 2>/dev/null
  done
  ip -6 rule show 2>/dev/null | awk '/^1:.*lookup main/{sub(/^1:[ \t]*/, ""); print}' | while IFS= read -r spec; do
    [ -n "$spec" ] && ip -6 rule del $spec pref 1 2>/dev/null
  done
}

# Route only ZeroTier managed subnets via main at pref 1 (instead of from all lookup main)
_sync_rules() {
  _del_rules
  ip -6 rule add to fc00::/7 lookup main pref 1 2>/dev/null || true

  (
    i=0
    while [ $i -lt 60 ]; do
      cidrs4=$(ip -4 route show table main 2>/dev/null | awk '/dev zt/ && $1 != "default" {print $1}' | sort -u)
      cidrs6=$(ip -6 route show table main 2>/dev/null | awk '/dev zt/ && $1 != "default" && $1 !~ /^fe80:/ {print $1}' | sort -u)
      if [ -n "$cidrs4" ] || [ -n "$cidrs6" ]; then
        for c in $cidrs4; do
          ip -4 rule show | grep -q "to $c lookup main" || ip -4 rule add to "$c" lookup main pref 1 2>/dev/null || true
        done
        for c in $cidrs6; do
          ip -6 rule show | grep -q "to $c lookup main" || ip -6 rule add to "$c" lookup main pref 1 2>/dev/null || true
        done
        break
      fi
      i=$((i + 1))
      sleep 1
    done
  ) &
}

__start() {
  _sync_rules

  # start zerotier daemon
  nohup $ZTROOT/zerotier-one -d >> $ZT_LOG 2>&1 &
}