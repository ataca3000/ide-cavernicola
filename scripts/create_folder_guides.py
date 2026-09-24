"""
Script para generar archivos README.md guía en todas las subcarpetas modulares de IDC Cavernícola.
Autor: Luis Felipe Durán Salinas / Brecha Soluciones DS
"""

import os

folders_info = {
    # RULES
    "rules/deprecated": {
        "title": "Reglas Obsoletas (Deprecated Rules)",
        "coloca": "Coloca aquí las reglas que fueron útiles en versiones previas pero que han sido reemplazadas por una morfología, técnica o axioma superior.",
        "formato": ".md o .json con el ID de la regla previa y el motivo por el cual quedó superada."
    },
    "rules/experimental": {
        "title": "Reglas Experimentales (Experimental Rules)",
        "coloca": "Coloca aquí las nuevas reglas o restricciones de diseño que se encuentran en fase de prueba activa en taller o software y aún no completan las 8-12 horas continuas.",
        "formato": ".md o .json detallando la hipótesis, condiciones de prueba y métricas de resistencia."
    },
    "rules/proposed": {
        "title": "Reglas Propuestas (Proposed Rules)",
        "coloca": "Coloca aquí propuestas de nuevas reglas planteadas por el usuario o sugeridas por la IA ante situaciones recurrentes no cubiertas.",
        "formato": ".md con la descripción de la regla, el axioma relacionado y el problema que busca resolver."
    },
    "rules/rejected": {
        "title": "Reglas Rechazadas (Rejected Rules)",
        "coloca": "Coloca aquí ideas o propuestas que fueron evaluadas y descartadas formalmente por violar principios físicos, termodinámicos, mecánicos o de viabilidad de costo.",
        "formato": ".md detallando por qué falló o por qué fue rechazada para evitar reincidencias."
    },
    "rules/validated": {
        "title": "Reglas Validadas (Validated Rules)",
        "coloca": "Coloca aquí las reglas definitivas que superaron la prueba de fuego empírica (AXIOM_11) y se convierten en leyes de estricto cumplimiento para el agente.",
        "formato": ".md o .json estructurado listo para ser ingerido por el motor de inferencia."
    },

    # LEGACY
    "legacy/diaries": {
        "title": "Diarios de Taller e Histórico (Diaries)",
        "coloca": "Coloca aquí bitácoras cronológicas, notas de campo, fechas y transcripciones del proceso de construcción de prototipos o software.",
        "formato": "Archivos de texto o markdown con fecha (YYYY-MM-DD) y resumen del día de trabajo."
    },
    "legacy/discoveries": {
        "title": "Descubrimientos Empíricos (Discoveries)",
        "coloca": "Coloca aquí epifanías, hallazgos no convencionales y soluciones no documentadas en libros que resultaron altamente efectivas en la práctica.",
        "formato": ".md describiendo el problema, la solución inesperada y por qué funcionó."
    },
    "legacy/lessons": {
        "title": "Lecciones de Falla (Lessons Learned)",
        "coloca": "Coloca aquí las autopsias de roturas mecánicas, componentes quemados o bugs críticos (el registro riguroso de 'así no se hace').",
        "formato": ".md con análisis de causa raíz (torque, fatiga, calor, base débil) y acción correctiva aplicada."
    },
    "legacy/theories": {
        "title": "Teorías Hipotéticas (Theories)",
        "coloca": "Coloca aquí modelos teóricos y conceptuales que guiaron las primeras fases de desarrollo antes de tocar el metal o compilar.",
        "formato": ".md con ecuaciones, diagramas de bloques o derivaciones matemáticas."
    },

    # LEARNING
    "learning/confidence": {
        "title": "Métricas de Confianza (Confidence)",
        "coloca": "Coloca aquí registros cuantitativos de calibración del agente, curvas de certeza y benchmarks de razonamiento.",
        "formato": ".json con puntajes de precisión o evaluación cuantitativa estilo Karpathy."
    },
    "learning/penalties": {
        "title": "Penalizaciones por Alucinación (Penalties)",
        "coloca": "Coloca aquí registros de propuestas inviables o alucinaciones generadas para retroalimentar negativamente el grafo causal.",
        "formato": ".json o .md con el contexto del error y el peso de penalización asignado."
    },
    "learning/rewards": {
        "title": "Recompensas por Eficiencia (Rewards)",
        "coloca": "Coloca aquí soluciones donde el sistema ahorró energía, redujo costos aprovechando leyes gratuitas (gravedad, palancas) o pasó la prueba de fuego.",
        "formato": ".json o .md con la solución óptima y el valor de refuerzo positivo."
    },
    "learning/uncertainty": {
        "title": "Gestión de Incertidumbre (Uncertainty)",
        "coloca": "Coloca aquí umbrales de duda y protocolos donde el agente debe detenerse y activar AXIOM_06 (consulta obligatoria antes de ejecutar).",
        "formato": ".json o .md definiendo los límites de tolerancia y cuándo pedir confirmación al humano."
    },

    # PLUGINS
    "plugins/browser": {
        "title": "Plugin de Navegación Web (Browser)",
        "coloca": "Coloca aquí scripts y adaptadores para scraping técnico, consulta de manuales en línea y datasheets de componentes.",
        "formato": ".py con implementaciones de búsqueda técnica y extracción de especificaciones."
    },
    "plugins/filesystem": {
        "title": "Plugin de Sistema de Archivos (Filesystem)",
        "coloca": "Coloca aquí conectores para lectura y manipulación de archivos locales, logs de telemetría y exportación de diagramas.",
        "formato": ".py con métodos de acceso seguro y lectura estructurada."
    },
    "plugins/robotics": {
        "title": "Plugin de Robótica y Control (Robotics)",
        "coloca": "Coloca aquí controladores cinemáticos, comunicación con microcontroladores (Arduino, ESP32, Raspberry Pi) o protocolos PLC (Modbus).",
        "formato": ".py o scripts de control de actuadores, motores paso a paso y servomotores."
    },
    "plugins/search": {
        "title": "Plugin de Búsqueda Semántica (Search)",
        "coloca": "Coloca aquí motores de búsqueda sobre repositorios de patentes, tesis o papers de ciencia de materiales.",
        "formato": ".py integrando índices vectoriales o búsqueda léxica."
    },
    "plugins/sensors": {
        "title": "Plugin de Sensores y Telemetría (Sensors)",
        "coloca": "Coloca aquí lectores de termopares, sensores de vibración, acelerómetros, consumo de corriente y encoders.",
        "formato": ".py con funciones de adquisición de datos en tiempo real."
    },
    "plugins/speech": {
        "title": "Plugin de Voz y Audio (Speech)",
        "coloca": "Coloca aquí modelos de síntesis (TTS) y reconocimiento de voz (STT) para comando de manos libres en taller.",
        "formato": ".py conectando librerías de audio como Whisper o Piper."
    },
    "plugins/vision": {
        "title": "Plugin de Visión por Computadora (Vision)",
        "coloca": "Coloca aquí modelos de detección de objetos, reconocimiento de piezas mecánicas en chatarra o inspección visual de soldaduras.",
        "formato": ".py usando OpenCV, YOLO o modelos multimodales."
    },

    # TOOLBOX
    "toolbox/biology": {
        "title": "Caja de Herramientas: Biología y Biomímesis (Biology)",
        "coloca": "Coloca aquí principios biomecánicos, estructuras óseas naturales y patrones biológicos transferibles a la ingeniería estructural.",
        "formato": ".json o .md con razones de resistencia/peso de estructuras celulares y bio-diseños."
    },
    "toolbox/coding": {
        "title": "Caja de Herramientas: Algoritmos y Código (Coding)",
        "coloca": "Coloca aquí snippets de optimización matemática, algoritmos de grafos causales y patrones de arquitectura limpia.",
        "formato": ".py o .md con funciones reutilizables de alta eficiencia."
    },
    "toolbox/economics": {
        "title": "Caja de Herramientas: Economía de Escala (Economics)",
        "coloca": "Coloca aquí fórmulas para cálculo de retorno de inversión (ROI), costo de corte/maquinado por pieza y punto de equilibrio (AXIOM_12).",
        "formato": ".json o .py para evaluación de costo-beneficio de prototipos."
    },
    "toolbox/internet": {
        "title": "Caja de Herramientas: Protocolos de Red (Internet)",
        "coloca": "Coloca aquí plantillas de API REST, WebSockets y clientes MQTT para comunicación máquina a máquina (M2M).",
        "formato": ".py o .json con especificaciones de contratos de red."
    },
    "toolbox/probability": {
        "title": "Caja de Herramientas: Probabilidad y Fiabilidad (Probability)",
        "coloca": "Coloca aquí modelos estadísticos de tiempo medio entre fallas (MTBF), distribución de Weibull y análisis de riesgo.",
        "formato": ".json o .py para predecir cuándo una pieza alcanzará su límite de fatiga."
    },
    "toolbox/spacetime": {
        "title": "Caja de Herramientas: Cinemática Espacio-Tiempo (Spacetime)",
        "coloca": "Coloca aquí ecuaciones de trayectoria, cinemática directa e inversa, aceleración angular e inercia rotacional.",
        "formato": ".json o .py con matrices de transformación y cinemática."
    },

    # VERSIONS
    "versions/v0.1": {
        "title": "Versión Histórica v0.1 (Génesis)",
        "coloca": "Coloca aquí el snapshot de configuración, reglas iniciales y primeros esquemas de la versión 0.1 de Cavernícola.",
        "formato": "Archivos de configuración congelados para referencia histórica."
    },
    "versions/v0.2": {
        "title": "Versión Histórica v0.2",
        "coloca": "Coloca aquí el snapshot de los primeros grafos causales y reglas de amortización implementadas.",
        "formato": "Archivos de configuración congelados."
    },
    "versions/v0.3": {
        "title": "Versión Histórica v0.3",
        "coloca": "Coloca aquí el snapshot previo a la consolidación de los 14 axiomas universales.",
        "formato": "Archivos de configuración congelados."
    },
    "versions/v1": {
        "title": "Versión v1.0 (Matriz de Primeros Principios)",
        "coloca": "Coloca aquí el conjunto de reglas y pesos que definieron la primera versión formal de la arquitectura.",
        "formato": "JSON de la matriz cognitiva v1.0."
    },
    "versions/v2": {
        "title": "Versión v2.0 (IDC Universal Inventor Cognitive Set)",
        "coloca": "Coloca aquí los contratos, arnés y axiomas correspondientes a la versión actual 2.0.0.",
        "formato": "Configuraciones actuales v2.0."
    },
    "versions/v3": {
        "title": "Versión Futura v3.0 (Evolución Autónoma)",
        "coloca": "Coloca aquí las propuestas y especificaciones para la próxima generación del agente autónomo.",
        "formato": "Propuestas de arquitectura y modelos de próxima generación."
    }
}

def main():
    count = 0
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for folder, data in folders_info.items():
        target_dir = os.path.join(base_dir, folder.replace("/", os.sep))
        os.makedirs(target_dir, exist_ok=True)
        readme_path = os.path.join(target_dir, "README.md")
        content = f"""# {data['title']}

## 📌 ¿Qué colocar aquí si lo necesitas?
> {data['coloca']}

### 📋 Formato sugerido:
- **Estructura recomendada:** {data['formato']}
- **Autoría:** Mantener atribución a **Luis Felipe Durán Salinas / Brecha Soluciones DS**.
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        count += 1
        print(f"Creado: {folder}/README.md")

    print(f"\n¡Total creados exitosamente: {count} archivos README.md!")

if __name__ == "__main__":
    main()
