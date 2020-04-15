"""日本語の操作。"""

from typing import List
import re
import unicodedata

import spacy
# import pykakasi

from config import Config


class Surgeon():
    """A class which does some operations on Japanese text."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.nlp = None
        # Placeholder for katakana replacement
        self.kata_ph = r'{@Katakana@}'

    def load_ginza(self, ):
        """Load GiNZA library."""
        # pykakasiより読みがうまいが、ロードに少し時間がかかる
        self.nlp = spacy.load('ja_ginza')
        print('GiNZA loaded')

    def mora(self, text):
        """Return a list of moras from given string."""
        result: List[str] = []

        is_first = True
        in_alphabet_word = False

        # あーこれ再帰使うのか？
        # 適当に書くとやばくなりそうなのでよく考える必要あり
        for chara in text:
            if chara == ' ':
                in_alphabet_word = False
            elif chara in self.cfg.yoon + self.cfg.kigo:
                # 拗音と約物は前のモーラにくっつける
                if is_first:
                    result.append(chara)
                else:
                    result[len(result)-1] += chara
            elif chara in self.cfg.alphabet:
                # アルファベットはとりあえず無視
                if is_first:
                    result.append(chara)
                    in_alphabet_word = True
                else:
                    if in_alphabet_word:
                        result[len(result)-1] += chara
                    else:
                        result.append(chara)
                        in_alphabet_word = True
            else:
                result.append(chara)

            is_first = False

        return result

    def kanji_to_hira(self, jpstr):
        """"Transliterate kanji to kana, while keeping katakana."""
        # 辞書登録された語を先にかな化する
        for kanji, kana in self.cfg.conv_dict:
            jpstr = jpstr.replace(kanji, kana)

        # カタカナの連なりをマッチ
        pattern = re.compile(f'[{self.cfg.katakana}]+')
        match = pattern.findall(jpstr)

        # カタカナをプレースホルダーに置き換える
        re.sub(pattern, jpstr, self.kata_ph)

        # 漢字かな変換
        # GiNZAは改行含む空白文字を消去してしまうので、自分で保存する
        whitespace_ptn = re.compile(r'\s+')
        converted = ''
        cur = 0

        for ws_m in whitespace_ptn.finditer(jpstr):
            converted += self._ginza(jpstr[cur:ws_m.start()]) + ws_m.group()
            cur = ws_m.end()
        # remaining string
        converted += self._ginza(jpstr[cur:])

        # カタカナを元に戻す
        for katakana in match:
            converted.replace(self.kata_ph, katakana, 1)

        return converted

    def _ginza(self, jpstr):
        """Return a string transliterated by GiNZA.
        Given string's whitespace will be removed."""
        doc = self.nlp(jpstr)

        # カタカナのUnicode範囲パターン
        kata_ptn = re.compile('[\u30A1-\u30FF]+')

        result = ""
        for sent in doc.sents:
            for token in sent:
                if self.has_hankaku(token.orth_) or token.pos_ == 'PUNCT':
                    result += token.orth_
                    continue
                # info = [
                #     token.i,         # トークン番号
                #     token.orth_,     # テキスト
                #     token._.reading,  # 読みカナ
                #     token.lemma_,    # 基本形
                #     token.pos_,      # 品詞
                #     token.tag_,      # 品詞詳細
                #     token._.inf      # 活用情報
                # ]
                # print(info)
                if kata_ptn.search(token.orth_):
                    # 元の文字列にカタカナが存在するなら
                    result += token.orth_
                else:
                    result += self.kata_to_hira(token._.reading)

        return result

    # def kanji_to_hira_kakasi(self, jptext):
    #     """"Transliterate kanji to kana, while keeping katakana."""
    #     # 辞書登録された語を先にかな化する
    #     for kanji, kana in self.cfg.conv_dict:
    #         jptext = jptext.replace(kanji, kana)

    #     # カタカナの連なりをマッチ
    #     pattern = re.compile(f'[{self.cfg.katakana}]+')
    #     match = pattern.findall(jptext)

    #     # カタカナをプレースホルダーに置き換える
    #     re.sub(pattern, jptext, self.kata_ph)

    #     # 漢字かな変換
    #     kakasi = pykakasi.kakasi()
    #     kakasi.setMode('J', 'H')  # Japanese to furigana
    #     conv = kakasi.getConverter()
    #     converted = conv.do(jptext)

    #     # カタカナを元に戻す
    #     for katakana in match:
    #         converted.replace(self.kata_ph, katakana, 1)

    #     return converted

    def kata_to_hira(self, jpstr):
        """Convert katakana to hiragana."""
        return ''.join([chr(ord(ch) - 96) if ('ァ' <= ch <= 'ヴ') else ch for ch in jpstr])

    def has_hankaku(self, jpstr):
        """Return True only if given string has hankaku character."""
        for char in jpstr:
            if unicodedata.east_asian_width(char) == 'Na':
                return True
        return False


def main():
    """test"""
    cfg = Config()
    surg = Surgeon(cfg)
    surg.load_ginza()
    print(surg.kanji_to_hira('夜空に瞬くシリウスの煌めき'))


if __name__ == '__main__':
    main()
