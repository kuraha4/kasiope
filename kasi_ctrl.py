"""Text editor widget."""

import platform
import re

import wx

from config import Config
import inputter
import surgeon


class KasiCtrl(wx.TextCtrl):
    """TextCtrl which handles Japanese lyrics."""

    def __init__(self, parent, cfg: Config):
        style = wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_NOHIDESEL
        style |= wx.TE_RICH2
        super(KasiCtrl, self).__init__(parent, wx.ID_ANY, style=style)

        self.cfg = cfg

        self.surg = surgeon.Surgeon(cfg)
        self.surg.load_ginza()

        # 必要な箇所だけSetStyle()をするための情報
        self.needs_restyle_all = False
        self.needs_restyle_range = None

        # Font
        # https://wxpython.org/Phoenix/docs/html/wx.Font.html
        if platform.system() == 'Windows':
            font = wx.Font(cfg.font_size,
                           wx.FONTFAMILY_DEFAULT,
                           wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL,
                           faceName='メイリオ')
        else:
            font = wx.Font(cfg.font_size,
                           wx.FONTFAMILY_DEFAULT,
                           wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)
        # self.SetDefaultStyle(wx.TextAttr(None, font=font))
        #self.needs_restyle_all = True
        #self.SetStyle(0, self.GetLastPosition(), self.GetDefaultStyle())

        # フォントのあとに色変えないとフォントの色が変わらない
        self.SetForegroundColour(cfg.text_color)
        self.SetBackgroundColour(cfg.color1)

        # Margin
        # print(self.GetMargins())
        # self.SetMargins(1, 1)

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self, 1, wx.EXPAND)
        parent.SetSizerAndFit(bsizer)

        self.Bind(wx.EVT_TEXT_PASTE, self.on_text_paste)
        self.Bind(wx.EVT_TEXT, self.on_text)

    @property
    def text(self):
        """Return all text entered in TextCtrl."""
        return self.GetValue()

    def get_range(self, _from, _to=None):
        """Return a string in given range."""
        if _to is None:
            _to = self.GetLastPosition()
        return self.GetRange(_from, _to)

    def remove_whitespace(self):
        """Return a string with removed all whitespaces except newline."""
        new_text = re.sub(r"[^\S\r\n]", "", self.text)
        # 戻すには2回undoする必要がある
        # SetValueだとundoすら効かないしとりあえずこれで
        self.replace_all(new_text)

    def insert_spaces(self):
        """Insert space between mora and return it."""
        new_text = ""
        for line in self.text.splitlines():
            new_text += " ".join(self.surg.mora(line)) + "\n"
        self.replace_all(new_text)

    def kanji_to_hira_selected(self):
        """Transliterate kanji to hiragana in selected text."""
        selected = self.GetStringSelection()
        conved = self.surg.kanji_to_hira(selected)

        start, end = self.GetSelection()
        self.replace_range(start, end, conved)

    def kanji_to_hira_all(self):
        """Transliterate all kanji to hiragana in text."""
        conved = self.surg.kanji_to_hira(self.GetValue())
        self.replace_all(conved)

    def show_eof_window(self):
        """Tell the user that the caret is at EOF."""
        dlg = wx.MessageDialog(self,
                               ('終端に到達しました。\n'
                                '文字送出を始めたい位置にテキストカーソルを移動させてください。'),
                               '情報')
        dlg.ShowModal()
        dlg.Destroy()

    def send_mora(self, wait):
        """Send out a mora and advance the caret."""
        # TextCtrlから取得したポジションは、
        # 取得した文字列のインデックスとして使えないので注意
        pos = self.GetInsertionPoint()

        # キャレットが終端にあるときは何もしない
        if pos == self.GetLastPosition():
            self.show_eof_window()
            return

        match = re.search(r'\s+', self.get_range(pos))

        if match:
            print(f'group: {match.group()}, start: {match.start()}, end: {match.end()}')

            # キャレットの位置はposから数えるのを忘れないように
            inputter.send_string(self.get_range(pos, pos + match.start()) + ' ', wait)

            # SetInsertionPoint()では、改行は1つで2文字分数えるので、不足分を足す
            newlines = match.group().count('\n')

            self.SetInsertionPoint(pos + match.end() + newlines)

        else:
            # Last one
            inputter.send_string(self.get_range(pos) + '\n', wait)
            self.SetInsertionPointEnd()

    def send_line(self, wait):
        """Send out a line and advance the caret."""
        print('send_line() called')
        pos = self.GetInsertionPoint()
        if pos == self.GetLastPosition():
            self.show_eof_window()
            return

        # 1つ目のboolは領域内にあったかどうかかな多分
        # pylint: disable=invalid-name
        _, x, y = self.PositionToXY(pos)

        # キャレットから行末までを送出
        # 末尾にスペース追加
        line = self.GetLineText(y)
        inputter.send_string(line[x:] + ' ', wait)

        # キャレットは次の空行でない行の先頭に移動
        new_pos = self.XYToPosition(0, y+1)

        match = re.search(r'^[\r\n]+', self.get_range(new_pos))
        if match:
            # TextCtrlの位置にするときは、改行は2つ数える
            new_pos += match.end() * 2

        self.SetInsertionPoint(new_pos)

    def highlight(self, start, end):
        """Highlight character."""
        # SetStyle()によってスクロールしてしまうのを回避
        self.Freeze()

        print(f'highlight from {start} to {end}')
        df_style = self.GetDefaultStyle()
        hl_style = wx.TextAttr("black", "white")

        pattern = re.compile(f'[{"".join(self.cfg.highlight)}]')

        no_highlight_cur = self.get_line_head(start)
        left = -1
        right = -1
        for match in pattern.finditer(self.get_range(start, end)):

            left = start + match.start()
            right = start + match.end()

            print(left, right, no_highlight_cur)

            # don't highlight
            self.SetStyle(no_highlight_cur, left, df_style)

            # print(f'setstyle from {left} to {right}')
            ret = self.SetStyle(left, right, hl_style)
            # print(ret)

            no_highlight_cur = right

        # print(left, right, no_highlight_cur, self.get_line_end(no_highlight_cur))
        ret = self.SetStyle(no_highlight_cur, self.get_line_end(no_highlight_cur), df_style)
        # print(ret)

        self.Thaw()

    def replace_range(self, start, end, new_text):
        """Replace text in range and set text style."""
        # restyleは行ごとに行うとよさそう
        self.needs_restyle_range = (start, end)
        self.Replace(start, end, new_text)

    def replace_all(self, new_text):
        """Replace all text and set text style."""
        # restyleは行ごとに行うとよさそう
        self.needs_restyle_all = True
        self.Replace(0, self.GetLastPosition(), new_text)

    def on_text(self, event):
        """Event handler."""
        # テキスト入力時、キャレットが移動したあとにイベントハンドラーが呼ばれる
        if self.needs_restyle_all:
            start, end = 0, self.GetLastPosition()
            self.needs_restyle_all = False
            self.highlight(start, end)

        elif self.needs_restyle_range:
            start, end = self.needs_restyle_range
            start, _ = self.get_line_range(start)
            _, end = self.get_line_range(end)
            self.needs_restyle_range = None
            self.highlight(start, end)

        else:
            # ハイライトする文字を一文字だけ入力したとき、後続する文字もハイライトされてしまう
            # デフォルトに戻してるつもりなんだが……
            # 日本語入力では一般に、一度に複数文字入力されるので注意
            #start, end = self.get_line_range(self.GetInsertionPoint())
            # self.highlight(start, end)
            pass

        event.Skip()

    def on_text_paste(self, event):
        """Event handler."""
        # ここではまだTextCtrlにペーストはされていない
        self.needs_restyle_all = True
        event.Skip()

    def get_line_range(self, pos):
        """posのある行の始点と終点のポジションを返す。"""
        return self.get_line_head(pos), self.get_line_end(pos)

    def get_line_number(self, pos):
        """Return a line number of given position."""
        return len(self.GetRange(0, pos).split("\n"))

    def get_line_head(self, pos):
        """Return a head position of given position's line."""
        # pylint: disable=invalid-name
        _, _, y = self.PositionToXY(pos)
        return self.XYToPosition(0, y)

    def get_line_end(self, pos):
        """Return a end position of given position's line."""
        head = self.get_line_head(pos)
        line_len = self.GetLineLength(self.get_line_number(pos))
        return head + line_len
