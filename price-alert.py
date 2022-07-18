#!/usr/bin/env python3

import re
import time
import requests
import smtplib
import logging
import click
import json
from copy import copy
from lxml import html
from urllib.parse import urljoin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cfg import (
    default_pool_interval,
    default_debug,
    default_base_url,
    default_xpath_selector,
    default_items,
    default_smtp_url,
    default_user_email,
    default_pass_email,
)


def send_email(price, url, email_info):
    try:
        s = smtplib.SMTP(email_info['smtp_url'])
        s.starttls()
        s.login(email_info['user'], email_info['password'])
    except smtplib.SMTPAuthenticationError:
        logger.info('Failed to login')
    else:
        logger.info('Logged in! Composing message..')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Price Alert - %s' % price
        msg['From'] = email_info['user']
        msg['To'] = email_info['user']
        text = 'The price is currently %s !! URL to salepage: %s' % (
            price, url)
        part = MIMEText(text, 'plain')
        msg.attach(part)
        s.sendmail(email_info['user'], email_info['user'], msg.as_string())
        logger.info('Message has been sent.')


def get_price(url, selector):
    r = requests.Session().get(url, headers={
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    })
    r.raise_for_status()
    tree = html.fromstring(r.text)
    try:
        # extract the price from the string
        price_string = re.findall('\d+.\d+', tree.xpath(selector)[0].text)[0]
        logger.info(price_string)
        return float(price_string.replace(',', '.'))
    except (IndexError, TypeError) as e:
        logger.debug(e)
        logger.info('Didn\'t find the \'price\' element, trying again later')


def config_logger(debug):
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)


@click.command()
@click.option('-t', '--pool-interval',
              type=int, default=default_pool_interval,
              help='Time in seconds between checks')
@click.option('-d', '--debug',
              type=bool, default=default_debug,
              help='If true set debug level to DEBUG')
@click.option('-b', '--base-url',
              type=str, default=default_base_url,
              help='base url to crawl.')
@click.option('-x', '--xpath-selector',
              type=str, default=default_xpath_selector,
              help='xpath selector to crawl.')
@click.option('-i', '--json-items',
              type=str, default=default_items,
              help='List of items to crawl in json format')
@click.option('-s', '--smtp-url',
              type=str, default=default_smtp_url,
              help='smtp url for the email notification')
@click.option('-u', '--user-email',
              type=str, default=default_user_email,
              help='user for the email notification')
@click.option('-p', '--pass-email',
              type=str, default=default_pass_email,
              help='password for the email notification')
def main(
    pool_interval, debug, base_url, xpath_selector, json_items, smtp_url,
    user_email, pass_email
):
    config_logger(debug)

    email = {
        "smtp_url": smtp_url,
        "user": user_email,
        "password": pass_email
    }
    items = json.loads(json_items)

    while True and len(items):
        for item in copy(items):
            logger.info(f'Checking price for {item[0]} (should be lower than {item[1]})')
            item_page = urljoin(base_url, item[0])
            price = get_price(item_page, xpath_selector)
            if not price:
                logger.info(f'No price found for {item_page}')
                continue
            elif price <= item[1]:
                logger.info(f'Price is {price}!! Trying to send email.')
                send_email(price, item_page, email)
                items.remove(item)
            else:
                logger.info(f'Price is {price}. Ignoring...')

        if len(items):
            logger.info(f'Sleeping for {pool_interval} seconds')
            time.sleep(pool_interval)
        else:
            break
    logger.info('Price alert triggered for all items, exiting.')


if __name__ == '__main__':
    main()
