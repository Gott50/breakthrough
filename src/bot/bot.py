import os
import re
from datetime import datetime

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bot.time_util import sleep
from .settings import Settings


class Bot:

    def __init__(self,
                 selenium_local_session=True,
                 page_delay=25,
                 headless_browser=False,
                 proxy_ip=None,
                 proxy_chrome_extension=None,
                 proxy_port: int = 0,
                 print=print,
                 sleep_time=2):
        print(
            "Bot(selenium_local_session=%s, page_delay=%s, headless_browser=%s, proxy_ip=%s, proxy_chrome_extension=%s, proxy_port: int = %s, print=%s, sleep_time=%s)" %
            (selenium_local_session,
             page_delay,
             headless_browser,
             proxy_ip,
             proxy_chrome_extension,
             proxy_port,
             print,
             sleep_time)
            )

        self.sleep_time = sleep_time
        self.print = print
        self.browser = None
        self.headless_browser = headless_browser
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_chrome_extension = proxy_chrome_extension
        self.page_delay = page_delay
        self.selenium_local_session = selenium_local_session

        if selenium_local_session:
            self.set_selenium_local_session()

    def set_selenium_local_session(self):
        """Starts local session for a selenium server.
        Default case scenario."""
        chromedriver_location = Settings.chromedriver_location
        chrome_options = Options()
        # chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--lang=de-DE')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--incognito')
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # mobile_emulation = {"deviceName": "iPhone 5"}
        # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        # this option implements Chrome Headless, a new (late 2017)
        # GUI-less browser. chromedriver 2.9 and above required
        if self.headless_browser:
            chrome_options.add_argument('--headless')
            # Replaces browser User Agent from "HeadlessChrome".
            user_agent = "Chrome"
            chrome_options.add_argument('user-agent={user_agent}'
                                        .format(user_agent=user_agent))
        # Proxy for chrome
        capabilities = DesiredCapabilities.CHROME
        if self.proxy_ip and (self.proxy_port > 0):
            capabilities['proxy'] = {
                'httpProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'ftpProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'sslProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'noProxy': None,
                'proxyType': "MANUAL",
                'class': "org.openqa.selenium.Proxy",
                'autodetect': False
            }

        # add proxy extension
        if self.proxy_chrome_extension and not self.headless_browser:
            chrome_options.add_extension(self.proxy_chrome_extension)

        chrome_prefs = {
            'intl.accept_languages': 'de-DE'
        }
        chrome_options.add_experimental_option('prefs', chrome_prefs)
        try:
            self.browser = webdriver.Chrome(chromedriver_location,
                                            desired_capabilities=capabilities,
                                            chrome_options=chrome_options)
        except selenium.common.exceptions.WebDriverException as exc:
            self.print(exc)
            raise Exception('ensure chromedriver is installed at {}'.format(
                Settings.chromedriver_location))

        # prevent: Message: unknown error: call function result missing 'value'
        matches = re.match(r'^(\d+\.\d+)',
                           self.browser.capabilities['chrome']['chromedriverVersion'])
        if float(matches.groups()[0]) < Settings.chromedriver_min_version:
            raise Exception('chromedriver {} is not supported, expects {}+'.format(
                float(matches.groups()[0]), Settings.chromedriver_min_version))

        self.browser.implicitly_wait(self.page_delay)
        self.print('Session started - %s'
                   % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def set_selenium_remote_session(self, selenium_url=''):
        """Starts remote session for a selenium server.
         Useful for docker setup."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument("start-maximized")  # open Browser in maximized mode
        chrome_options.add_argument("disable-infobars")  # disabling infobars
        chrome_options.add_argument("--disable-extensions")  # disabling extensions
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # mobile_emulation = {"deviceName": "iPhone 5"}
        # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        # Proxy for chrome
        capabilities = chrome_options.to_capabilities()
        if self.proxy_ip and (self.proxy_port > 0):
            capabilities['proxy'] = {
                'httpProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'ftpProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'sslProxy': "%s:%i" % (self.proxy_ip, self.proxy_port),
                'noProxy': None,
                'proxyType': "MANUAL",
                'class': "org.openqa.selenium.Proxy",
                'autodetect': False
            }

        self.browser = webdriver.Remote(command_executor=selenium_url,
                                        desired_capabilities=capabilities)

        message = "Session started!"

        self.print(message)
        self.print("initialization")
        self.print("info")
        self.print('')

        return self

    def act(self, url=None):
        result = 0
        try:
            driver = self.browser
            u = url or os.environ.get('URL')
            self.print("url: %s" % u)
            driver.get(u)

            sleep(self.sleep_time)

            wait = WebDriverWait(driver, 120)
            iframe = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="APESTER_1"]/iframe')))
            ActionChains(driver).move_to_element(iframe).perform()
            driver.switch_to.frame(iframe)
            sleep(self.sleep_time)
            self.print("switch frame to: %s" % iframe)

            wait = WebDriverWait(driver, 120)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.interactiveMultiChoice')))
            sleep(self.sleep_time)
            self.print("done Waiting for .interactiveMultiChoice")

            choices = driver.find_elements(By.CSS_SELECTOR, '.interactiveMultiChoice div span')
            self.print("choices: ")

            for c in choices:
                self.print(c.text)
                if c.text == 'Wechselgott':
                    ActionChains(driver).move_to_element(c).click(c).perform()
                    result += 1
                    break
            sleep(self.sleep_time * 10)

        except Exception as e:
            self.print(e)

        self.print("result: %s" % result)

        return result

    def end(self):
        """Closes the current session"""
        try:
            self.browser.delete_all_cookies()
            self.browser.quit()
        except WebDriverException as exc:
            self.print('Could not locate Chrome: {}'.format(exc))

        self.print('Session ended - {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.print('-' * 20 + '\n\n')
