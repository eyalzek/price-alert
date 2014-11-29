#!/usr/bin/python
import time
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import html

# Change these values to your desired sale page (the selector and price check were tested on Amazon).
URL = "http://www.amazon.com/exec/obidos/ASIN/B0042A8CW2/websearchengi40-20"
SMTP_URL = "smtp.gmail.com:587"
XPATH_SELECTOR = '//*[@id="priceblock_ourprice"]'
MAX_PRICE = "$100"
SLEEP_INTERVAL = 10

def send_email(price):
    global URL
    email, passwd = [line.strip("\n") for line in tuple(open("creds", "r"))] # replace this with your email credentials

    try:
        s = smtplib.SMTP(SMTP_URL)
        s.starttls()
        s.login(email, passwd)
    except smtplib.SMTPAuthenticationError:
        print("Failed to login")
    else:
        print("Logged in! Composing message..")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Price Alert - {}".format(price)
        msg["From"] = email
        msg["To"] = email
        text = "The price is currently {0} !! URL to salepage: {1}".format(price, URL)
        part = MIMEText(text, "plain")
        msg.attach(part)
        s.sendmail(email, email, msg.as_string())
        print("Message has been sent.")

while True:
    r = requests.get(URL)
    tree = html.fromstring(r.text)
    try:
        price = tree.xpath(XPATH_SELECTOR)[0].text
    except IndexError:
        print("Didn't find the 'price' element, trying again")
        continue
    if price <= MAX_PRICE:
        print("Price is {}!! Trying to send email.".format(price))
        send_email(price)
        break
    else:
        print("Price is {}. Ignoring...".format(price))
        time.sleep(SLEEP_INTERVAL)
