# 🦾 CHASIS — Puente Ciberfísico de IDC

El módulo **Chasis** es la capa de abstracción de hardware que conecta la **Corteza Cognitiva** (`core/`) con el mundo real, industrial y físico.

## 🔌 Componentes
1. **`arduino/`:** Interfaces serial / Firmata / SPI / I2C para lectura de corriente, señales analógicas y generación de pulsos en microcontroladores (Arduino, ESP32, Teensy).
2. **`plc/`:** Protocolos industriales deterministas (Modbus TCP/RTU, CAN Bus, OPC-UA) para interactuar con sistemas de automatización de planta.
3. **`sensors/`:** Adquisición continua de telemetría sensorial:
   - Visión computacional / Cámaras de profundidad (detección de obstáculos y realidad aumentada).
   - Sensores de efecto Hall (corriente continua en tiempo real).
   - Termopares y galgas extensométricas.

## ⚡ Conexión con la Corteza (`core/`)
Las lecturas de alta frecuencia del Chasis se envían a la Corteza a través de `ReactionPulse`. Si un sensor detecta un peligro inminente (ej. sobrecorriente en motor o colisión visual a 5cm), el `PulseReactionEngine` de la Corteza dispara una reacción refleja inmediata antes de que intervenga el razonamiento deliberado.
