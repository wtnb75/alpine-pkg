FROM alpine:3
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN echo "http://wtnb75-repo.s3-website-ap-northeast-1.amazonaws.com/apk/" >> /etc/apk/repositories
ADD wtnb75@gmail.com-601572c5.rsa.pub /etc/apk/keys/
RUN apk update
