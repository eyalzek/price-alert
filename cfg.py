from decouple import AutoConfig


config = AutoConfig()

default_pool_interval = config("POOL_INTERVAL", 30)
default_debug = config("DEBUG", False)
default_base_url = config("BASE_URL", "")
default_xpath_selector = config("XPATH_SELECTOR", "")
default_items = config("ITEMS", "")
default_smtp_url = config("SMTP_URL", "")
default_user_email = config("USER_EMAIL", "")
default_pass_email = config("PASS_EMAIL", "")
