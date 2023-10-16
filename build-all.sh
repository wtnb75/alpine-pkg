#! /bin/sh
set -eu
set -o pipefail
cd $(dirname $0)
apkdir=$(pwd)/apk
mgmtdir=$(pwd)/mgmt
draft1=${mgmtdir}/draft.list
draft2=${mgmtdir}/draft.list.$(uname -m)
cd ${apkdir}

do1(){
    local dirname=$1
    [ -f $dirname/APKBUILD ] || return
    cd $dirname
    abuild -r -k || exit 1
    cd - > /dev/null
}

if [ "$*" = "" ]; then
    for i in */APKBUILD; do
        grep -q "^$(basename $(dirname $i))" ${draft1} && continue
        [ -f ${draft2} ] && grep -q "^$(basename $(dirname $i))" ${draft2} && continue
        do1 $(dirname $i) 2| sed -e 's, ERROR: \([^ :]*\):, ::error file=apk/\1/APKBUILD:: \1:,g;'
    done
else
    for i; do
        do1 $i 2| sed -e 's, ERROR: \([^ :]*\):, ::error file=apk/\1/APKBUILD:: \1:,g;'
    done
fi
apk-index || exit 1
