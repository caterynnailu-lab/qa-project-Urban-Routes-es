# Proyecto de Automatización - Urban Routes (Sprint 9)

Este proyecto contiene las pruebas automatizadas de extremo a extremo para la aplicación web **Urban Routes**. El script valida de forma automatizada todo el flujo necesario para solicitar un servicio de taxi con requerimientos específicos.

## 🛠️ Tecnologías y Técnicas Utilizadas
* **Lenguaje:** Python 3
* **Framework de Pruebas:** Pytest
* **Herramienta de Automatización:** Selenium WebDriver (v4)
* **Patrón de Diseño:** Page Object Model (POM) para una mejor mantenibilidad y separación de la lógica.

## 🧪 Pruebas Cubiertas
El flujo automatizado ejecuta las siguientes acciones:
1. Configuración de las direcciones (Punto A y Punto B).
2. Selección de la tarifa "Comfort".
3. Registro y confirmación automatizada del número de teléfono.
4. Asociación de una tarjeta de crédito válida.
5. Inclusión de un mensaje personalizado para el conductor.
6. Solicitud de adicionales (manta y pañuelos).
7. Compra de complementos (2 helados).
8. Confirmación y envío del pedido del taxi para abrir el modal de búsqueda.

## 🚀 Cómo Ejecutar las Pruebas

1. Asegúrate de activar tu entorno virtual local:
   ```bash
   .venv\Scripts\activate
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install selenium pytest
   ```
3. Verifica que la URL del servidor activo esté configurada en el archivo `data.py`.
4. Ejecuta el suite de pruebas con el comando:
   ```bash
   pytest main.py
   ```
