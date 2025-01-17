#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

"""
Colour palette creator and colour names dictionary
Author: Piotr Miller
e-mail: nwg.piotr@gmail.com
Website: https://github.com/nwg-piotr/azote-palettes
License: GPL-3.0-or-later

Depends on: 'python-colorthief'
"""
import sys
import os
import platform
import tempfile
import gi
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
from PIL import Image
from colorthief import ColorThief
from azote_palettes.color_tools import get_colour_name, hex_to_rgb, rgb_to_cmyk
from azote_palettes import common

tempdir = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
clipboard_file = os.path.join(tempdir, 'azote-clipboard.png')
clipboard_file_scaled = os.path.join(tempdir, 'azote-clipboard-scaled.png')

# I have no Mac in range to check if it works there!
image_grab = platform.system() == 'Windows' or platform.system() == 'Darwin'

if image_grab:
    from PIL import ImageGrab


def save_clipboard():
    if image_grab:
        clipboard = ImageGrab.grabclipboard()
        if clipboard:
            clipboard.save(clipboard_file, 'PNG')
    else:
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        pixbuf = clipboard.wait_for_image()
        if pixbuf:
            pixbuf.savev(clipboard_file, 'png', [], [])


def scale_image(path):
    preview_max_height = int(common.rc.preview_max_width * 0.5625)
    try:
        pillow_image = Image.open(path)
        w, h = pillow_image.size
        ratio = min(common.rc.preview_max_width / w, preview_max_height / h)
        if w > common.rc.preview_max_width or h > preview_max_height:
            w = w * ratio
            h = h * ratio
            pillow_image.thumbnail((w, h), Image.NEAREST)
        pillow_image.save(clipboard_file_scaled)
    except Exception as e:
        print(e)


def color_image(size, color):
    """
    :param size: tuple (width, height)
    :param color: tuple (red, green, blue)
    :return: GdkPixbuf
    """
    image = Image.new("RGB", size, color)
    data = image.tobytes()
    w, h = image.size
    data = GLib.Bytes.new(data)
    return GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * 3)


def palette(image_path):
    try:
        color_thief = ColorThief(image_path)
        return color_thief.get_palette(color_count=common.rc.num_colors + 1, quality=10)
    except:
        return None


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


class Preview(Gtk.VBox):
    def __init__(self):
        super().__init__()
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            common.image_path = sys.argv[1]
        else:
            common.image_path = os.path.join(common.images_path, 'welcome.jpg')

        self.image = Gtk.Image()
        scale_image(common.image_path)
        self.image.set_from_file(clipboard_file_scaled)

        self.set_spacing(5)
        self.set_border_width(15)
        self.pack_start(self.image, True, True, 0)

        self.label = Gtk.Label()
        self.label.set_property("name", "label")
        self.label.set_text(common.image_path)
        self.pack_start(self.label, True, True, 10)

        self.toolbar = Toolbar()
        self.pack_start(self.toolbar, False, False, 0)

        self.palette_preview = PalettePreview()
        self.add(self.palette_preview)

    def refresh(self):
        self.label.set_text(common.image_path)
        scale_image(common.image_path)
        self.image.set_from_file(clipboard_file_scaled)

        self.palette_preview.destroy()
        self.palette_preview = PalettePreview()
        self.palette_preview.show_all()
        self.add(self.palette_preview)


class PalettePreview(Gtk.VBox):
    def __init__(self):
        super().__init__()
        self.set_spacing(5)
        self.label = Gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_property("name", "label")
        self.label.set_text('Click a button below for colour details')
        self.pack_start(self.label, True, True, 10)
        self.palette = palette(common.image_path)
        if self.palette:
            self.all_buttons = []
            index = 0
            for i in range(common.rc.num_colors // 6):
                hbox = Gtk.HBox()
                for j in range(6):
                    try:
                        color = self.palette[index]
                        pixbuf = color_image((80, 30), color)
                        image = Gtk.Image.new_from_pixbuf(pixbuf)
                        button = Gtk.Button.new_with_label(rgb_to_hex(color))
                        button.set_always_show_image(True)
                        button.set_image(image)
                        button.set_image_position(2)
                        button.set_property("name", "color-btn")
                        button.connect('clicked', self.on_button_press)
                        self.all_buttons.append(button)
                        label = Gtk.Label()
                        label.set_text(str(color))
                        hbox.pack_start(button, True, False, 0)
                        index += 1
                    except IndexError:
                        break
                self.pack_start(hbox, True, True, 0)

    def on_button_press(self, button):
        # mark all buttons unselected
        for btn in self.all_buttons:
            btn.set_property("name", "color-btn")

        # mark clicked button selected
        button.set_property("name", "color-btn-selected")

        # find CMYK value
        rgb = hex_to_rgb(button.get_label())
        c, m, y, k = rgb_to_cmyk(rgb[0], rgb[1], rgb[2])
        c = 'C: <span weight="bold">{}</span>'.format(str(round(c)))
        m = 'M: <span weight="bold">{}</span>'.format(str(round(m)))
        y = 'Y: <span weight="bold">{}</span>'.format(str(round(y)))
        k = 'K: <span weight="bold">{}</span>'.format(str(round(k)))

        # find exact or closest common colour name
        exact_name, closest_name = get_colour_name(button.get_label(), 'names')

        # find exact or closest Pantone C colour
        exact_pantone, closest_pantone = get_colour_name(button.get_label(), 'pantone')

        self.label.set_selectable(True)

        if exact_name:
            label_name = 'Exact: {}'.format(exact_name)
        else:
            label_name = 'Nearest: {}'.format(closest_name)

        if exact_pantone:
            label_pantone = 'Exact Pantone: {}'.format(exact_pantone)
        else:
            label_pantone = 'Nearest Pantone: {}'.format(closest_pantone)

        self.label.set_markup(
            '{} | {} {} {} {} | {} | {}'.format(button.get_label(), c, m, y, k, label_name, label_pantone))


class Toolbar(Gtk.HBox):
    def __init__(self):
        super().__init__()
        self.set_spacing(5)

        button = Gtk.Button.new_with_label("Palette size ({})".format(common.rc.num_colors))
        self.pack_start(button, False, False, 0)
        button.connect_after('clicked', self.on_size_button)

        button = Gtk.Button.new_with_label("Select image")
        self.add(button)
        button.connect_after('clicked', self.on_open_button)

        button = Gtk.Button.new_with_label("Paste image")
        self.pack_start(button, False, False, 0)
        button.connect_after('clicked', self.on_paste_button)

    def on_size_button(self, button):
        menu = Gtk.Menu()
        item = Gtk.MenuItem.new_with_label('6 colors')
        item.connect('activate', self.on_size_menu_item, button, 6)
        menu.append(item)
        item = Gtk.MenuItem.new_with_label('12 colors')
        item.connect('activate', self.on_size_menu_item, button, 12)
        menu.append(item)
        item = Gtk.MenuItem.new_with_label('18 colors')
        item.connect('activate', self.on_size_menu_item, button, 18)
        menu.append(item)
        item = Gtk.MenuItem.new_with_label('24 colors')
        item.connect('activate', self.on_size_menu_item, button, 24)
        menu.append(item)
        item = Gtk.MenuItem.new_with_label('30 colors')
        item.connect('activate', self.on_size_menu_item, button, 30)
        menu.append(item)
        item = Gtk.MenuItem.new_with_label('36 colors')
        item.connect('activate', self.on_size_menu_item, button, 36)
        menu.append(item)

        menu.show_all()
        menu.popup_at_widget(button, Gdk.Gravity.WEST, Gdk.Gravity.SOUTH_WEST, None)

    def on_size_menu_item(self, item, button, number):
        common.rc.num_colors = number
        common.rc.save()
        common.preview.refresh()
        button.set_label("Palette size ({})".format(common.rc.num_colors))

    def on_open_button(self, button):
        dialog = Gtk.FileChooserDialog(title='Select image', parent=button.get_toplevel(),
                                       action=Gtk.FileChooserAction.OPEN)
        filter = Gtk.FileFilter()
        filter.set_name('jpg/png')
        filter.add_pattern("*.png")
        filter.add_pattern("*.PNG")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.JPG")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.JPEG")
        dialog.add_filter(filter)

        if common.last_folder:
            dialog.set_current_folder(common.last_folder)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)
        dialog.set_default_response(1)
        dialog.set_default_size(800, 600)

        response = dialog.run()
        if response == 1:
            common.image_path = dialog.get_filename()
            common.preview.refresh()
            common.last_folder = os.path.split(common.image_path)[0]
        dialog.destroy()

    def on_paste_button(self, button):
        save_clipboard()

        global clipboard_file
        if os.path.exists(clipboard_file):
            scale_image(clipboard_file)
            common.preview.image.set_from_file(clipboard_file)
            common.preview.label.set_text(clipboard_file)
            common.image_path = clipboard_file
            common.preview.refresh()


class GUI:
    def __init__(self):
        window = Gtk.Window()
        window.set_title('Azote Palettes')
        if platform.system().upper() == 'WINDOWS':
            icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join(common.images_path, 'azote-palettes.png'))
        else:
            icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join(common.images_path, 'azote-palettes.svg'))
        window.set_default_icon(icon)
        window.connect_after('destroy', destroy)
        window.connect("key-release-event", handle_keyboard)

        common.preview = Preview()
        window.add(common.preview)

        window.show_all()


def destroy(self):
    Gtk.main_quit()


class RuntimeConfig(object):
    def __init__(self):
        super().__init__()
        self.preview_max_width = 720
        self.num_colors = 24

        try:
            with open(common.rc_path, 'r') as f:
                rc = json.load(f)
                self.preview_max_width = int(rc['preview_max_width'])
                self.num_colors = int(rc['num_colors'])
        except FileNotFoundError:
            self.save()

    def save(self):
        rc = {'preview_max_width': str(self.preview_max_width),
              'num_colors': str(self.num_colors)}

        with open(common.rc_path, 'w') as f:
            json.dump(rc, f, indent=2)


def handle_keyboard(window, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        window.close()


def main():
    common.home = os.path.expanduser('~')
    common.rc_path = os.path.join(common.home, '.azote-palettes-rc')
    common.resources_path = os.path.dirname(os.path.abspath(__file__))
    common.images_path = os.path.join(common.resources_path, 'images')
    common.rc = RuntimeConfig()

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    css = b"""
                button#color-btn {
                font-weight: normal;
                font-size: 13px;
                }
                button#color-btn-selected {
                    font-weight: bold;
                    font-size: 13px;
                    border-top: 1px solid #ccc;
                    border-left: 1px solid #ccc;
                    border-bottom: 1px solid #333;
                    border-right: 1px solid #333;
                }
                label#label {
                    font-size: 13px;
                }
                """
    provider.load_from_data(css)

    app = GUI()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
