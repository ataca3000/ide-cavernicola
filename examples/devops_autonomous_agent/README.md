# Caso de Uso Práctico: Agente Autónomo de Optimización de CI/CD e IDE

Este ejemplo demuestra **dónde y por qué implementar la arquitectura IDC (Inventor Driven Cognition)** en un caso del mundo real: **un agente optimizador de compilación, empaquetado y despliegue continuo**.

---

## 🛑 El Problema con los Agentes Tradicionales
Cuando un agente convencional (ej. basado únicamente en llamadas a LLMs) intenta resolver problemas de build o rendimiento:
1. **Amnesia:** En cada ejecución empieza de cero, repitiendo diagnósticos lentos.
2. **Repetición de errores:** Si hace 2 días descubrió que ejecutar `upgrade_everything` rompía las dependencias, hoy vuelve a intentarlo porque no tiene memoria causal ni papelera de descarte.
3. **Despilfarro de recursos:** Hace llamadas masivas y costosas a APIs para decisiones mecánicas obvias.
4. **Alucinación de soluciones:** Supone que una solución funcionará sin contrastar su modelo mental contra la realidad física.

---

## ⚡ La Solución con IDC (Inventor Driven Cognition)

En este ejemplo ([`agent.py`](agent.py)), el agente funciona como un auténtico ingeniero/inventor pragmático:

```mermaid
sequenceDiagram
    participant User as Ingeniero / Pipeline
    participant Decision as DecisionEngine (IDC)
    participant Trash as Causal Trash (memory/trash/)
    participant Sim as SimulationEngine
    participant Sandbox as Realidad / Sandbox Físico
    participant Memory as Causal Memory (memory/causal/)

    User->>Decision: Propuesta de estrategia: "upgrade_everything"
    Decision->>Trash: ¿Existe en papelera de rechazos?
    Trash-->>Decision: Sí (falló 17 veces: "introduced_instability")
    Decision-->>User: RECHAZADO de inmediato (Cero gasto de energía)

    User->>Decision: Propuesta: "mount_persistent_build_cache"
    Decision->>Sim: Simular costo vs riesgo
    Sim-->>Decision: Éxito predicho: 90% | Riesgo: BAJO
    Decision->>Sandbox: Ejecutar prueba real (-4 unidades de energía)
    Sandbox-->>Decision: Verificado con la realidad: Éxito (+68.5% velocidad)
    Decision->>Memory: Guardar regla causal A -> B (confianza: 0.95)
```

---

## 🚀 Cómo Ejecutar el Ejemplo

Desde la raíz del proyecto:

```bash
uv run python examples/devops_autonomous_agent/agent.py
```

### Comportamiento observado:

1. **Caso 1 (Protección contra fallos conocidos):**  
   El agente evalúa `upgrade_everything`.  
   *Resultado:* El `DecisionEngine` detecta el patrón en `memory/trash/rejected.json` y **aborta la acción al instante sin quemar energía ni romper el build**.
2. **Caso 2 (Exploración, simulación y consolidación causal):**  
   El agente evalúa `mount_persistent_build_cache`.  
   *Resultado:* Pasa el filtro de propósito, la simulación proyecta bajo riesgo, se ejecuta en la realidad consumiendo 4 unidades de energía, comprueba la ganancia del 68.5% y **escribe una nueva regla causal en `memory/causal/`**. La próxima vez, la aplicará por reflejo directo.
