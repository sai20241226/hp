#!/usr/bin/env python
import cgi
import smtplib
from email.mime.text import MIMEText
import os
import sys
import traceback

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

# 環境変数からメール設定を取得
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')

if not SENDER_EMAIL or not SENDER_PASSWORD or not ADMIN_EMAIL:
    print("Content-Type: text/html; charset=utf-8")
    print()
    print("メール設定が不足しています。環境変数を設定してください。")
    sys.exit()

form = cgi.FieldStorage()
name = form.getvalue('name')
email = form.getvalue('email')
message = form.getvalue('message')

# 自動返信メール
subject_to_user = "お問い合わせありがとうございます"
body_to_user = f"{name}様\n\nお問い合わせありがとうございます。\n内容を確認後、ご連絡いたします。\n\nお問い合わせ内容:\n{message}"

# 管理者向け通知メール
subject_to_admin = "ウェブサイトからのお問い合わせ"
body_to_admin = f"氏名: {name}\nメールアドレス: {email}\nお問い合わせ内容:\n{message}"

# メール送信
success_user, error_user = send_email(SENDER_EMAIL, SENDER_PASSWORD, email, subject_to_user, body_to_user)
success_admin, error_admin = send_email(SENDER_EMAIL, SENDER_PASSWORD, ADMIN_EMAIL, subject_to_admin, body_to_admin)

print("Content-Type: text/html; charset=utf-8")
print()

if success_user and success_admin:
    print("<p>送信完了しました。お問い合わせありがとうございます。</p>")
else:
    print("<p>送信に失敗しました。もう一度お試しください。</p>")
    if error_user:
        print(f"<p>エラー（ユーザー）: {error_user}</p>")
    if error_admin:
        print(f"<p>エラー（管理者）: {error_admin}</p>")
