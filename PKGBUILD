# Maintainer: Piotr Miller <nwg.piotr@gmail.com>
pkgname=('azote-palettes')
pkgver=1.0.1
pkgrel=1
pkgdesc="Colour palette creator and colour names dictionary"
arch=('x86_64')
url="https://github.com/nwg-piotr/azote-palettes"
license=('GPL3')
depends=('python' 'python-setuptools' 'python-gobject' 'python-pillow' 'python-colorthief' 'gtk3')

source=("$pkgname-$pkgver.tar.gz::https://github.com/nwg-piotr/azote-palettes/archive/v"$pkgver".tar.gz")

md5sums=('42410a70b9e0d8650bf88ec69e9e827f')

package() {
  install -D -m 755 "$pkgname"-"$pkgver"/dist/azote-palettes "$pkgdir"/usr/bin/azote-palettes
  install -D -t "$pkgdir"/usr/share/"$pkgname" "$pkgname"-"$pkgver"/dist/azote-palettes.svg
  install -D -t "$pkgdir"/usr/share/applications "$pkgname"-"$pkgver"/dist/azote-palettes.desktop
  install -Dm 644 "$pkgname"-"$pkgver"/LICENSE-COLORTHIEF "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE-COLORTHIEF"
  cd "$srcdir/$pkgname-$pkgver"
  /usr/bin/python setup.py install --root="$pkgdir/" --optimize=1
}
