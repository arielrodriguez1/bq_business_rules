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
├── main.py                           # Script principal (interfaz CLI)
├── bq_analyzer.py                   # Análisis de BigQuery INFORMATION_SCHEMA
├── excel_generator.py               # Generación de Excel con estilos Walmart
├── requirements.txt                 # Dependencias Python
├── run.bat                          # Script de ejecución Windows
├── Reglas_Negocio_template.xlsx    # 📋 TEMPLATE BASE (formato estandarizado)
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
- Acceso a BigQuery
- Credenciales autenticadas (`gcloud auth login`)

## Instalación

```bash
# Instalar dependencias
uv pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

El script solicitará:
1. Proyecto GCP
2. Dataset
3. Tabla(s) a analizar

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
