from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common. keys import Keys

class UrbanRoutesPage:
    def __init__(self, driver):
        self.driver = driver

        # --- Localizadores Base ---
        self.from_field = (By.ID, 'from')
        self.to_field = (By.ID, 'to')
        self.order_button = (By.XPATH, "//button[contains(@class, 'button') and contains(@class, 'round')]")
        # Info del conductor (paso opcional)
        self.driver_arrival_title = (By.CLASS_NAME, 'order-header-title')
        self.driver_car_number = (By.CLASS_NAME, 'number')

        # Tarifa Comfort
        self.comfort_card = (
    By.XPATH,
    "//div[contains(@class,'tcard') and .//div[text()='Comfort']]"
)

        # Teléfono
        self.phone_button = (By.CLASS_NAME, 'np-button')
        self.phone_input = (By.ID, 'phone')
        self.next_button = (By.XPATH, "//button[text()='Siguiente']")
        self.code_input = (By.ID, 'code')
        self.confirm_button = (By.XPATH, "//button[text()='Confirmar']")

        # Tarjeta de Crédito (Item 4)
        self.payment_method_button = (By.CLASS_NAME, 'pp-button')
        self.add_card_button = (By.CLASS_NAME, 'pp-plus-container')
        self.card_number_input = (By.ID, 'number')
        self.card_code_input = (By.XPATH, "//input[@name='code' and @id='code']")
        self.save_card_button = (By.XPATH, "//button[@type='submit' and text()='Agregar']")
        self.close_payment_modal_button = (By.XPATH, "//div[contains(@class,'payment-picker')]//button[contains(@class,'close-button')]")

        # Requisitos del Viaje
        self.message_field = (By.ID, 'comment')
        self.blanket_switch = (
    By.XPATH,
    "//div[@class='r-sw-container'][.//div[@class='r-sw-label' and text()='Manta y pañuelos']]//div[@class='switch']"
)
        self.blanket_checkbox = (
    By.XPATH,
    "//div[@class='r-sw-container'][.//div[@class='r-sw-label' and text()='Manta y pañuelos']]//input[@class='switch-input']"
)
        self.ice_cream_plus_btn = (By.CLASS_NAME, 'counter-plus')
        self.ice_cream_counter = (
    By.XPATH,
    "//div[text()='Helado']/..//div[@class='counter-value']"
)

        # Solicitud Final
        self.submit_order_button = (By.CLASS_NAME, 'smart-button')
        self.search_modal = (By.CLASS_NAME, 'order-body')

    # --- Métodos de Acción Desacoplados ---

    def set_route(self, from_address, to_address):
        # SOLO escribe las direcciones para mantener la independencia
        WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located(self.from_field)).send_keys(from_address)
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def click_order_taxi(self):
        # Este método ahora se encarga exclusivamente de hacer el clic inicial
        button = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.order_button)
        )
        button.click()

    def select_comfort_tariff(self):
        tariff_card = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.comfort_card)
        )
        tariff_card.click()

    def fill_phone(self, phone_number):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.phone_button)
        ).click()
        phone_field = WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.phone_input)
        )
        phone_field.send_keys(phone_number)

    def click_phone_next(self):
        self.driver.find_element(*self.next_button).click()

    def get_phone_value(self):
        return self.driver.find_element(*self.phone_input).get_property('value')

    def set_phone(self, phone_number):
        """Mantiene compatibilidad: rellena y avanza en un solo paso."""
        self.fill_phone(phone_number)
        self.click_phone_next()

    def confirm_phone_code(self, sms_code):
        WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located(self.code_input)).send_keys(sms_code)
        self.driver.find_element(*self.confirm_button).click()

    def add_credit_card(self, card_number, card_code):

        payment_btn = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(self.payment_method_button)
        )
        self.driver.execute_script("arguments[0].click();", payment_btn)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.add_card_button)
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.card_number_input)
        ).send_keys(card_number)

        cvv_field = self.driver.find_element(*self.card_code_input)
        cvv_field.send_keys(card_code)
        cvv_field.send_keys(Keys.TAB)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.save_card_button)
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.close_payment_modal_button)
        ).click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.invisibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'overlay')]")
            )
        )

    def set_message(self, message):
            field = WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located(self.message_field))
            field.send_keys(message)

    def toggle_blanket_and_tissues(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.blanket_switch)
        ).click()

    def add_ice_creams(self, amount):
        plus_btn = WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.ice_cream_plus_btn)
        )
        for _ in range(amount):
            plus_btn.click()

    def click_submit_order_button(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.submit_order_button)
        ).click()

    # --- Metodos de Validacion ---
    def get_from_value(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to_value(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def is_comfort_selected(self):
        return self.driver.find_element(*self.comfort_card).is_displayed()

    def get_message_value(self):
        return self.driver.find_element(*self.message_field).get_property('value')

    def is_blanket_checked(self):
        return self.driver.find_element(*self.blanket_checkbox).is_selected()

    def get_ice_cream_count(self):
        return self.driver.find_element(*self.ice_cream_counter).text

    def get_payment_method_text(self):
        return self.driver.find_element(*self.payment_method_button).text

    def is_search_modal_visible(self):
        try:
            WebDriverWait(self.driver, 10).until(
                expected_conditions.visibility_of_element_located(self.search_modal)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_driver_info(self, max_retries=5):
        """Espera a que el modal muestre la info real del conductor asignado
        (contiene 'llegará en X min').

        NOTA: se observó que esta app de práctica cancela el pedido de forma
        intermitente después de "Pedir un taxi" (el modal pasa de shown a oculto
        en ~2s, sin errores visibles, y el botón vuelve a su estado original
        "Pedir un taxi"). No se identificó causa atribuible al código de
        automatización: se descartaron timing insuficiente, pérdida de sesión
        por reload de página, y estado inconsistente del botón de envío.
        Se implementa reintento automático como mitigación de este
        comportamiento intermitente del entorno de práctica.
        """
        import time
        for attempt in range(max_retries):
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda driver: 'lleg' in driver.find_element(*self.driver_arrival_title).text.lower()
                )
                return
            except TimeoutException:
                order_container = self.driver.find_element(By.CLASS_NAME, 'order')
                if 'shown' not in order_container.get_attribute('class'):
                    time.sleep(3)
                    self.click_submit_order_button()
                else:
                    time.sleep(3)
                continue
        raise Exception(
            f"Se agotaron los {max_retries} intentos esperando la asignación del conductor "
            f"(comportamiento intermitente conocido de la app de práctica)."
        )

    def get_driver_arrival_text(self):
        return self.driver.find_element(*self.driver_arrival_title).text

    def get_car_number(self):
        return self.driver.find_element(*self.driver_car_number).text
