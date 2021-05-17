FROM alpine:3
RUN apk add alpine-sdk sudo atools abuild-doc mandoc ccache cmake go rust linux-headers automake autoconf libtool pkgconfig musl-dev
RUN sed -i -e 's,#USE_CCACHE=1,USE_CCACHE=1,g;' /etc/abuild.conf
RUN adduser -S -G abuild packager
ADD sudoers.packager /etc/sudoers.d/packager
ADD apk-index.sh /usr/local/bin/apk-index
RUN install -d -o root -g abuild -m 0775 /var/cache/distfiles
RUN install -d -o packager -g abuild -m 0755 /home/packager/packages /home/packager/.abuild /home/packager/.cache /home/packager/go /home/packager/.cargo
ADD abuildconf/* /home/packager/.abuild/
RUN chown -R packager.abuild /home/packager/.abuild
RUN cp /home/packager/.abuild/*.rsa.pub /etc/apk/keys/
USER packager
