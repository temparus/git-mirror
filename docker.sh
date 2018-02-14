#!/bin/sh

if [ -z "$GIT_MIRROR_DAEMON" ]; then
  echo "$GIT_MIRROR_DAEMON python3 /git-mirror/git-mirror.py -c /git-mirror/config.json" | crontab -
  crond -f -d 0
else
  python3 /git-mirror/git-mirror.py "$@"
fi