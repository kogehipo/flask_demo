# coding: utf-8

from flask import Flask, Blueprint, render_template, request, redirect, url_for
import sqlite3
import datetime

from io import BytesIO
import urllib
import matplotlib       # 筆者の環境(M1 Macbook)ではエラーが出るので、
matplotlib.use('Agg')   # この2行を追加した。
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

app = Blueprint('sensordata', __name__, \
        url_prefix='/flask_demo/sensordata', \
        template_folder='sensordata_templates')

# データベースアクセスのためのグローバル変数
conn: sqlite3.Connection
cur: sqlite3.Cursor
DATABASE_NAME = 'sensordata/SENSOR_DATA.db'

# データベースに接続する
def connect_database():
    global conn, cur
    # データベースを作成して接続する（既に存在していれば再接続）
    conn = sqlite3.connect(DATABASE_NAME)
    cur = conn.cursor()
    # sensor_data というテーブルがまだ無ければ作る。
    sql = 'CREATE TABLE IF NOT EXISTS sensor_data(\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                time DATETIME2,\
                temp FLOAT,\
                humid FLOAT)'
    cur.execute(sql)
    conn.commit()

# 初期画面：これまで受信したデータの表示
@app.route('/')
def index():
    global cur
    connect_database()
    cur.execute('SELECT * FROM sensor_data')
    data = cur.fetchall()
    return render_template('sensordata.html', page='menu', sensor_data=data)
 
# センサーデータの受信
@app.route('/post', methods=['GET'])
def post():
    # GETプロトコルでデータ受信
    try:
        temp  = str(request.args.get('temp', default=-999.0, type=float))
        humid = str(request.args.get('humid', default=-999.0, type=float))
    except Exception as e:
        return str(e)

    # データ管理のため現在時刻も保存する
    time = str(datetime.datetime.now())

    # データベースに格納
    global cur, conn
    connect_database()
    sql = 'INSERT INTO sensor_data(time,temp,humid) VALUES(?,?,?)'
    data = [time,temp,humid]
    cur.execute(sql, data)
    conn.commit()

    # 初期画面に戻る
    return redirect(url_for('index'))

@app.route('/graph')
def graph():
    print('DEBUG: Reached to graph()')
    return render_template('sensordata.html', page='graph')

@app.route('/plot')
def plot():
    print('DEBUG: Reached to plot()')
    global cur
    connect_database()
    cur.execute('SELECT * FROM sensor_data')
    data = cur.fetchall()

    time = []
    temp = []
    humid = []
    start_time = datetime.datetime.strptime(data[0][1], '%Y-%m-%d %H:%M:%S.%f')
    for d in data:
        t = datetime.datetime.strptime(d[1], '%Y-%m-%d %H:%M:%S.%f')
        delta = (t - start_time).seconds
        time = time + [delta]
        temp = temp + [float(d[2])]
        humid = humid + [float(d[3])]

    # グラフの描画
    fig = plt.figure()
    plt.plot(time, temp)
    plt.plot(time, humid)
    #plt.scatter(time, temp, humid)  # 離散グラフならこちらを有効にする
    plt.show()

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    img_data = urllib.parse.quote(png_output.getvalue())
    return img_data

if __name__ == '__main__':
    app.run(debug=True)
