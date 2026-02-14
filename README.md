# Supply Chain Monitoring Dashboard

## 📊 Executive Overview

Este proyecto representa la evolución de un sistema de reportes operativos automatizados hacia un dashboard de monitoreo orientado a gestión.

El objetivo no es solo generar datos, sino transformarlos en información clara para anticipar riesgos operativos y fortalecer la toma de decisiones en Supply Chain.

---

## 🎯 Objetivo de Gestión

En entornos productivos exigentes, los problemas no suelen originarse por falta de información, sino por falta de visibilidad oportuna.

Este dashboard permite:

- Monitorear nivel de inventarios
- Visualizar días de cobertura
- Estimar rotación mensual
- Identificar riesgos (Bajo / Medio / Alto)
- Detectar potenciales quiebres antes de impactar producción

La tecnología es el medio.  
La anticipación es el objetivo.

---

## ⚙️ Indicadores incluidos

### 1️⃣ Stock actual vs Stock mínimo
Permite visualizar desvíos críticos de inventario.

### 2️⃣ Días de cobertura
Mide cuánto tiempo puede sostenerse la operación con el stock actual.

### 3️⃣ Punto de reorden
Calculado como:
Reorder Point = Demanda diaria × Lead Time

### 4️⃣ Clasificación de riesgo
- ALTO: stock < mínimo o cobertura < lead time
- MEDIO: stock < punto de reorden
- BAJO: operación estable

### 5️⃣ Rotación estimada
Rotación mensual promedio para seguimiento de dinámica de inventarios.

---

## 📂 Estructura del Proyecto

