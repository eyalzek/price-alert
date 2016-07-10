#!/usr/bin/python
import time
import requests
import smtplib
from urlparse import urljoin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import html
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read("creds")
email_user = config.get('email','user')
email_pass = config.get('email','pass')


# Change these values to your desired sale page (the selector and price check were tested on Amazon).
BASE_URL = "https://www.amazon.co.uk/gp/offer-listing/"
SMTP_URL = "smtp.gmail.com:587"
XPATH_SELECTOR = '//*[contains(@class, "olpOfferPrice")]'
SLEEP_INTERVAL = 10
#ITEMS is a list of lists, storing ASINs and their maximum prices
ITEMS = [("B014GXQ9YW", 80)]

def send_email(price):
    global BASE_URL

    try:
        s = smtplib.SMTP(SMTP_URL)
        s.starttls()
        s.login(email_user, email_pass)
    except smtplib.SMTPAuthenticationError:
        print("Failed to login")
    else:
        print("Logged in! Composing message..")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Price Alert - {}".format(price)
        msg["From"] = email_user
        msg["To"] = email_user
        text = "The price is currently {0} !! URL to salepage: {1}".format(price, BASE_URL)
        part = MIMEText(text, "plain")
        msg.attach(part)
        s.sendmail(email_user, email_user, msg.as_string())
        print("Message has been sent.")

while True:
    #item[0] is the item's ASIN while item[1] is that item's maximum price
    for item in ITEMS:
        r = requests.get(urljoin(BASE_URL, item[0]), verify=False)
        tree = html.fromstring(r.text)
        try:
            elements = tree.xpath(XPATH_SELECTOR)
            #We have to strip the currency sign off of the number to cast it to a float
            prices = [float(p.text.lstrip().rstrip()[1:]) for p in elements]
        except IndexError:
            print("Didn't find the 'price' element, trying again")
            continue
        if any(map(lambda p: p <= item[1], prices)):
            print("Prices are {}!! Trying to send email.".format(prices))
            send_email(price)
            break
        else:
            print("Prices are {}. Ignoring...".format(prices))

    print "Sleeping for {} seconds".format(SLEEP_INTERVAL)
    time.sleep(SLEEP_INTERVAL)
