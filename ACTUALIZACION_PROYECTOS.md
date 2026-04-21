# 🚀 Actualización: Menú de Proyectos y Validación de Permisos

## ✅ Cambios Implementados

### 1. **Menú de Selección de Proyectos**
Ya no necesitas escribir manualmente el proyecto cada vez. Ahora verás un menú con las opciones:

```
  Selecciona un proyecto GCP:

    [1] wmt-intl-cons-local-k1-prod
    [2] wmt-intl-cons-mc-k1-prod
    [3] wmt-k1-dwh-data-prod
    [4] wmt-edw-prod
    [5] Otro (digitar manualmente)

  Opción:
```

**Ventajas:**
- ⚡ Más rápido: solo digita el número
- 🎯 Sin errores de tipeo
- 🔄 Opción "Otro" para proyectos adicionales

---

### 2. **Validación Automática de Permisos BigQuery**

Antes de ejecutar cualquier query, el sistema valida que tengas el permiso `bigquery.jobs.create` en el proyecto.

**Qué hace:**
- ✅ Ejecuta una query de prueba simple: `SELECT 1`
- 🔍 Detecta errores 403 (sin permisos) o 404 (proyecto no existe)
- 🔄 Si no tienes permisos, te permite seleccionar otro proyecto

**Mensajes que verás:**

```bash
# ✅ Si tienes permisos:
  [i] Validando permisos de BigQuery en wmt-edw-prod...
  [OK] Permisos validados correctamente.

# ❌ Si NO tienes permisos:
  [i] Validando permisos de BigQuery en wmt-edw-prod...
  [!] ERROR: No tienes permisos 'bigquery.jobs.create' en el proyecto wmt-edw-prod.
      Solicita acceso o selecciona otro proyecto.
```

---

### 3. **Validación en Billing Project (si usas uno diferente)**

Si especificas un **Billing Project** diferente al proyecto de datos, también se validan los permisos ahí.

```bash
  [?] Necesitas usar un proyecto diferente para ejecutar queries (billing)?
      (Presiona ENTER para usar el mismo proyecto: wmt-edw-prod)
  Billing Project: otro-proyecto-billing

  [i] Validando permisos en billing project otro-proyecto-billing...
  [OK] Permisos de billing validados.
```

Si no tienes permisos en el billing project, automáticamente usa el proyecto principal.

---

## 🎯 Cómo Usar

### **Ejecución Normal:**
1. Doble clic en `run.bat`
2. Selecciona el proyecto del menú (1-5)
3. Si el proyecto requiere permisos, recibirás un mensaje claro
4. Ingresa el dataset y tabla como siempre

### **Ejemplo de Sesión:**

```
  >> Configuracion de sesion

  Selecciona un proyecto GCP:

    [1] wmt-intl-cons-local-k1-prod
    [2] wmt-intl-cons-mc-k1-prod
    [3] wmt-k1-dwh-data-prod
    [4] wmt-edw-prod
    [5] Otro (digitar manualmente)

  Opción: 3

  [i] Validando permisos de BigQuery en wmt-k1-dwh-data-prod...
  [OK] Permisos validados correctamente.

  Dataset en GCP  (ej. mi_dataset): sales_data

  [?] Necesitas usar un proyecto diferente para ejecutar queries (billing)?
      (Presiona ENTER para usar el mismo proyecto: wmt-k1-dwh-data-prod)
  Billing Project: [ENTER]

  >> Nueva consulta  (proyecto: wmt-k1-dwh-data-prod | dataset: sales_data)

  Nombre de la tabla  (ej. mi_tabla): transactions
```

---

## 🔧 Archivos Modificados

### `main.py`
- ➕ Agregada función `_select_project()` con menú interactivo
- ➕ Agregada lista `WALMART_PROJECTS` con proyectos predefinidos
- 🔄 Actualizada función `_get_session_credentials()` con validación de permisos
- ✅ Validación recursiva si falla el permiso (te permite reintentar)

### `bq_analyzer.py`
- ➕ Agregada función `validate_bigquery_permissions(project_id)`
- ➕ Importado `google.api_core.exceptions` para manejo de errores
- 🔄 Actualizada función `analyze_table()` para validar permisos antes de queries
- ✅ Manejo de excepciones Forbidden (403) y NotFound (404)

---

## 🛡️ Seguridad y Permisos

### **Permiso Requerido:**
- `bigquery.jobs.create` en el proyecto GCP

### **Cómo Solicitarlo:**
Si recibes un error de permisos, contacta a:
1. **Tu manager** para autorización
2. **GCP Admin** para asignar el rol:
   - `roles/bigquery.user` (mínimo)
   - `roles/bigquery.jobUser` (recomendado)
   - `roles/bigquery.dataViewer` (para leer datos)

### **Mensaje de Error Típico:**
```
[!] ERROR: No tienes permisos 'bigquery.jobs.create' en el proyecto wmt-edw-prod.
    Solicita acceso o selecciona otro proyecto.
```

---

## 📝 Notas Adicionales

### **¿Por qué validar permisos?**
- 🚨 Evita errores crípticos de BigQuery a mitad del proceso
- ⏱️ Ahorra tiempo detectando problemas de acceso desde el inicio
- 📊 Mejora la experiencia del usuario con mensajes claros

### **¿Qué pasa si selecciono "Otro"?**
- Te pedirá que escribas el nombre del proyecto manualmente
- También validará permisos en ese proyecto
- Útil para proyectos nuevos o de prueba

### **¿Puedo agregar más proyectos al menú?**
Sí! Edita `main.py` y agrega proyectos a la lista `WALMART_PROJECTS`:

```python
WALMART_PROJECTS = [
    "wmt-intl-cons-local-k1-prod",
    "wmt-intl-cons-mc-k1-prod",
    "wmt-k1-dwh-data-prod",
    "wmt-edw-prod",
    "tu-nuevo-proyecto",  # ⬅️ Agrega aquí
]
```

---

## 🐞 Solución de Problemas

### **Error: "Proyecto no encontrado"**
- ✅ Verifica que el proyecto existe en GCP
- ✅ Confirma que tienes acceso al proyecto
- ✅ Revisa que estés conectado a Walmart VPN/Eagle WiFi

### **Error: "No tienes permisos"**
- ✅ Solicita el rol `bigquery.user` o `bigquery.jobUser`
- ✅ Verifica con: `gcloud projects get-iam-policy PROJECT_ID`
- ✅ Contacta al owner del proyecto para acceso

### **La validación es muy lenta**
- ⚠️ Normal si la conexión a GCP es lenta
- ✅ La query de validación es simple y rápida (SELECT 1)
- ✅ Timeout configurado a 5 segundos

---

## 📞 Soporte

Si encuentras algún problema o necesitas ayuda:
1. Revisa los logs de error en pantalla
2. Verifica tu conectividad a GCP (`gcloud auth list`)
3. Contacta al equipo de Data Engineering

---

**Versión:** 2.0  
**Fecha:** 2026-04-21  
**Autor:** Code Puppy 🐶  
**Commit:** `3253a41`
