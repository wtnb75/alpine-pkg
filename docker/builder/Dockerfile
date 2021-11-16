FROM alpine:edge
RUN apk add alpine-sdk sudo atools abuild-doc mandoc ccache cmake go rust linux-headers automake autoconf libtool pkgconfig musl-dev cargo
RUN apk add python3 py3-pip py3-click py3-lxml py3-yaml py3-requests py3-jinja2 py3-natsort
RUN pip3 install cssselect dirindex
RUN sed -i -e 's,#USE_CCACHE=1,USE_CCACHE=1,g;' /etc/abuild.conf
RUN adduser -S -G abuild packager
ADD sudoers.packager /etc/sudoers.d/packager
ADD apk-index.sh /usr/local/bin/apk-index
RUN install -d -o root -g abuild -m 0775 /var/cache/distfiles
RUN install -d -o packager -g abuild -m 0755 /home/packager/packages /home/packager/.abuild /home/packager/.cache /home/packager/go /home/packager/.cargo
ADD abuildconf/* /home/packager/.abuild/
RUN chown -R packager.abuild /home/packager/.abuild
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN echo "http://wtnb75-repo.s3-website-ap-northeast-1.amazonaws.com/apk/" >> /etc/apk/repositories
ADD abuildconf/*.rsa.pub /etc/apk/keys/
RUN chown root.root /etc/apk/keys/wtnb75*.pub && \
    chmod 644 /etc/apk/keys/wtnb75*.pub
USER packager
