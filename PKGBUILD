# Maintainer: Piotr Miller <nwg.piotr@gmail.com>
pkgname=('azote-palettes')
pkgver=0.2.1
pkgrel=1
pkgdesc="Colour palette creator and colour names dictionary"
arch=('x86_64')
url="https://github.com/nwg-piotr/azote-palettes"
license=('GPL3')
depends=('python' 'python-setuptools' 'python-gobject' 'python-pillow' 'python-colorthief' 'gtk3' 'wl-clipboard')

source=("https://github.com/nwg-piotr/azote-palettes/archive/v"$pkgver".tar.gz")

md5sums=('7b2dad2e276313cb066eaa042a38786d')

package() {
  install -D -m 755 "$pkgname"-"$pkgver"/dist/azote-palettes "$pkgdir"/usr/bin/azote-palettes
  install -D -t "$pkgdir"/usr/share/"$pkgname" "$pkgname"-"$pkgver"/dist/azote-palettes.svg
  install -D -t "$pkgdir"/usr/share/applications "$pkgname"-"$pkgver"/dist/azote-palettes.desktop
  install -Dm 644 "$pkgname"-"$pkgver"/LICENSE-COLORTHIEF "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE-COLORTHIEF"
  cd "$srcdir/$pkgname-$pkgver"
  /usr/bin/python setup.py install --root="$pkgdir/" --optimize=1
}
