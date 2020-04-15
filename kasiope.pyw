"""A simple tool for inputting Japanese lyrics to music notation software.

TODO:
    - 非同期でGiNZAをロードしたいがやりかたわからない、要勉強
    - Remove selected characters
    - GiNZAなくても例外処理して起動できるように
    - ウェイト調整UIをつくる
    - マウスかキー入力があったら挿入を止めたい
"""

from os import path

import wx
import keyboard

from config import Config
from kasi_ctrl import KasiCtrl


class KasiopeFrame(wx.Frame):
    """wxPython frame."""

    def __init__(self, cfg):
        style = wx.DEFAULT_FRAME_STYLE | (wx.STAY_ON_TOP if cfg.stay_on_top else 0)

        super(KasiopeFrame, self).__init__(None, wx.ID_ANY, 'Kasiope',
                                           size=cfg.window_size,
                                           style=style)
        self.cfg = cfg

        # ウェイトを上げても脱字するときはする
        self.send_wait = 0.035

        # self.cb_enable_hotkey = None

        # UI構成
        self.root_panel = self._make_root_panel()
        # pylint: disable=invalid-name
        self.kc = KasiCtrl(self.root_panel, self.cfg)
        button_panel = self._make_buttons()

        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(button_panel, 0, wx.EXPAND)
        bsizer.Add(self.kc, 1, wx.EXPAND)
        self.root_panel.SetSizer(bsizer)

        if path.exists("icon.ico"):
            self.SetIcon(wx.Icon("icon.ico"))

        self._add_hotkeys()

    def _make_root_panel(self):
        """Make and return root panel."""
        panel = wx.Panel(self, wx.ID_ANY)
        panel.SetForegroundColour(self.cfg.color1)
        panel.SetBackgroundColour(self.cfg.color2)
        return panel

    def _make_buttons(self):
        """Make and return button panel."""
        panel = wx.Panel(self.root_panel, wx.ID_ANY)

        # https://www.python-izm.com/gui/wxpython/wxpython_button/
        b_kanji_to_kana = wx.Button(panel, wx.ID_ANY, '漢字→かな', style=wx.BORDER_DEFAULT)
        b_remove_whitespace = wx.Button(panel, wx.ID_ANY, '空白除去', style=wx.BORDER_DEFAULT)
        b_insert_spaces = wx.Button(panel, wx.ID_ANY, 'スペース挿入', style=wx.BORDER_DEFAULT)

        # ホットキー有効化ボタン（放置
        # self.cb_enable_hotkey = wx.CheckBox(panel, wx.ID_ANY, 'ホットキー有効')
        # self.cb_enable_hotkey.SetForegroundColour('#DFE2E6')
        # self.cb_enable_hotkey.SetValue(True)

        b_kanji_to_kana.Bind(wx.EVT_BUTTON, self.on_kanji_to_kana)
        b_remove_whitespace.Bind(wx.EVT_BUTTON, self.on_remove_whitespace)
        b_insert_spaces.Bind(wx.EVT_BUTTON, self.on_insert_spaces)

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_bsizer = wx.BoxSizer(wx.HORIZONTAL)

        btn_bsizer.Add(b_kanji_to_kana)
        btn_bsizer.Add(b_remove_whitespace)
        btn_bsizer.Add(b_insert_spaces)

        # cb_bsizer.Add(self.cb_enable_hotkey, flag=wx.ALIGN_RIGHT | wx.EXPAND)

        bsizer.Add(btn_bsizer)
        # bsizer.Add((10, 1))
        # bsizer.Add(self.cb_enable_hotkey, flag=wx.EXPAND)

        panel.SetSizer(bsizer)

        return panel

    def _add_hotkeys(self):
        """Add global hotkeys."""
        keyboard.add_hotkey(self.cfg.send_mora_hotkey, lambda: self.kc.send_mora(self.send_wait))
        keyboard.add_hotkey(self.cfg.send_line_hotkey, lambda: self.kc.send_line(self.send_wait))

        # 半角/全角キーは押しっぱなしの状態になり、
        # 事実上すべてのホットキーを無効化させてしまう。
        # 対策としてコールバックにstash_state()を登録してすぐに離す。
        # 副作用は未知。
        # cf. https://github.com/boppreh/keyboard/issues/223
        keyboard.on_press_key('半角/全角', lambda _: keyboard.stash_state())

    def on_kanji_to_kana(self, _):
        """Button callback."""
        self.kc.kanji_to_hira_all()

    def on_remove_whitespace(self, _):
        """Button callback."""
        self.kc.remove_whitespace()

    def on_insert_spaces(self, _):
        """Button callback."""
        self.kc.insert_spaces()

    # pylint: disable=invalid-name
    def OnQuit(self, _):
        """Close callback."""
        self.Close()


def main():
    """Run application."""
    cfg = Config()
    app = wx.App()
    frame = KasiopeFrame(cfg)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
