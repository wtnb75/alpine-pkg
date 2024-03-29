# Contributor: Watanabe Takashi <wtnb75@gmail.com>
# Maintainer:
pkgname={{name}}
pkgver={{version}}
pkgrel=0
pkgdesc="{{description}}"
url="{{url}}"
arch="all"
license="{{license}}"
depends=""
makedepends=""
install=""
subpackages="$pkgname-doc"
source="{{source}}"
builddir="$srcdir/$pkgname-$pkgver"

build() {
	cd "$builddir"
	mkdir build
	cd build
	cmake .. -DCMAKE_INSTALL_PREFIX=/usr
	./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --mandir=/usr/share/man
	make
}

check() {
	# Replace with proper check command(s)
	:
}

package() {
	cd "$builddir"/build
	make install DESTDIR=$pkgdir
}
