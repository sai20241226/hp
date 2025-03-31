from flask import Flask, render_template, request, send_from_directory
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/contact.py', methods=['POST'])
def contact():
    # contact.pyを実行
    process = subprocess.Popen(['python', 'contact.py'],
                           stdin=request.stream,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=os.environ.copy())  # 環境変数をコピー
    stdout, stderr = process.communicate()

    if stderr:
        return f"エラーが発生しました: {stderr.decode('utf-8')}", 500
    else:
        return stdout.decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True)
