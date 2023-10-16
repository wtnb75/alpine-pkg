#! /bin/sh
set -eu
set -o pipefail
. /etc/abuild.conf
. $HOME/.abuild/abuild.conf

for idx in $(find ${REPODEST-/home/packager/packages}/apk/$(uname -m) -type f -name APKINDEX.tar.gz); do
  [ -f "${idx}" ] || continue
  d=$(dirname $idx)
  apk index -o ${idx} ${d}/*.apk
  [ -f "${PACKAGER_PRIVKEY}" ] || continue
  abuild-sign -k ${PACKAGER_PRIVKEY} ${idx}
done
