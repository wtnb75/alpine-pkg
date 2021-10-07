[![main](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml/badge.svg)](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml)

# Usage

## Enable Repository

- echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
- echo "http://wtnb75-repo.s3-website-ap-northeast-1.amazonaws.com/apk/" >> /etc/apk/repositories
- wget -P /etc/apk/keys/ http://wtnb75-repo.s3-website-ap-northeast-1.amazonaws.com/wtnb75@gmail.com-601572c5.rsa.pub

## install

- apk update
- apk add dool
- etc...
