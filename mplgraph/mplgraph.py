# coding: utf-8

# 参考： 
# Matplotlib描画画像をFlaskによるWebアプリにてBytesIO を介して直接表示する方法
# https://qiita.com/SatoshiTerasaki/items/8d79ec9d463bf0ce3595
# Python 3：3次元グラフの書き方
# https://qiita.com/orange_u/items/8a1e285a45093857aef7

from flask import Flask, Blueprint, request, render_template, redirect, url_for, send_file

from io import BytesIO
import urllib
import matplotlib       # 筆者の環境(M1 Macbook)ではエラーが出るので、
matplotlib.use('Agg')   # この2行を追加した。
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import os

app = Blueprint('mplgraph', __name__, url_prefix='/mplgraph', template_folder='mplgraph_templates')

# 受信データを表示するための文字列の初期値
sensor = 'No data received from the sensor.'

# /download にアクセスしたときの処理
@app.route('/download')
def download():
    print('DEBUG: Download function was called.')

    # 蓄積されたデータが存在したと仮定して、仮のデータを作る。
    data = [
        ['TIME','Latitude','Longitude','Temperature'],
        ['2019-07-01 15:00:00','9997','1740','25.0'],
        ['2019-07-02 15:00:00','9997','1749','26.0'],
        ['2019-07-03 15:00:00','9997','1757','27.0'],
        ['2019-07-04 15:00:00','9997','1769','26.5'],
        ['2019-07-05 15:00:00','9997','1762','29.0'],
        ['2019-07-08 15:00:00','9997','1760','32.0']
    ]
    # Pandasデータフレームに変換（この状態でデータを保持しているとする）
    df = pd.DataFrame(data)

    # ここからはファイルを送信する処理
    # 参考: https://qiita.com/5zm/items/760000cf63b176be544c

    # いったんファイルを保存する
    filename = 'mplgraph/SensorData.csv'
    df.to_csv(filename)

    CSV_MIMETYPE = 'text/csv'
    downloadFileName = filename
    downloadFile = filename
    return send_file(downloadFile, as_attachment=True, \
        attachment_filename=downloadFileName, mimetype=CSV_MIMETYPE)


# /post にアクセスしたときの処理
@app.route('/post', methods=['GET', 'POST'])
def post():
    global sensor

    print('DEBUG: Sensor data was received.')

    temp  = -999.0;
    humid = -999.0;
    hidx  = -999.0;

    # POSTかGETでデータ受信を試みる
    try:
        if request.method == 'POST':
            temp  = float(request.form['temp'])
            humid = float(request.form['humid'])
            hidx  = float(request.form['hidx'])
        else:
            temp  = float(request.args.get('temp', ''))
            humid = float(request.args.get('humid', ''))
            hidx  = float(request.args.get('hidx', ''))
    except Exception as e:
        print('DEBUG: DATA ERROR\n')
        return str(e)

    sensor = "Temperature:"+str(temp)+" Humidity:"+str(humid)+" HeatIndex:"+str(hidx)
    print(sensor)
    return redirect(url_for('mplgraph.index'))


# グラフの例：引数の2乗和を計算する関数
def func1(x, y):
    return x**2 + y**2


@app.route("/plot/<func>")
def plot_graph(func='sin'):

    if func == '3d':

        # 描写データの作成
        # 3次元で描写するには2次元メッシュが必要
        # 2次元配列をarangeを用いて作る
        # x, y をそれぞれ1次元領域で分割する
        x = np.arange(-3.0, 3.0, 0.1)
        y = np.arange(-3.0, 3.0, 0.1)

        # 3次元の離散データを適当に準備
        ds = np.array([[0, 0,18],[5, 0,18],[10, 0,20],[15, 0,25],[20, 0,28],
                    [0, 5,18],[5, 5,19],[10, 5,19],[15, 5,23],[20, 5,25],
                    [0,10,18],[5,10,20],[10,10,22],[15,10,22],[20,10,23],
                    [0,20,18],[5,20,19],[10,20,16],[15,20,15],[20,20,17]])
        X = ds[:,[0]]
        Y = ds[:,[1]]
        Z = ds[:,[2]]

        # 3次元離散グラフを描画
        # Figureで2次元の図を生成し、Axes3D関数で3次元にする
        fig = Figure()
        ax = Axes3D(fig)

        # 軸ラベルの設定
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("Temperature")

        # グラフ描写
        ax.scatter(X, Y, Z, s=40, c="blue")
        #plt.show()

    elif func == '3dsin':

        # 描写データの作成
        # 3次元で描写するには2次元メッシュが必要
        # 2次元配列をarangeを用いて作る
        # x, y をそれぞれ1次元領域で分割する
        x = np.arange(-3.0, 3.0, 0.1)
        y = np.arange(-3.0, 3.0, 0.1)

        # 2次元メッシュはmeshgridでつくる
        # Xの行にxの行列を，Yは列にyの配列を入れたものになっている
        X, Y = np.meshgrid(x, y)
        Z = func1(X, Y)

        # グラフの作成
        # figureで2次元の図を生成する
        # その後，Axes3D関数で3次元にする
        fig = Figure()
        ax = Axes3D(fig)

        # 軸ラベルの設定
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("f(x, y)")

        # グラフ描写
        ax.plot_wireframe(X, Y, Z)
        #plt.show()

    elif func == '3dhotaka':

        # 地形図のプロットはここを参考
        # http://memomemokun.hateblo.jp/entry/2018/11/02/093839
        # 国土地理院のデータについては別途調査
        # 離散データをグリッド化する方法も別途調査した

        # 地形データの読み込み
        # CSVには 緯度,経度,高度 の順にデータが格納されている
        # このデータは離散的なデータなのでグリッド化が必要
        df = pd.read_csv('mplgraph/hotaka2.csv', names=('Latitude', 'Longitude', 'Altitude'))
        LatData = df['Latitude']
        LonData = df['Longitude']
        AltData = df['Altitude']

        # 緯度-経度 のメッシュグリッドを作成
        # np.linespace(最初の値, 最後の値, 要素数)
        lat = np.linspace(LatData.min(), LatData.max(), 256)
        lon = np.linspace(LonData.min(), LonData.max(), 256)
        Lat, Lon = np.meshgrid(lat, lon)

        # グリッド化する
        Alt = griddata((LatData, LonData), AltData, (Lat, Lon))

        # figureで2次元の図を生成し、Axes3D関数で3次元にする
        fig = plt.figure(figsize=(13, 10), dpi=80, facecolor='w', edgecolor='k')

        ax = Axes3D(fig)

        # 上高地の遙か上空ぐらいから前穂高越しに地形を見下ろす感じに視点を設定
        ax.view_init(70, -67)

        # 軸ラベルの設定
        ax.set_xlabel("Latitude")
        ax.set_ylabel("Longitude")
        ax.set_zlabel("Altitude")

        # グラフ描写
        ax.plot_wireframe(Lat, Lon, Alt, rstride=1, cstride=2, linewidth=1)
        #plt.show()

    elif func == '3dhotaka2':

        # 地形データの読み込み
        # CSVには 緯度,経度,高度 の順にデータが格納されている
        # このデータは離散的なデータなのでグリッド化が必要
        df = pd.read_csv('mplgraph/hotaka2.csv', names=('Latitude', 'Longitude', 'Altitude'))
        LatData = df['Latitude']
        LonData = df['Longitude']
        AltData = df['Altitude']

        # 緯度-経度 のメッシュグリッドを作成
        # np.linespace(最初の値, 最後の値, 要素数)
        lat = np.linspace(LatData.min(), LatData.max(), 256)
        lon = np.linspace(LonData.min(), LonData.max(), 256)
        Lat, Lon = np.meshgrid(lat, lon)

        # グリッド化する
        Alt = griddata((LatData, LonData), AltData, (Lat, Lon))

        # figureで2次元の図を生成し、Axes3D関数で3次元にする
        fig = plt.figure(figsize=(13, 10), dpi=80, facecolor='w', edgecolor='k')

        #ax = fig.gca(projection='3d')
        ax = Axes3D(fig)

        # 上高地の遙か上空ぐらいから前穂高越しに地形を見下ろす感じに視点を設定
        ax.view_init(70, -67)

        # 軸ラベルの設定
        ax.set_xlabel("Latitude")
        ax.set_ylabel("Longitude")
        ax.set_zlabel("Altitude")

        #標高25m間隔で等高線を描く
        elevation = range(1500,3500,25)
        cont = plt.contour(Lat, Lon, Alt, levels=elevation, cmap='hot_r')
        
        #ラベルをつける
        cb = plt.colorbar(cont, shrink=0.5, aspect=10)
        
        #plt.savefig('map.jpg', dpi=72)
        #plt.show()

    else:
        fig = Figure()
        ax = fig.add_subplot(111)
        xs = np.linspace(-np.pi, np.pi, 100)
        if func == 'sin':
            ys = np.sin(xs)
        elif func == 'cos':
            ys = np.cos(xs)
        elif func == 'tan':
            ys = np.tan(xs)
        else:
            ys = xs
        ax.plot(xs, ys)

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    img_data = urllib.parse.quote(png_output.getvalue())
    return img_data


@app.route("/")
def index():
    global sensor
    subdir = os.getenv('FLASK_SUBDIR', default='')
    #print("To render:::::: "+sensor)
    return render_template("mplgraph.html", img_data=None, sensor_readings=sensor, flask_subdir=subdir)

if __name__ == "__main__":
    app.run(debug=True)
