#!/bin/sh

if [[ "x$GIT_MIRROR_DAEMON" != "x" ]]; then
  echo "$GIT_MIRROR_DAEMON python3 /git-mirror/git-mirror.py -c /git-mirror/config.json" | crontab -
  crond -f
else
  python3 /git-mirror/git-mirror.py "$@"
fi