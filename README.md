[![main](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml/badge.svg)](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml)

# Usage

## Enable Repository

- echo "https://wtnb75.github.io/alpine-pkg/" >> /etc/apk/repositories
- wget -P /etc/apk/keys/ https://wtnb75.github.io/alpine-pkg/wtnb75@gmail.com-601572c5.rsa.pub

## install

- apk update
- apk add dool
- etc...
