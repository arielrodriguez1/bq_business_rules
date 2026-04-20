"""
bq_analyzer.py
--------------
Módulo de análisis de BigQuery.
Consulta el INFORMATION_SCHEMA y realiza profiling de cada columna
para extraer metadatos de reglas de negocio.
"""

from google.cloud import bigquery
import pandas as pd
import warnings

# Suprimir el warning de credenciales de Google Cloud SDK
warnings.filterwarnings('ignore', message='Your application has authenticated using end user credentials')


# ──────────────────────────────────────────────
#  Mapas de formato por tipo de dato
# ──────────────────────────────────────────────
FORMAT_MAP = {
    "STRING":     "Texto libre (VARCHAR)",
    "BYTES":      "Cadena de bytes",
    "INT64":      "Entero (64 bits)",
    "INTEGER":    "Entero",
    "FLOAT64":    "Decimal (64 bits)",
    "FLOAT":      "Decimal",
    "NUMERIC":    "Numérico de precisión fija",
    "BIGNUMERIC": "Numérico de alta precisión",
    "BOOL":       "Booleano (TRUE / FALSE)",
    "BOOLEAN":    "Booleano (TRUE / FALSE)",
    "DATE":       "YYYY-MM-DD",
    "TIME":       "HH:MM:SS",
    "DATETIME":   "YYYY-MM-DD HH:MM:SS",
    "TIMESTAMP":  "YYYY-MM-DD HH:MM:SS UTC",
    "RECORD":     "Estructura anidada (STRUCT)",
    "STRUCT":     "Estructura anidada",
    "ARRAY":      "Arreglo de valores",
    "GEOGRAPHY":  "Punto / Polígono geográfico",
    "JSON":       "Objeto JSON",
}

DISTINCT_THRESHOLD = 15   # Nro. máximo de valores únicos para listar "Valores Permitidos"
SAMPLE_LIMIT       = 5    # Cuántos ejemplos mostrar en la columna Formato


# ──────────────────────────────────────────────
#  Clasificación de sensibilidad según DC-DG-03-02
# ──────────────────────────────────────────────
def classify_sensitivity(column_name: str, data_type: str, distinct_count: int = 0) -> tuple[str, str, str]:
    """
    Clasifica la sensibilidad de una columna según Global Data Sensitivity 
    Classification Standard DC-DG-03-02.
    
    Returns:
        tuple: (clasificación, referencia_standard, observación)
        - clasificación: "Highly Sensitive", "Sensitive", o "Non Sensitive"
        - referencia_standard: Sección del DC-DG-03-02
        - observación: Justificación detallada
    """
    col_lower = column_name.lower()
    
    # ═══════════════════════════════════════════════════════════════════
    # HIGHLY SENSITIVE - DC-DG-03-02 Section 3.1 & Appendix A Category 1
    # ═══════════════════════════════════════════════════════════════════
    
    # PII - Personally Identifiable Information
    if any(pattern in col_lower for pattern in ['ssn', 'social_security', 'tax_id', 'tin', 'itin']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.1 | Appendix A.1.a - PII Identifiers",
            "Contiene identificadores de seguridad social o tributarios que permiten identificar únicamente a un individuo. Requiere encriptación en reposo y en tránsito. Acceso restringido y auditoría obligatoria."
        )
    
    if any(pattern in col_lower for pattern in ['passport', 'driver_license', 'license_number', 'cedula', 'dni']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.1 | Appendix A.1.b - Government IDs",
            "Documentos de identificación gubernamental. Alto riesgo de robo de identidad. Requiere encriptación AES-256, controles de acceso basados en roles y logging de todas las consultas."
        )
    
    if any(pattern in col_lower for pattern in ['birth_date', 'dob', 'date_of_birth', 'birthdate']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.1 | Appendix A.1.c - Date of Birth",
            "Fecha de nacimiento combinada con otros datos puede identificar únicamente a un individuo. Clasificada como PII según GDPR y CCPA. Acceso limitado a procesos autorizados."
        )
    
    # Financial Data
    if any(pattern in col_lower for pattern in ['card_number', 'card_num', 'credit_card', 'cc_num', 'cvv', 'pan', 'card_holder']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.2 | Appendix A.2.a - Payment Card Data (PCI-DSS)",
            "Información de tarjetas de pago sujeta a PCI-DSS. Prohibido almacenar CVV/CVV2. PAN debe estar tokenizado o enmascarado. Violaciones pueden resultar en multas de $5K-$500K por incidente."
        )
    
    if any(pattern in col_lower for pattern in ['bank_account', 'routing_number', 'iban', 'swift', 'account_number']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.2 | Appendix A.2.b - Banking Information",
            "Información bancaria que permite realizar transacciones financieras. Requiere encriptación, tokenización cuando sea posible, y acceso restringido a sistemas de pago autorizados."
        )
    
    if any(pattern in col_lower for pattern in ['salary', 'wage', 'income', 'compensation', 'bonus']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.2 | Appendix A.2.c - Compensation Data",
            "Información salarial confidencial. Divulgación no autorizada puede causar problemas legales y de relaciones laborales. Acceso limitado a HR y Finance con justificación de negocio."
        )
    
    # PHI - Protected Health Information
    if any(pattern in col_lower for pattern in ['medical', 'diagnosis', 'prescription', 'health', 'hipaa', 'patient']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.3 | Appendix A.3 - Protected Health Information (HIPAA)",
            "Información de salud protegida bajo HIPAA. Requiere controles de acceso estrictos, encriptación, y BAA (Business Associate Agreement) para terceros. Violaciones: hasta $50K por registro."
        )
    
    # Credentials & Secrets
    if any(pattern in col_lower for pattern in ['password', 'pwd', 'secret', 'token', 'api_key', 'private_key', 'auth']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.4 | Appendix A.4 - Authentication Credentials",
            "Credenciales de autenticación. NUNCA almacenar en texto plano. Usar hashing (bcrypt/Argon2) para passwords, secretos en vault (Azure Key Vault/HashiCorp Vault). Rotación obligatoria cada 90 días."
        )
    
    # Biometric Data
    if any(pattern in col_lower for pattern in ['biometric', 'fingerprint', 'retina', 'facial', 'voice_print']):
        return (
            "Highly Sensitive",
            "DC-DG-03-02 Section 3.1.5 | Appendix A.5 - Biometric Data",
            "Datos biométricos irreversibles. Clasificación más alta bajo GDPR/BIPA. Requiere consentimiento explícito, encriptación y derecho al olvido. Prohibido uso sin autorización legal."
        )
    
    # ═══════════════════════════════════════════════════════════════════
    # SENSITIVE - DC-DG-03-02 Section 3.2 & Appendix A Category 2
    # ═══════════════════════════════════════════════════════════════════
    
    # Personal Contact Information
    if any(pattern in col_lower for pattern in ['email', 'e_mail', 'mail', 'correo']):
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.1 | Appendix A.6.a - Email Address",
            "Dirección de email puede usarse para phishing/spam. Considerar PII bajo GDPR. Requiere opt-in para marketing, encriptación en tránsito (TLS), y derecho a eliminación bajo solicitud."
        )
    
    if any(pattern in col_lower for pattern in ['phone', 'telephone', 'mobile', 'cell', 'telefono']):
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.1 | Appendix A.6.b - Phone Number",
            "Número telefónico clasificado como PII en combinación con otros datos. Requiere protección contra acceso no autorizado y opt-out para comunicaciones comerciales (TCPA compliance)."
        )
    
    if any(pattern in col_lower for pattern in ['address', 'street', 'zip', 'postal', 'city', 'state', 'direccion']):
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.1 | Appendix A.6.c - Physical Address",
            "Dirección física puede identificar residencia/ubicación de individuos. PII bajo GDPR/CCPA. Requiere consentimiento para uso, acceso controlado, y capacidad de rectificación/eliminación."
        )
    
    # Personal Names
    if any(pattern in col_lower for pattern in ['name', 'first_name', 'last_name', 'full_name', 'fname', 'lname', 'nombre', 'apellido']):
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.1 | Appendix A.6.d - Personal Names",
            "Nombres personales clasificados como PII. Requieren protección de privacidad, especialmente en combinación con otros datos. Derecho de acceso, rectificación y portabilidad bajo GDPR."
        )
    
    # Customer/User Data
    if any(pattern in col_lower for pattern in ['customer', 'client', 'user', 'member']):
        if not any(tech in col_lower for tech in ['_id', '_cd', 'load', 'upd', 'system']):
            return (
                "Sensitive",
                "DC-DG-03-02 Section 3.2.2 | Appendix A.7.a - Customer Data",
                "Información de clientes que puede contener datos personales. Sujeto a políticas de privacidad y términos de servicio. Acceso basado en need-to-know y auditoría de consultas."
            )
    
    # Transactional Data
    if any(pattern in col_lower for pattern in ['order', 'purchase', 'transaction', 'payment']):
        if '_cd' in col_lower or '_id' in col_lower or '_num' in col_lower:
            return (
                "Sensitive",
                "DC-DG-03-02 Section 3.2.3 | Appendix A.7.b - Transaction Identifiers",
                "Identificadores de transacciones comerciales. Pueden vincularse a individuos y revelar patrones de compra. Requiere protección contra acceso no autorizado y retención limitada según política."
            )
    
    if any(pattern in col_lower for pattern in ['price', 'amount', 'cost', 'total', 'subtotal']) and data_type in ['INT64', 'FLOAT64', 'NUMERIC']:
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.3 | Appendix A.7.c - Financial Amounts",
            "Montos financieros de transacciones. Información comercialmente sensible que puede revelar estrategias de pricing o comportamiento de compra. Acceso controlado a equipos autorizados."
        )
    
    # Seller/Vendor Data
    if any(pattern in col_lower for pattern in ['seller', 'vendor', 'supplier']):
        if '_cd' in col_lower or '_id' in col_lower:
            return (
                "Sensitive",
                "DC-DG-03-02 Section 3.2.4 | Appendix A.7.d - Seller/Vendor Identifiers",
                "Identificadores de vendedores/proveedores. Información comercial sensible que puede revelar relaciones de negocio. Sujeto a acuerdos de confidencialidad y NDA."
            )
    
    # IP Addresses
    if any(pattern in col_lower for pattern in ['ip_address', 'ip_addr', 'ip']):
        return (
            "Sensitive",
            "DC-DG-03-02 Section 3.2.5 | Appendix A.8 - Network Identifiers",
            "Direcciones IP pueden identificar dispositivos/usuarios bajo GDPR (PII indirecta). Requiere protección, anonimización para analytics, y retención limitada (típicamente 90-180 días)."
        )
    
    # Username/UserID technical fields
    if any(pattern in col_lower for pattern in ['userid', 'user_id', 'username']):
        if any(tech in col_lower for tech in ['load', 'upd', 'create', 'modify']):
            return (
                "Sensitive",
                "DC-DG-03-02 Section 3.2.6 | Appendix A.9 - System User Identifiers",
                "Identificadores de usuarios del sistema para auditoría. Puede revelar quién accedió/modificó datos. Requiere protección para prevenir suplantación y mantener integridad de audit trails."
            )
    
    # ═══════════════════════════════════════════════════════════════════
    # NON SENSITIVE - DC-DG-03-02 Section 3.3 & Appendix A Category 3
    # ═══════════════════════════════════════════════════════════════════
    
    # Technical metadata - timestamps
    if any(pattern in col_lower for pattern in ['_ts', '_dt', '_date', '_time']) and not any(birth in col_lower for birth in ['birth', 'dob']):
        return (
            "Non Sensitive",
            "DC-DG-03-02 Section 3.3.1 | Appendix A.10.a - Technical Timestamps",
            "Marcas de tiempo técnicas para auditoría y control de procesos ETL. No contienen información personal o comercialmente sensible. Útiles para troubleshooting y optimización."
        )
    
    # Status codes and flags
    if any(pattern in col_lower for pattern in ['status', 'state', 'flag', 'ind', 'indicator']):
        if not any(sensitive in col_lower for sensitive in ['payment', 'health', 'medical']):
            return (
                "Non Sensitive",
                "DC-DG-03-02 Section 3.3.2 | Appendix A.10.b - Status Indicators",
                "Códigos de estado operacional. Información técnica no sensible usada para control de flujo y lógica de negocio. No requiere controles especiales de acceso."
            )
    
    # Geographic codes (non-specific)
    if any(pattern in col_lower for pattern in ['country', 'region', 'geo', 'zone']) and '_cd' in col_lower:
        return (
            "Non Sensitive",
            "DC-DG-03-02 Section 3.3.3 | Appendix A.10.c - Geographic Codes",
            "Códigos geográficos a nivel país/región. Información pública no sensible. Útil para segmentación de reportes y análisis sin riesgo de privacidad."
        )
    
    # Host/Platform identifiers
    if any(pattern in col_lower for pattern in ['host', 'platform', 'site', 'channel']):
        return (
            "Non Sensitive",
            "DC-DG-03-02 Section 3.3.4 | Appendix A.10.d - Platform Identifiers",
            "Identificadores de plataforma/sitio web. Información técnica operacional. No presenta riesgo de privacidad o seguridad. Útil para análisis de tráfico y performance."
        )
    
    # Company/Organization codes
    if any(pattern in col_lower for pattern in ['company', 'cmpny', 'org', 'division']):
        return (
            "Non Sensitive",
            "DC-DG-03-02 Section 3.3.5 | Appendix A.10.e - Organization Codes",
            "Códigos de organización/empresa. Información estructural interna. No confidencial pero útil para reporting jerárquico y consolidación de datos."
        )
    
    # Year/Month partitions
    if any(pattern in col_lower for pattern in ['year_mth', 'year_month', 'partition', 'periodo']):
        return (
            "Non Sensitive",
            "DC-DG-03-02 Section 3.3.6 | Appendix A.10.f - Time Partitions",
            "Particiones temporales para optimización de queries. Información técnica de organización de datos. No sensible, mejora performance de consultas analíticas."
        )
    
    # Default for unmatched columns
    return (
        "Non Sensitive",
        "DC-DG-03-02 Section 3.3.7 | Appendix A.10.g - General Non-Sensitive Data",
        f"Campo de tipo {data_type} sin patrones de información sensible detectados. Clasificación por defecto. Revisar manualmente si el contexto de negocio indica mayor sensibilidad."
    )


def generate_description(column_name: str, data_type: str, distinct_count: int = 0) -> str:
    """
    Genera una descripción funcional automática basada en el nombre de la columna.
    """
    col_lower = column_name.lower()
    
    # Diccionario de descripciones por sufijos/patrones comunes
    descriptions = {
        '_cd': 'Código identificador',
        '_id': 'Identificador único',
        '_desc': 'Descripción textual',
        '_ts': 'Marca de tiempo (timestamp)',
        '_dt': 'Fecha',
        '_date': 'Fecha',
        '_time': 'Hora',
        '_flg': 'Indicador booleano (flag)',
        '_ind': 'Indicador',
        '_cnt': 'Contador',
        '_num': 'Número',
        '_amt': 'Monto o cantidad',
        '_pct': 'Porcentaje',
        '_qty': 'Cantidad',
        'load_': 'Campo técnico de carga de datos',
        'upd_': 'Campo técnico de actualización',
        '_userid': 'Usuario que realizó la operación',
        'year_mth': 'Periodo en formato año-mes',
        'order': 'Información de pedido',
        'seller': 'Información del vendedor',
        'country': 'País',
        'host': 'Sitio web o plataforma',
        'status': 'Estado o estatus',
        'delivery': 'Información de entrega',
        'dlvr': 'Información de entrega (delivery)',
        'geo': 'Información geográfica',
        'region': 'Región geográfica',
        'ontime': 'Indicador de puntualidad',
    }
    
    # Buscar patrones
    for pattern, desc in descriptions.items():
        if pattern in col_lower:
            # Personalizar según el nombre específico
            if pattern in ['_cd', '_id']:
                prefix = column_name.replace('_cd', '').replace('_id', '').replace('_', ' ').title()
                return f"{desc} de {prefix}"
            elif pattern in ['_desc']:
                prefix = column_name.replace('_desc', '').replace('_', ' ').title()
                return f"{desc} del campo {prefix}"
            elif pattern in ['_ts', '_dt', '_date']:
                prefix = column_name.replace('_ts', '').replace('_dt', '').replace('_date', '').replace('_', ' ').title()
                return f"Fecha/hora de {prefix}"
            else:
                return desc
    
    # Si no hay patrón reconocido, descripción genérica basada en tipo
    if data_type in ['STRING', 'BYTES']:
        return f"Campo de texto: {column_name}"
    elif data_type in ['INT64', 'INTEGER', 'FLOAT64', 'NUMERIC']:
        return f"Campo numérico: {column_name}"
    elif data_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
        return f"Campo de fecha/hora: {column_name}"
    elif data_type in ['BOOL', 'BOOLEAN']:
        return f"Indicador booleano: {column_name}"
    else:
        return f"Campo de tipo {data_type}: {column_name}"


# ──────────────────────────────────────────────
#  Función principal
# ──────────────────────────────────────────────
def analyze_table(project_id: str, dataset_id: str, table_id: str, billing_project: str = None) -> pd.DataFrame:
    """
    Analiza una tabla de BigQuery y devuelve un DataFrame con las
    reglas de negocio por columna.

    Args:
        project_id: Proyecto donde está la tabla
        dataset_id: Dataset de la tabla
        table_id: Nombre de la tabla
        billing_project: Proyecto para billing (si es diferente al project_id)

    Columnas del DataFrame resultante:
        Columna | Tabla Origen | Tipo | Formato | Valores Permitidos | Valor Nulo Permitido
    """
    # Usar billing_project si se especifica, sino usar project_id
    billing_proj = billing_project if billing_project else project_id
    client = bigquery.Client(project=billing_proj)
    table_ref = f"`{project_id}.{dataset_id}.{table_id}`"

    print(f"\n[>>] Consultando INFORMATION_SCHEMA para: {project_id}.{dataset_id}.{table_id}")

    # ── 1. Estructura de columnas desde INFORMATION_SCHEMA ──────────────────
    query_schema = f"""
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table_id}'
        ORDER BY ordinal_position
    """
    df_schema = client.query(query_schema).to_dataframe()

    if df_schema.empty:
        raise ValueError(
            f"No se encontraron columnas para la tabla '{table_id}' "
            f"en el dataset '{dataset_id}' del proyecto '{project_id}'.\n"
            "Verifica que el proyecto, dataset y tabla sean correctos."
        )

    print(f"[OK] {len(df_schema)} columnas encontradas. Iniciando profiling...\n")

    rows = []

    for _, schema_row in df_schema.iterrows():
        col        = schema_row["column_name"]
        data_type  = schema_row["data_type"].upper()
        is_nullable = str(schema_row["is_nullable"]).strip().upper()  # "YES" / "NO"

        print(f"   > Analizando columna: {col} ({data_type})")

        # ── 2. Profiling individual por columna ──────────────────────────────────────
        formato         = FORMAT_MAP.get(data_type, data_type)
        allowed_values  = "Sin restricción definida"
        ejemplo_real    = ""
        distinct_count  = 0

        try:
            # Cuantos valores distintos tiene?
            q_distinct = f"""
                SELECT COUNT(DISTINCT CAST({col} AS STRING)) AS cnt
                FROM {table_ref}
            """
            distinct_count = client.query(q_distinct).to_dataframe().iloc[0]["cnt"]

            if 0 < distinct_count <= DISTINCT_THRESHOLD:
                # Lista cerrada → enumeramos los valores
                q_vals = f"""
                    SELECT DISTINCT CAST({col} AS STRING) AS v
                    FROM {table_ref}
                    WHERE {col} IS NOT NULL
                    ORDER BY 1
                    LIMIT {DISTINCT_THRESHOLD}
                """
                vals_list = (
                    client.query(q_vals)
                    .to_dataframe()["v"]
                    .dropna()
                    .tolist()
                )
                allowed_values = ", ".join(str(v) for v in vals_list)
            
            # Extraer un ejemplo real de la columna
            q_example = f"""
                SELECT CAST({col} AS STRING) AS sample
                FROM {table_ref}
                WHERE {col} IS NOT NULL
                LIMIT 1
            """
            example_df = client.query(q_example).to_dataframe()
            if not example_df.empty:
                ejemplo_real = str(example_df.iloc[0]["sample"])

            # Para tipos con formato específico, añadimos un ejemplo real
            if data_type in ("DATE", "DATETIME", "TIMESTAMP", "TIME"):
                q_sample = f"""
                    SELECT CAST({col} AS STRING) AS sample
                    FROM {table_ref}
                    WHERE {col} IS NOT NULL
                    LIMIT 1
                """
                sample_df = client.query(q_sample).to_dataframe()
                if not sample_df.empty:
                    sample_val = sample_df.iloc[0]["sample"]
                    formato = f"{FORMAT_MAP.get(data_type, data_type)}  (ej. {sample_val})"

            # Para numéricos, rango mínimo–máximo
            elif data_type in ("INT64", "INTEGER", "FLOAT64", "FLOAT", "NUMERIC", "BIGNUMERIC"):
                q_range = f"""
                    SELECT
                        MIN(CAST({col} AS FLOAT64)) AS min_val,
                        MAX(CAST({col} AS FLOAT64)) AS max_val
                    FROM {table_ref}
                    WHERE {col} IS NOT NULL
                """
                range_df = client.query(q_range).to_dataframe()
                if not range_df.empty:
                    min_v = range_df.iloc[0]["min_val"]
                    max_v = range_df.iloc[0]["max_val"]
                    if min_v is not None and max_v is not None:
                        formato = f"{FORMAT_MAP.get(data_type, data_type)}  [rango: {min_v} – {max_v}]"

        except Exception as exc:
            print(f"     [!] Error en profiling de '{col}': {exc}")
            allowed_values = "Error al consultar"

        # ── 3. Construir fila de resultados ──────────────────────────────────
        
        # Generar descripción automática
        descripcion = generate_description(col, data_type, distinct_count)
        
        # Clasificar sensibilidad según DC-DG-03-02 (retorna 3 valores)
        sensibilidad, referencia_std, observacion_std = classify_sensitivity(col, data_type, distinct_count)
        
        # Determinar criticidad basada en sensibilidad
        if sensibilidad == "Highly Sensitive":
            criticidad = "Alta"
            justificacion = "Información altamente sensible que requiere máximos controles de seguridad"
        elif sensibilidad == "Sensitive":
            criticidad = "Media"
            justificacion = "Información sensible que requiere protección adecuada"
        else:
            criticidad = "Baja"
            justificacion = "Información técnica/operacional sin riesgo de privacidad"
        
        rows.append({
            "Columna":                      col,
            "Descripcion":                  descripcion,
            "Tabla Origen":                 f"{project_id}.{dataset_id}.{table_id}",
            "Tipo":                         data_type,
            "Formato":                      formato,
            "Valores Permitidos":           allowed_values,
            "Valor Nulo Permitido":         "Si" if is_nullable == "YES" else "No",
            "Criticidad":                   criticidad,
            "Justificacion de Criticidad":  justificacion,
            "Ejemplo":                      ejemplo_real,
            "Clasificacion de Sensibilidad": sensibilidad,
            "Referencia Standard":          referencia_std,
            "Observacion":                  observacion_std,
        })

    print(f"\n[OK] Profiling completado para {len(rows)} columnas.")
    return pd.DataFrame(rows)
