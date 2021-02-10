### FLASK_DEMO

Flaskアプリのチュートリアル兼アプリの雛形として作成しました。
全体を統合するために Blueprint を使っています。

## 実行方法

$ python3 app.py

## 環境変数

同一サーバー上で別アプリが動作している（例えばWordPress）などの理由によりサブディレクトリで動かす場合、環境変数 FLASK_SUBDIR にディレクトリ名を設定してください。
例. FLASK_SUBDIR=/flask_demo

## デモ内容

# pageswitch

ページ遷移を行う。

# addressbook

住所録。データベースはSQLiteを使用。

# mplgraph

matplotlibを用いてグラフを描画しています。

# filetransfer

CSVファイルのアップロード、およびダウンロード
