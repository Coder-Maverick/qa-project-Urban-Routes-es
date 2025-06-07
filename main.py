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

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        page = UrbanRoutesPage(self.driver)
        page.set_from(data.address_from)
        page.set_to(data.address_to)
        assert page.get_from() == data.address_from
        assert page.get_to() == data.address_to

    def test_order_taxi(self):
        self.driver.get(data.urban_routes_url)
        wait = WebDriverWait(self.driver, 10)
        page = UrbanRoutesPage(self.driver)

        # Dirección
        page.set_from(data.address_from)
        page.set_to(data.address_to)

        # Seleccionar tarifa Comfort
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-for="tariff-card-4"]'))).click()

        # Número de teléfono
        wait.until(EC.element_to_be_clickable((By.ID, 'phone'))).send_keys(data.phone_number)
        wait.until(EC.element_to_be_clickable((By.ID, 'phone-confirm'))).click()

        # Obtener código SMS
        code = retrieve_phone_code(self.driver)
        wait.until(EC.element_to_be_clickable((By.ID, 'code'))).send_keys(code)

        # Agregar tarjeta
        wait.until(EC.element_to_be_clickable((By.ID, 'card'))).click()
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'card-number-input'))).send_keys(data.card_number)
        cvv_field = wait.until(EC.element_to_be_clickable((By.ID, 'code')))
        cvv_field.send_keys(data.card_code)
        cvv_field.send_keys(Keys.TAB)  # para activar el botón "link"
        wait.until(EC.element_to_be_clickable((By.ID, 'submit-card'))).click()

        # Escribir mensaje al conductor
        wait.until(EC.presence_of_element_located((By.ID, 'comment'))).send_keys(data.message_for_driver)

        # Pedir manta y pañuelos
        wait.until(EC.element_to_be_clickable((By.ID, 'comfort'))).click()

        # Pedir 2 helados
        ice_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ice-cream')))
        ice_button.click()
        ice_button.click()  # dos veces

        # Confirmar pedido
        wait.until(EC.element_to_be_clickable((By.ID, 'order'))).click()

        # Esperar modal de conductor (opcional)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'driver-info')))

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
