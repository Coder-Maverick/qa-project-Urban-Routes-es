import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time


def retrieve_phone_code(driver) -> str:
    import json
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    phone_field = (By.ID, 'phone')
    phone_confirm_button = (By.ID, 'phone-confirm')
    code_field = (By.ID, 'code')
    comment_field = (By.XPATH, '//textarea[@id="comment"]')
    blanket_button = (By.ID, 'comfort')
    ice_cream_button = (By.CLASS_NAME, 'ice-cream')
    order_button = (By.ID, 'order')
    driver_info = (By.CLASS_NAME, 'driver-info')
    card_button = (By.ID, 'card')
    card_number_input = (By.CLASS_NAME, 'card-number-input')
    submit_card_button = (By.ID, 'submit-card')

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.from_field)
        ).send_keys(from_address)

    def set_to(self, to_address):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.to_field)
        ).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=options)

    def setup_method(self):
        self.driver.get(data.urban_routes_url)
        self.page = UrbanRoutesPage(self.driver)
        self.wait = WebDriverWait(self.driver, 10)

    def test_set_route(self):
        self.page.set_from(data.address_from)
        self.page.set_to(data.address_to)
        assert self.page.get_from() == data.address_from
        assert self.page.get_to() == data.address_to

    def test_select_plan(self):
        plan_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-for="tariff-card-4"]')))
        plan_button.click()
        assert 'selected' in plan_button.get_attribute('class')

    def test_fill_phone_number(self):
        self.page.driver.find_element(*self.page.phone_field).send_keys(data.phone_number)
        self.page.driver.find_element(*self.page.phone_confirm_button).click()
        assert self.wait.until(EC.presence_of_element_located(self.page.code_field))

    def test_fill_card(self):
        self.page.driver.find_element(*self.page.card_button).click()
        self.page.driver.find_element(*self.page.card_number_input).send_keys(data.card_number)
        cvv_field = self.wait.until(EC.element_to_be_clickable(self.page.code_field))
        cvv_field.send_keys(data.card_code)
        cvv_field.send_keys(Keys.TAB)
        self.page.driver.find_element(*self.page.submit_card_button).click()
        assert self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "card-item")]')))

    def test_comment_for_driver(self):
        comment_box = self.wait.until(EC.presence_of_element_located(self.page.comment_field))
        comment_box.send_keys(data.message_for_driver)
        assert comment_box.get_property('value') == data.message_for_driver

    def test_order_blanket_and_handkerchiefs(self):
        blanket_button = self.wait.until(EC.element_to_be_clickable(self.page.blanket_button))
        blanket_button.click()
        assert 'active' in blanket_button.get_attribute('class')

    def test_order_2_ice_creams(self):
        ice_button = self.wait.until(EC.element_to_be_clickable(self.page.ice_cream_button))
        ice_button.click()
        ice_button.click()
        count = len(self.page.driver.find_elements(By.XPATH, '//div[@class="ice-cream selected"]'))
        assert count == 2

    def test_car_search_model_appears(self):
        self.page.driver.find_element(*self.page.order_button).click()
        assert self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "car-model")]')))

    def test_driver_info_appears(self):
        assert self.wait.until(EC.presence_of_element_located(self.page.driver_info))

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

