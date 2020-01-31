import os
import unittest
import httpretty
import requests
import logging
from sure import expect
from price_alert import config_logger, get_price, env_override


class TestPriceAlert(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestPriceAlert, self).__init__(*args, **kwargs)
        self.url = "http://localhost:8090/TESTITEM"
        self.html_body = '<span id="priceblock_ourprice">1234&nbsp;€</span>'
        self.xpath_selector = "//*[@id='priceblock_ourprice']"

    def setUp(self):
        config_logger(False)
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, self.url,
                               body=self.html_body,
                               content_type="application/json")

    def test_get_price(self):
        price = get_price(self.url, self.xpath_selector)
        expect(price).to.equal(1234)

    def test_get_price_not_found(self):
        price = get_price(self.url, "//*[@id='wrong']")
        expect(price).to.equal(None)

    def test_env_override(self):
        os.environ['PRICE_ALERT_BASE_URL'] = 'http://test.local'
        os.environ['PRICE_ALERT_XPATH_SELECTOR'] = 'test.local'
        os.environ['PRICE_ALERT_EMAIL__SMTP_URL'] = 'test.local:587'
        os.environ['PRICE_ALERT_EMAIL__USER'] = 'test@example.com'
        os.environ['PRICE_ALERT_EMAIL__PASSWORD'] = 'test1234'
        config = env_override({})
        expect(config).to.equal({
            'email': {
                'smtp_url': 'test.local:587',
                'user': 'test@example.com',
                'password': 'test1234'
            },
            'base_url': 'http://test.local',
            'xpath_selector': 'test.local'
        })

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()


if __name__ == '__main__':
    unittest.main()
