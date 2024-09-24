

import smtplib
from email.mime.text import MIMEText


app_passowrd = "hhuk hkyo sgxm unmi"
subject = "python email"
body = "This is the body of the text message"
sender = "smalldragon89@gmail.com"
recipients = ["smalldragon89@gmail.com"]
password = app_passowrd


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


# send_email(subject, body, sender, recipients, password)