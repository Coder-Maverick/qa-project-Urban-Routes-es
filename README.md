# Urban Routes Automation Tests

Este proyecto contiene pruebas automatizadas para verificar la funcionalidad del proceso de solicitud de taxi en la plataforma Urban Routes.

## 🧪 Descripción

Las pruebas automatizadas simulan el flujo completo de un usuario que:

- Configura la dirección de origen y destino.
- Selecciona la tarifa "Comfort".
- Introduce un número de teléfono y un código de confirmación.
- Agrega una tarjeta de crédito.
- Escribe un mensaje para el conductor.
- Solicita una manta, pañuelos y dos helados.
- Realiza el pedido del taxi.
- (Opcional) Espera a que aparezca la información del conductor.

## 🛠️ Tecnologías y técnicas utilizadas

- Lenguaje: Python 3
- Selenium WebDriver
- Pytest (opcional)
- Patrón Page Object Model (POM)
- Extracción de logs para interceptar el código de confirmación
- Esperas explícitas para sincronización dinámica

## ▶️ Cómo ejecutar las pruebas

1. Instala las dependencias necesarias:
install pytest
pytest main.py

