# BQ Business Rules Generator

Generador automático de reglas de negocio desde BigQuery con clasificación de sensibilidad según DC-DG-03-02.

## Descripción

Este proyecto extrae metadatos de tablas BigQuery y genera documentación completa en Excel con:
- Descripción funcional de columnas
- Clasificación de sensibilidad (DC-DG-03-02 + Appendix A)
- Criticidad y justificación
- Ejemplos reales de datos
- Valores permitidos y formatos
- Tabla resumen por clasificación

## Estructura del Proyecto

```
bq_business_rules/
├── main.py                           # Script principal (interfaz CLI con menú)
├── bq_analyzer.py                   # Análisis de BQ + validación de permisos
├── excel_generator.py               # Generación de Excel con estilos Walmart
├── test_permisos.py                 # 🔍 Test de permisos BigQuery
├── requirements.txt                 # Dependencias Python
├── run.bat                          # Script de ejecución Windows
├── test_permisos.bat                # 🔍 Launcher del test de permisos
├── Reglas_Negocio_template.xlsx    # 📋 TEMPLATE BASE (formato estandarizado)
├── ACTUALIZACION_PROYECTOS.md      # 📘 Documentación de cambios v2.2
├── output/                          # Archivos Excel generados (git-ignored)
└── README.md                        # Este archivo
```

## 📋 Template Base

El sistema utiliza **`Reglas_Negocio_template.xlsx`** como plantilla estandarizada para todos los archivos generados. Este template:

✅ Mantiene formato corporativo consistente  
✅ Incluye estilos, colores y configuración de Walmart  
✅ Garantiza compatibilidad con herramientas de auditoría  
✅ Permite personalización previa (logos, headers, footers)  

**Ubicación fija**: `C:\Users\vn59q13\OneDrive - Walmart Inc\Documentos\bq_business_rules\Reglas_Negocio_template.xlsx`

Cada ejecución:
1. Copia el template
2. Renombra con timestamp (`Reglas_Negocio_{tabla}_{timestamp}.xlsx`)
3. Puebla con datos de BigQuery
4. Mantiene todo el formato del template original

## Requisitos

- Python 3.13+
- Google Cloud SDK configurado
- Acceso a BigQuery con permisos:
  - `bigquery.jobs.create` (validado automáticamente)
  - `bigquery.datasets.get`
  - `bigquery.tables.get`
  - `bigquery.tables.getData`
- Credenciales autenticadas (`gcloud auth login`)
- Walmart VPN o Eagle WiFi (requerido para acceso a GCP)

## Instalación

```bash
# Instalar dependencias
uv pip install -r requirements.txt
```

## Uso

### Ejecución Normal

```bash
# Opción 1: Doble clic en Windows
run.bat

# Opción 2: Línea de comandos
python main.py
```

El script presenta un **menú interactivo** que solicita:

1. **Proyecto GCP** (menú de selección):
   - [1] wmt-intl-cons-local-k1-prod
   - [2] wmt-intl-cons-mc-k1-prod
   - [3] wmt-k1-dwh-data-prod
   - [4] wmt-edw-prod
   - [5] Otro (digitar manualmente)

2. **Validación automática** de permisos `bigquery.jobs.create`

3. **Dataset** en el proyecto seleccionado

4. **Billing Project** (opcional, si difiere del proyecto de datos)

5. **Tabla(s)** a analizar

### Test de Permisos

Para verificar permisos sin ejecutar el análisis completo:

```bash
# Opción 1: Doble clic
test_permisos.bat

# Opción 2: Línea de comandos
python test_permisos.py
```

Esta herramienta:
- ✅ Valida permisos en todos los proyectos predefinidos
- ✅ Permite probar proyectos personalizados
- ✅ Muestra resumen de accesos y errores
- ✅ Útil para troubleshooting de permisos

## Output

El Excel generado contiene 3 pestañas:

### 1. Reglas de Negocio
Tabla detallada con 13 columnas por campo:
- Columna, Descripción, Tabla Origen
- Tipo, Formato, Valores Permitidos
- Valor Nulo Permitido, Criticidad
- Justificación, Ejemplo Real
- Clasificación de Sensibilidad
- Referencia Standard DC-DG-03-02
- Observación detallada

### 2. Resumen por Clasificación
Tabla agrupada por nivel de sensibilidad:
- [HIGH] Highly Sensitive (PII, PHI, Financiero)
- [MED] Sensitive (Personal, Transaccional)
- [LOW] Non Sensitive (Metadatos, Tecnico)

Con estadísticas y referencias específicas al DC-DG-03-02 Appendix A.

### 3. Metadatos
Información técnica del análisis (proyecto, dataset, tabla, fecha).

## Clasificación de Sensibilidad

Basada en **Global Data Sensitivity Classification Standard DC-DG-03-02**:

- **Highly Sensitive**: SSN, tarjetas de pago, datos bancarios, salarios, PHI, credenciales, biométricos
- **Sensitive**: Email, teléfono, direcciones, nombres, IDs de clientes/transacciones, IPs
- **Non Sensitive**: Timestamps técnicos, códigos de estado, particiones, códigos geográficos

Más de 200+ patrones de detección automática.

## Compliance

- GDPR
- CCPA
- PCI-DSS
- HIPAA
- DC-DG-03-02 (Walmart Standard)

## Autor

**Ariel Rodriguez** - Walmart Tech
- Email: ariel.rodriguez1@walmart.com

## Changelog

### v2.2.0 (2026-04-21)
- **[NUEVO]** Menú de selección de proyectos predefinidos
- **[NUEVO]** Validación automática de permisos BigQuery
- **[NUEVO]** Script de test de permisos (`test_permisos.py`)
- **[NUEVO]** Documentación detallada en `ACTUALIZACION_PROYECTOS.md`
- Manejo mejorado de errores de acceso y permisos
- Validación de billing project
- UX mejorada con mensajes en español

### v2.1.0 (2026-04-20)
- **[NUEVO]** Sistema basado en template estandarizado
- **[NUEVO]** Uso de `Reglas_Negocio_template.xlsx` como base
- Formato corporativo 100% consistente entre ejecuciones
- Mejora en mantenibilidad y personalización

### v2.0.0 (2026-04-20)
- Clasificacion automatica DC-DG-03-02 + Appendix A
- Tabla resumen por clasificacion
- Referencias especificas al Standard
- Observaciones detalladas
- Ejemplos reales de datos
- Descripcion funcional auto-generada

### v1.0.0 (2026-04-19)
- Analisis basico de INFORMATION_SCHEMA
- Generacion de Excel con estilos Walmart
- Profiling de columnas

## License

Walmart Proprietary - Internal Use Only
