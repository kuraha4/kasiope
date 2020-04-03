"""Config data holder."""

from os import path
import json


class Config():
    """Config data holder."""

    def __init__(self):
        """Set attributes."""
        json_path = 'config.json'

        if path.exists(json_path):
            self.load(json_path)
        else:
            # default values
            self.window_size = (600, 800)
            self.stay_on_top = True
            self.font_size = 11

            self.text_color = '#DFE2E6'
            self.color1 = '#36414D'
            self.color2 = '#20272E'

            self.send_mora_hotkey = 'ctrl+alt+pageup'
            self.send_line_hotkey = 'ctrl+alt+pagedown'

            # 単純に置換するだけなので内容に注意
            self.conv_dict = [('個別に変換したい文字列', 'こべつにへんかんしたいもじれつ')]
            self.yoon = 'ゃゅょぁぃぅぇぉャュョァィゥェォ'
            self.sokuon = 'っッ'
            self.kigo = '「」『』（）！？!?♥♡、。,.・／/…’”\'\"-'
            self.alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZéàèùâêîôûçëïü'
            self.katakana = ('アイウエオカキクケコサシスセソタチツテトナニヌネノ'
                             'ハヒフヘホマミムメモヤユヨラリルレロワヰウヱヲン'
                             'ヴガギグゲゴザジズゼゾダヂヅデドバビブベボヷヸヹヺ'
                             'パピプペポ'
                             'ァィゥェォヵㇰヶㇱㇲッㇳㇴㇵㇶㇷㇸㇹㇺャュョㇻㇼㇽㇾㇿヮ')
            self.highlight = 'ー' + self.sokuon + self.kigo

            self.save()

    def save(self):
        """Save attributes to JSON file."""
        with open('config.json', 'w', encoding='utf-8') as wfile:
            json.dump(self, wfile, cls=self.ConfigEncoder, indent=4, ensure_ascii=False)

    def load(self, json_path):
        """Set attributes from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as rfile:
            dct = json.load(rfile)

        self.window_size = dct['window_size']
        self.stay_on_top = dct['stay_on_top']
        self.font_size = dct['font_size']

        self.text_color = dct['text_color']
        self.color1 = dct['color1']
        self.color2 = dct['color2']

        self.send_mora_hotkey = dct['send_mora_hotkey']
        self.send_line_hotkey = dct['send_line_hotkey']

        self.conv_dict = dct['conv_dict']
        self.yoon = dct['yoon']
        self.sokuon = dct['sokuon']
        self.kigo = dct['kigo']
        self.alphabet = dct['alphabet']
        self.katakana = dct['katakana']
        self.highlight = dct['highlight']

    class ConfigEncoder(json.JSONEncoder):
        """JSON Encoder class for Config."""
        # pylint: disable=method-hidden

        def default(self, o):
            return o.__dict__


# test
# def main():
#     cfg = Config()
#     # cfg.save()


# if __name__ == '__main__':
#     main()
