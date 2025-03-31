from flask import Flask, render_template, request, send_from_directory
import subprocess
import os
import cgi
import smtplib
from email.mime.text import MIMEText
import sys
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/contact', methods=['POST'])
def contact():
    # 環境変数からメール設定を取得
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

    if not SENDER_EMAIL or not SENDER_PASSWORD or not ADMIN_EMAIL:
        return "メール設定が不足しています。環境変数を設定してください。", 500

    form = cgi.FieldStorage(fp=request.stream, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE': request.headers['Content-Type']})
    name = form.getvalue('name')
    email = form.getvalue('email')
    message = form.getvalue('message')

    # 自動返信メール
    subject_to_user = "お問い合わせありがとうございます"
    body_to_user = f"{name}様\n\nお問い合わせありがとうございます。\n内容を確認後、ご連絡いたします。\n\nお問い合わせ内容:\n{message}"

    # 管理者向け通知メール
    subject_to_admin = "ウェブサイトからのお問い合わせ"
    body_to_admin = f"氏名: {name}\nメールアドレス: {email}\nお問い合わせ内容:\n{message}"

    def send_email(sender_email, sender_password, recipient_email, subject, body):
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            return True, None
        except Exception as e:
            return False, str(e)

    # メール送信
    success_user, error_user = send_email(SENDER_EMAIL, SENDER_PASSWORD, email, subject_to_user, body_to_user)
    success_admin, error_admin = send_email(SENDER_EMAIL, SENDER_PASSWORD, ADMIN_EMAIL, subject_to_admin, body_to_admin)

    if success_user and success_admin:
        return "<p>送信完了しました。お問い合わせありがとうございます。</p>"
    else:
        error_message = "<p>送信に失敗しました。もう一度お試しください。</p>"
        if error_user:
            error_message += f"<p>エラー（ユーザー）: {error_user}</p>"
        if error_admin:
            error_message += f"<p>エラー（管理者）: {error_admin}</p>"
        return error_message, 500

if __name__ == '__main__':
    app.run(debug=True)
