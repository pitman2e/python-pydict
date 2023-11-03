# Maintainer: pitman2e
pkgname=pydict
pkgver=0.8.2
pkgrel=1
pkgdesc="A Dictionary Scalper"
arch=('any')
depends=("python-beautifulsoup4" "python-selenium" "python-pyperclip" "python-requests" "python-pyqt6" "python-hanziconv" "qt6-wayland")
makedepends=('git' 'python>=3.10')
conflicts=()
provides=()
source=("git+https://github.com/pitman2e/python-pydict.git#branch=master")
sha512sums=("SKIP")

package() {
  cd "${srcdir}/python-pydict"
  python3 setup.py install --root="$pkgdir" --optimize=1 || return 1
  install -Dm755 "usr/bin/pydict" "${pkgdir}/usr/bin/pydict"
  install -Dm755 "usr/share/applications/pydict.desktop" "${pkgdir}/usr/share/applications/pydict.desktop"
}
