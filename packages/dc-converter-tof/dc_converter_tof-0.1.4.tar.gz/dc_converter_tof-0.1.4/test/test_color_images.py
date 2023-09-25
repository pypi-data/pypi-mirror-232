import os.path

from dc_convert.convert_folder import write_color_images


def test_add():
    write_color_images(os.path.expanduser('~/tmp/Tasse/Timo_Tasse_10-ergonomic-standing-2023-09-21T164305.097Z-DCG2202205001888/data.raw'))


