import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
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
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    # Botón principal para solicitar o abrir el menú de tarifas
    order_taxi_button = (By.XPATH, "//button[contains(@class, 'button round')]")

    # Tarifa Comfort (puedes buscarla por texto o clase específica)
    comfort_tariff_button = (By.XPATH, "//div[contains(text(), 'Comfort')]")

    # Campo y botones para el número de teléfono
    phone_field_trigger = (By.CLASS_NAME, "np-text")  # El elemento que abre el modal de teléfono
    phone_input = (By.ID, "phone")
    phone_next_button = (By.XPATH, "//button[text()='Siguiente']")
    phone_code_input = (By.ID, "code")
    phone_confirm_button = (By.XPATH, "//button[text()='Confirmar']")
    # Métodos de pago
    payment_method_button = (By.CLASS_NAME, "pp-text")
    add_card_button = (By.XPATH, "//div[text()='Agregar tarjeta']")
    card_number_field = (By.ID, "number")
    card_code_field = (By.XPATH, "//input[@id='code' and @name='code']")  # Campo CVV de tarjeta
    card_blank_space = (By.CLASS_NAME, "payment-inst")
    card_save_button = (By.XPATH, "//button[text()='Agregar']")
    close_payment_modal = (By.XPATH,
                           "//div[contains(@class, 'payment-picker')]//button[contains(@class, 'close-button')]")

    # Comentario y extras
    comment_field = (By.ID, "comment")
    blanket_switch = (By.XPATH, "//span[@class='slider round']")  # Switch para manta y pañuelos
    ice_cream_plus = (By.XPATH, "//div[text()='Helado']/..//div[@class='counter-plus']")
    submit_order_button = (By.CLASS_NAME, "smart-button-main")
    search_car_modal = (By.CLASS_NAME, "order-body")

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def click_order_taxi(self):
        self.driver.find_element(*self.order_taxi_button).click()

    def select_comfort_tariff(self):
        # Es recomendable usar WebDriverWait aquí para esperar a que el menú de tarifas aparezca
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.comfort_tariff_button)
        ).click()

    def set_phone(self, phone_number):
        # Abre el modal del teléfono
        self.driver.find_element(*self.phone_field_trigger).click()

        # Espera que aparezca el campo y escribe el número
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.phone_input)
        ).send_keys(phone_number)

        # Haz clic en Siguiente
        self.driver.find_element(*self.phone_next_button).click()

        # Obtiene el código usando la función integrada del proyecto
        code = retrieve_phone_code(self.driver)

        # Introduce el código de confirmación recibido y confirma
        self.driver.find_element(*self.phone_code_input).send_keys(code)
        self.driver.find_element(*self.phone_confirm_button).click()

    def add_credit_card(self, card_number, card_code):
        self.driver.find_element(*self.payment_method_button).click()
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.add_card_button)
        ).click()
        self.driver.find_element(*self.card_number_field).send_keys(card_number)

        card_code_input = self.driver.find_element(*self.card_code_field)
        card_code_input.send_keys(card_code)
        card_code_input.send_keys(Keys.TAB)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.card_save_button)
        ).click()
        self.driver.find_element(*self.close_payment_modal).click()

    def set_comment(self, comment):
        self.driver.find_element(*self.comment_field).send_keys(comment)

    def toggle_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_switch).click()

    def add_ice_cream(self):
        self.driver.find_element(*self.ice_cream_plus).click()

    def submit_order(self):
        self.driver.find_element(*self.submit_order_button).click()

    def get_search_modal_status(self):
        return WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.search_car_modal)
        ).is_displayed()


class TestUrbanRoutes:

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options
        import data

        # Configuración moderna para habilitar el registro de rendimiento (necesario para el código telefónico)
        chrome_options = Options()
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.driver.get(data.urban_routes_url)

    def test_urban_routes_full_flow(self):
        import data
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions

        routes_page = UrbanRoutesPage(self.driver)

        # Esperar explícitamente a que la página cargue el campo 'from'
        WebDriverWait(self.driver, 15).until(
            expected_conditions.visibility_of_element_located(routes_page.from_field)
        )

        # 1. Configurar direcciones
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)
        assert routes_page.get_from() == data.address_from
        assert routes_page.get_to() == data.address_to

    # 2. Seleccionar tarifa Comfort
        routes_page.click_order_taxi()
        routes_page.select_comfort_tariff()

    # 3. Rellenar teléfono
        routes_page.set_phone(data.phone_number)

    # 4. Agregar tarjeta de crédito
        routes_page.add_credit_card(data.card_number, data.card_code)

    # 5. Escribir comentario para el conductor
        routes_page.set_comment(data.message_for_driver)

    # 6. Pedir manta y pañuelos
        routes_page.toggle_blanket_and_tissues()

    # 7. Pedir 2 helados (hace clic dos veces)
        routes_page.add_ice_cream()
        routes_page.add_ice_cream()

    # 8. Buscar un taxi
        routes_page.submit_order()

    # 9. Verificar que aparece el modal de búsqueda de automóvil
        assert routes_page.get_search_modal_status() == True

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()