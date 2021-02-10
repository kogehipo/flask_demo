# coding: utf-8

from flask import Flask, Blueprint, render_template, request, send_file, redirect, url_for
import pandas as pd

FILENAME = 'filetransfer/DATATABLE.csv'

app = Blueprint('filetransfer', __name__, \
        url_prefix='/flask_demo/filetransfer', \
        template_folder='filetransfer_templates', \
        static_folder='filetransfer_static')

@app.route('/')
def index():
    try:
        table = pd.read_csv(FILENAME, header=None, encoding='sjis').values.tolist()
    except:
        table = [['データはありません。']]
    print(table)
    return render_template('filetransfer.html', page='index', table=table)

@app.route('/download')
def download():
    CSV_MIMETYPE = 'text/csv'
    return send_file(FILENAME, as_attachment=True, \
        attachment_filename=FILENAME, mimetype=CSV_MIMETYPE, cache_timeout=0)

@app.route('/upload_filename')
def upload_filename():
    return render_template('filetransfer.html', page='upload_filename')

# ファイルのアップロードについてはここを参照: https://blog.imind.jp/entry/2020/01/25/032249
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('filetransfer.html', page='message', message='ファイルが指定されていません。')

    # fileの取得（FileStorage型で取れる）
    # 参考: https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html
    fs = request.files['file']
    if fs.filename == '':
        return render_template('filetransfer.html', page='message', message='ファイルが指定されていません。')

    # ファイルがCSVであることの確認は省略
    # ファイルを保存
    fs.save(FILENAME)
    return redirect(url_for('filetransfer.index'))

if __name__ == '__main__':
    app.run(debug=True)
