[![branch](https://github.com/wtnb75/alpine-pkg/actions/workflows/branch.yml/badge.svg)](https://github.com/wtnb75/alpine-pkg/actions/workflows/branch.yml)

# Usage

## Enable Repository

- echo "https://wtnb75.github.io/alpine-pkg/" >> /etc/apk/repository
- cd /etc/apk/keys
- curl -sLO https://wtnb75.github.io/alpine-pkg/wtnb75@gmail.com-601572c5.rsa.pub

## install

- apk update
- apk add dool
- etc...
