楽譜ソフトへの日本語歌詞入力を助ける大雑把なツール。

![スクリーンショット](https://i.imgur.com/zoo2vy1.png)

- Windowsのみ対応のPythonスクリプト
- 次のライブラリが必要 `pip install wx keyboard ginza`
  - ginzaはダウンロードサイズ大きめなので注意
- kasiope.pywを実行して起動

ワークフロー
- このソフトに歌詞を貼り付ける。
- 音符にはまるように、漢字をひらがなに直し、スペースを入れる（要慣れ）。
- 楽譜ソフトに行き、歌詞入力状態にする（Shift+L等）。
- Ctrl+Alt+PageUpでテキストカーソルから一文字ずつ挿入していく。
- もしくは、Ctrl+Alt+PageDownでテキストカーソルから一行まとめて挿入する。
- 途中から入力したい場合は、テキストカーソルをその位置に移動させればよい。

注意点
- DoricoではAltキーを押しているとハイフンが分割されないので、ショートカットキーを押した後にすぐに離すように。
- 一行挿入している最中に歌詞入力状態でなくなっても挿入は止まらない（＝暴走する）。
- 設定はconfig.jsonを自分で編集する。