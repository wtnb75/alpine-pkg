#! /bin/sh
cd $(dirname $0)
apkdir=$(pwd)/apk
mgmtdir=$(pwd)/mgmt
cd ${apkdir}

do1(){
    local dirname=$1
    [ -f $dirname/APKBUILD ] || return
    cd $dirname
    abuild -r || exit 1
    cd - > /dev/null
}

if [ "$*" = "" ]; then
    for i in */APKBUILD; do
        grep -q "^$(basename $(dirname $i))" ${mgmtdir}/draft.list && continue
        do1 $(dirname $i)
    done
else
    for i; do
        do1 $i
    done
fi
apk-index || exit 1
