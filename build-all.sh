#! /bin/sh
cd $(dirname $0)

do1(){
    local dirname=$1
    [ -f $dirname/APKBUILD ] || return
    cd $dirname
    abuild -r
    cd - > /dev/null
}

if [ "$*" = "" ]; then
    for i in */APKBUILD; do
        do1 $(dirname $i)
    done
else
    for i; do
        do1 $i
    done
fi
apk-index
