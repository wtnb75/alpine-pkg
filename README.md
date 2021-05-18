[![main](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml/badge.svg)](https://github.com/wtnb75/alpine-pkg/actions/workflows/main.yml) [![Netlify Status](https://api.netlify.com/api/v1/badges/c8ca8f09-8390-4fbc-9aab-4bf79ecf4fcb/deploy-status)](https://app.netlify.com/sites/wtnb75-repo/deploys)

# Usage

## Enable Repository

- echo "https://wtnb75-repo.netlify.app/" >> /etc/apk/repositories
- wget -P /etc/apk/keys/ https://wtnb75-repo.netlify.app/wtnb75@gmail.com-601572c5.rsa.pub

## install

- apk update
- apk add dool
- etc...
