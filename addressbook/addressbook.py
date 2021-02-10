# coding: utf-8
 
from flask import Flask, Blueprint, render_template, request, redirect, url_for
# このプログラムではsqlite3を使います。
import sqlite3

app = Blueprint('addressbook', __name__, \
        url_prefix='/flask_demo/addressbook', \
        template_folder='addressbook_templates')

# データベースアクセスのためのグローバル変数
conn: sqlite3.Connection
cur: sqlite3.Cursor
DATABASE_NAME = 'addressbook/ADDRESS_BOOK.db'
 
# データベースに接続するための関数。重複して呼ばれても問題ないように考慮してある。
def connect_database():
    global conn, cur
    # データベースを作成して接続する（既に存在していれば再接続）
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    # address_book というテーブルがまだ無ければ作る。
    sql = 'CREATE TABLE IF NOT EXISTS address_book(\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                name STRING,\
                address STRING)'
    cur.execute(sql)
    conn.commit()
 
# 初期画面：現在の住所録を表示する
@app.route('/')
def index():
    global cur
    connect_database()
    cur.execute('SELECT * FROM address_book')
    data = cur.fetchall()
    return render_template('addressbook.html', page='menu', address_book=data)

# 住所入力の画面を表示
@app.route('/input')
def input():
    return render_template('addressbook.html', page='input')
 
# 入力された住所データをデータベースに格納する
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    try:
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
        else:
            name = request.args.get('name', '')
            address = request.args.get('address', '')
    except Exception as e:
        return str(e)
 
    # 本当はここで入力データのチェックが必要だが省略している。
    # ・SQLインジェクションへの対策
    # ・データの妥当性チェック
    # ・重複登録の確認・排除、etc.
 
    # データベースに格納
    global cur, conn
    connect_database()
    sql = 'INSERT INTO address_book(name,address) VALUES(?,?)'
    data = [name,address]
    cur.execute(sql, data)
    conn.commit()
 
    # 初期画面に遷移させる
    return redirect(url_for('addressbook.index'))
 
if __name__ == '__main__':
    app.run(debug=True)
