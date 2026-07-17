import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import data
from main import retrieve_phone_code
from urban_routes_page import UrbanRoutesPage


class TestUrbanRoutes:
    driver = None
    routes_page = None

    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def teardown_class(cls):
        if cls.driver:
            cls.driver.quit()

    def setup_method(self, method):
        # Excepción documentada: test_wait_for_driver_info depende de una sesión
        # continua del navegador. La app parece usar una conexión en segundo plano
        # para simular la asignación del conductor, que no se reestablece a tiempo
        # tras un reload completo de página. Por eso, para ESTE test específico,
        # no recargamos y en su lugar reconstruimos el flujo sobre la sesión existente.
        if method.__name__ != 'test_wait_for_driver_info':
            self.driver.get(data.urban_routes_url)
        self.routes_page = UrbanRoutesPage(self.driver)

    # --- Métodos de precondición (privados, NO son tests) ---

    def _do_set_route(self):
        self.routes_page.set_route(data.address_from, data.address_to)

    def _do_select_comfort(self):
        self._do_set_route()
        self.routes_page.click_order_taxi()
        self.routes_page.select_comfort_tariff()

    def _do_set_phone(self):
        self._do_select_comfort()
        self.routes_page.set_phone(data.phone_number)
        time.sleep(4)  # margen para que el log del SMS se registre
        sms_code = retrieve_phone_code(self.driver)
        self.routes_page.confirm_phone_code(sms_code)

    def _do_add_credit_card(self):
        self._do_set_phone()
        self.routes_page.add_credit_card(data.card_number, data.card_code)

    def _do_submit_order(self):
        self._do_add_credit_card()
        time.sleep(2)  # margen antes de enviar el pedido
        self.routes_page.click_submit_order_button()

    # --- Tests independientes ---

    def test_set_route(self):
        self._do_set_route()
        assert self.routes_page.get_from_value() == data.address_from
        assert self.routes_page.get_to_value() == data.address_to

    def test_select_comfort_tariff(self):
        self._do_select_comfort()
        assert self.routes_page.is_comfort_selected() == True

    def test_set_phone(self):
        self._do_select_comfort()
        self.routes_page.fill_phone(data.phone_number)
        assert self.routes_page.get_phone_value() == data.phone_number
        self.routes_page.click_phone_next()
        time.sleep(4)
        sms_code = retrieve_phone_code(self.driver)
        self.routes_page.confirm_phone_code(sms_code)

    def test_add_credit_card(self):
        self._do_add_credit_card()
        assert 'Tarjeta' in self.routes_page.get_payment_method_text()

    def test_set_message_for_driver(self):
        self._do_add_credit_card()
        self.routes_page.set_message(data.message_for_driver)
        assert self.routes_page.get_message_value() == data.message_for_driver

    def test_blanket_and_tissues(self):
        self._do_add_credit_card()
        self.routes_page.toggle_blanket_and_tissues()
        assert self.routes_page.is_blanket_checked() == True

    def test_two_ice_creams(self):
        self._do_add_credit_card()
        self.routes_page.add_ice_creams(2)
        assert self.routes_page.get_ice_cream_count() == "2"

    def test_search_taxi(self):
        self._do_add_credit_card()
        self.routes_page.click_submit_order_button()
        assert self.routes_page.is_search_modal_visible() == True

    def test_wait_for_driver_info(self):
        self.driver.get(data.urban_routes_url)
        time.sleep(2)
        self._do_submit_order()
        self.routes_page.wait_for_driver_info()
        arrival_text = self.routes_page.get_driver_arrival_text()
        car_number = self.routes_page.get_car_number()
        assert 'lleg' in arrival_text.lower()
        assert car_number != ''
