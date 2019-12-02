# CHANGELOG

## v0.2.3 (2019-12-02)

- `wl-clipboard` dependency dropped, Gtk.Clipboard class used instead; should work in both sway and X11.

## v0.2.2 (2019-12-01)

- `azote-palettes /path/to/the/image` argument makes the program try to open the image from the given path;
- `MimeType=image/jpeg;image/jpg;image/png;` added to `/usr/share/azote-palettes.desktop`.

## v0.2.1 (2019-12-01)

- Paste image feature added. For now it works on Wayland and (probably) on Windows and Mac (not yet tested).
- Runtime configuration file at `~/.azote-palettes-rc`.

## v0.1.1 (2019-11-29)

- initial release
