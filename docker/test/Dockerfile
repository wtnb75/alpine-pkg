FROM alpine:3
RUN echo "https://wtnb75-repo.netlify.app/" >> /etc/apk/repositories
ADD https://wtnb75-repo.netlify.app/wtnb75@gmail.com-601572c5.rsa.pub /etc/apk/keys/
RUN apk update
