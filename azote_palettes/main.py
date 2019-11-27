import sys
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
from gi.repository.GdkPixbuf import InterpType
from PIL import Image, ImageOps
from colorthief import ColorThief
import common
from color_tools import get_colour_name, hex_to_rgb, rgb_to_cmyk


def scaled_pixbuf(path):
    pillow_image = Image.open(path)
    w, h = pillow_image.size
    ratio = min(720 / w, 480 / h)
    if w > 720 or h > 480:
        w = w * ratio
        h = h * ratio
        pillow_image.thumbnail((w, h), Image.ANTIALIAS)
    data = pillow_image.tobytes()
    data = GLib.Bytes.new(data)
    return GdkPixbuf.Pixbuf.new_from_data(data.get_data(), GdkPixbuf.Colorspace.RGB, False, 8,
                                          pillow_image.width, pillow_image.height,
                                          len(pillow_image.getbands()) * pillow_image.width, None, None)


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
    return GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w *3)


def palette(image_path):
    color_thief = ColorThief(image_path)
    return color_thief.get_palette(color_count=25, quality=10)


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


class Preview(Gtk.VBox):
    def __init__(self):
        super().__init__()
        common.image_path = os.path.join(common.images_path, 'wallhaven-73mry3.jpg')

        self.label = Gtk.Label()
        self.label.set_text(common.image_path)
        self.pack_start(self.label, True, True, 0)

        self.image = Gtk.Image()
        pixbuf = scaled_pixbuf(common.image_path)
        self.image.set_from_pixbuf(pixbuf)
        self.set_spacing(5)
        self.set_border_width(15)
        self.add(self.image)
        self.palette_preview = PalettePreview()
        self.add(self.palette_preview)
        self.toolbar = Toolbar()
        self.add(self.toolbar)

    def refresh(self):
        self.label.set_text(common.image_path)

        pixbuf = scaled_pixbuf(common.image_path)
        self.image.set_from_pixbuf(pixbuf)

        self.palette_preview.destroy()
        self.toolbar.destroy()
        self.palette_preview = PalettePreview()
        self.toolbar = Toolbar()
        self.palette_preview.show_all()
        self.toolbar.show_all()
        self.add(self.palette_preview)
        self.add(self.toolbar)


class PalettePreview(Gtk.VBox):
    def __init__(self):
        super().__init__()
        self.set_spacing(5)
        self.set_border_width(15)
        self.label = Gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_text('Click a button below to find the nearest known color')
        self.pack_start(self.label, True, True, 10)
        self.palette = palette(common.image_path)
        self.all_buttons = []
        index = 0
        for i in range(4):
            hbox = Gtk.HBox()
            for j in range(6):
                color = self.palette[index]
                pixbuf = color_image((80, 30), color)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                button = Gtk.Button.new_with_label(rgb_to_hex(color))
                button.set_always_show_image(True)
                button.set_image(image)
                button.set_image_position(2)
                button.connect('clicked', self.on_button_press)
                self.all_buttons.append(button)
                label = Gtk.Label()
                label.set_text(str(color))
                hbox.add(button)
                index += 1
            self.add(hbox)

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
            label_name = 'Exact name: {}'.format(exact_name)
        else:
            label_name = 'Nearest known name: {}'.format(closest_name)

        if exact_pantone:
            label_pantone = 'Exact Pantone C: {}'.format(exact_pantone)
        else:
            label_pantone = 'Nearest Pantone C: {}'.format(closest_pantone)

        self.label.set_markup('{} {} {} {} | {} | {}'.format(c, m, y, k, label_name, label_pantone))


class Toolbar(Gtk.HBox):
    def __init__(self):
        super().__init__()
        self.set_spacing(5)
        self.set_border_width(15)
        open_button = Gtk.Button.new_with_label("Select image")
        self.add(open_button)
        open_button.connect_after('clicked', self.on_open_button)

    def on_open_button(self, button):
        dialog = Gtk.FileChooserDialog(title='Select image', parent=button.get_toplevel(),
                                       action=Gtk.FileChooserAction.OPEN)
        filter = Gtk.FileFilter()
        filter.set_name('.jpg .jpeg .png')
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        dialog.add_filter(filter)

        dialog.set_current_folder(os.path.expanduser("~"))
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OK, 1)
        dialog.set_default_response(1)
        dialog.set_default_size(800, 600)

        response = dialog.run()
        if response == 1:
            common.image_path = dialog.get_filename()
            common.preview.refresh()
            text = common.images_path
            if len(text) > 40:
                text = '…{}'.format(text[-38::])
            button.set_label(text)

        dialog.destroy()


class GUI:
    def __init__(self):
        window = Gtk.Window()
        window.set_title("I'm a GTK+ window on Win10 :P")
        icon = GdkPixbuf.Pixbuf.new_from_file(os.path.join(common.images_path, 'azote.png'))
        window.set_default_icon(icon)
        window.connect_after('destroy', destroy)

        common.preview = Preview()
        window.add(common.preview)

        window.show_all()


def destroy(self):
    Gtk.main_quit()


def main():
    common.path = os.path.dirname(os.path.abspath(__file__))
    common.images_path = os.path.join(common.path, 'images')

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    css = b"""
                button#color-btn {
                font-weight: normal;
                font-size: 11px;
                }
                button#color-btn-selected {
                    font-weight: bold;
                    font-size: 12px;
                    border-top: 1px solid #ccc;
                    border-left: 1px solid #ccc;
                    border-bottom: 1px solid #333;
                    border-right: 1px solid #333;
                }
                """
    provider.load_from_data(css)

    app = GUI()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
