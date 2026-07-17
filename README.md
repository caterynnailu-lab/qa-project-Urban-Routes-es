# Urban Routes — Automatización de pruebas (Sprint 9)

Suite de pruebas automatizadas con **Selenium + Page Object Model (POM)** para el flujo completo de pedido de taxi en Urban Routes.

## Estructura del proyecto

```
qa-project-Urban-Routes-es/
├── data.py                 # Datos de prueba (direcciones, teléfono, tarjeta, mensaje, URL)
├── main.py                 # Función retrieve_phone_code() (provista, no modificar)
├── urban_routes_page.py    # Page Object: UrbanRoutesPage (locators + acciones + getters)
├── test_urban_routes.py    # Clase TestUrbanRoutes: 9 pruebas independientes
└── README.md
```

## Arquitectura de las pruebas

Cada prueba es **independiente**: no depende del estado dejado por otra prueba. Esto se logra con:

- `setup_class` / `teardown_class`: abren y cierran el navegador **una sola vez** para toda la clase (por eficiencia, no se abre un navegador por prueba).
- `setup_method`: recarga la página de la app **antes de cada prueba**, garantizando un estado limpio. (Excepción documentada para `test_wait_for_driver_info`, ver más abajo).
- Métodos de precondición privados (prefijo `_do_*`, no son pruebas): cada uno reconstruye desde cero los pasos necesarios para llegar al punto que la prueba necesita validar.

```
_do_set_route()          → rellena origen y destino
_do_select_comfort()     → _do_set_route() + abre tarifas + selecciona Comfort
_do_set_phone()          → _do_select_comfort() + rellena teléfono + confirma código SMS
_do_add_credit_card()    → _do_set_phone() + agrega tarjeta de crédito
_do_submit_order()       → _do_add_credit_card() + pide el taxi
```

Es normal y esperado que estos métodos se repitan entre pruebas — son precondiciones, no lógica de negocio duplicada. Cada prueba usa la cadena de precondición mínima necesaria para llegar a su propio punto de validación.

## Pruebas y qué valida cada una

| # | Prueba | Qué valida |
|---|---|---|
| 1 | `test_set_route` | El campo "Desde" y "Hasta" contienen exactamente las direcciones configuradas (`get_from_value`, `get_to_value`). |
| 2 | `test_select_comfort_tariff` | La tarifa Comfort queda visualmente seleccionada tras hacer clic (`is_comfort_selected`). |
| 3 | `test_set_phone` | El campo de teléfono contiene el número ingresado **antes** de avanzar de pantalla (`get_phone_value`), y el flujo de confirmación por SMS se completa sin error. |
| 4 | `test_add_credit_card` | El método de pago queda mostrado como "Tarjeta" en la pantalla principal tras agregar la tarjeta (`get_payment_method_text`). |
| 5 | `test_set_message_for_driver` | El campo de mensaje para el conductor contiene el texto ingresado (`get_message_value`). |
| 6 | `test_blanket_and_tissues` | El switch de "Manta y pañuelos" queda realmente marcado como activado — se valida el estado del `<input type="checkbox">` (`is_blanket_checked` → `is_selected()`), no solo su visibilidad. |
| 7 | `test_two_ice_creams` | El contador específico de "Helado" muestra "2" tras dos clics en el botón `+` (`get_ice_cream_count`), usando un localizador que distingue el contador de Helado de los de Chocolate y Fresa (que comparten la misma clase CSS). |
| 8 | `test_search_taxi` | Al pedir el taxi, aparece el modal de búsqueda de conductor (`is_search_modal_visible`). |
| 9 | `test_wait_for_driver_info` *(opcional)* | Tras la búsqueda, el modal muestra la información real del conductor asignado ("El conductor llegará en X min.") y el número del vehículo. Ver nota abajo. |

## Localizadores específicos (evitando ambigüedad)

Varios localizadores se hicieron deliberadamente específicos porque la página tiene múltiples elementos con clases o texto compartido, lo que podía hacer que Selenium seleccionara el elemento incorrecto:

- **Tarifa Comfort**: en vez de buscar cualquier elemento que contenga el texto "Comfort" (`//*[contains(text(),'Comfort')]`), se ancla al contenedor de la tarjeta específica (`//div[contains(@class,'tcard') and .//div[text()='Comfort']]`).
- **Manta y pañuelos**: como la app tiene más de un switch (también existe "Cortina acústica" con la misma estructura HTML), el localizador se relaciona explícitamente con la etiqueta de texto "Manta y pañuelos" en vez de buscar cualquier `.switch` en la página.
- **Contador de helados**: como "Helado", "Chocolate" y "Fresa" comparten la misma clase `counter-value`, el localizador ancla específicamente al contador que sigue al texto "Helado".
- **Botón de guardar tarjeta**: se identificó mediante inspección directa del DOM (no por suposición) como `//button[@type='submit' and text()='Agregar']`.

## Nota sobre `test_wait_for_driver_info` (prueba opcional)

Durante el desarrollo se observó que la app de práctica **cancela el pedido de forma intermitente** después de "Pedir un taxi": el modal de búsqueda aparece correctamente (`class="order shown"`) y, en algunos casos, se cierra solo unos segundos después (`class="order"`, sin la clase `shown`), regresando a la pantalla principal sin ningún mensaje de error visible.

Se investigó exhaustivamente para descartar causas atribuibles al código de automatización:
- **Timing insuficiente**: se probó con esperas de hasta 60s — el cierre ocurre en ~2s, no por timeout.
- **Pérdida de sesión por reload de página**: se probó evitando el reload de `setup_method` específicamente para esta prueba — el comportamiento persistió.
- **Estado inconsistente del botón de envío**: se confirmó que el botón vuelve exactamente a su texto original ("Pedir un taxi"), no queda en un estado intermedio que pudiera causar un reintento incorrecto.

No se identificó una causa atribuible al código de la prueba. Se implementó un mecanismo de **reintento automático** (`wait_for_driver_info(max_retries=5)`) como mitigación: si el pedido se cancela, la prueba vuelve a solicitarlo hasta 5 veces antes de fallar con un mensaje explícito indicando el comportamiento observado.

## Requisitos

```bash
pip install selenium pytest pytest-order
```

## Ejecución

```bash
# Suite completa
pytest test_urban_routes.py -v

# Una prueba específica
pytest test_urban_routes.py::TestUrbanRoutes::test_add_credit_card -v
```

**Tiempo aproximado de ejecución:** ~2:20 min para la suite completa (cada prueba reconstruye sus propias precondiciones, incluyendo esperas reales de SMS y confirmaciones de la app).