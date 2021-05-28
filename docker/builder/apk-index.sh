#! /bin/sh
. /etc/abuild.conf
. $HOME/.abuild/abuild.conf

for idx in $(find ${REPODEST} -type f -name APKINDEX.tar.gz); do
  [ -f "${idx}" ] || continue
  d=$(dirname $idx)
  apk index -o ${idx} ${d}/*.apk
  [ -f "${PACKAGER_PRIVKEY}" ] || continue
  abuild-sign -k ${PACKAGER_PRIVKEY} ${idx}
done
