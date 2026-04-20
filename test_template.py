"""
Test rápido del sistema basado en template
"""

import pandas as pd
from excel_generator import generate_excel
import os

# Crear DataFrame de prueba con las 13 columnas esperadas
test_data = {
    "Columna": ["test_column_1", "test_column_2"],
    "Descripcion": ["Columna de prueba 1", "Columna de prueba 2"],
    "Tabla Origen": ["test_table", "test_table"],
    "Tipo": ["STRING", "INTEGER"],
    "Formato": ["Texto", "Numérico"],
    "Valores Permitidos": ["Cualquier texto", "1-999"],
    "Valor Nulo Permitido": ["Si", "No"],
    "Criticidad": ["Alta", "Baja"],
    "Justificacion de Criticidad": ["Datos críticos", "Datos auxiliares"],
    "Ejemplo": ["Ejemplo 1", "123"],
    "Clasificacion de Sensibilidad": ["Highly Sensitive", "Non Sensitive"],
    "Referencia Standard": ["DC-DG-03-02: PII", "DC-DG-03-02: Technical"],
    "Observacion": ["Observación 1", "Observación 2"],
}

df = pd.DataFrame(test_data)

print("[TEST] Iniciando prueba del generador basado en template...\n")

try:
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "output"
    )
    
    filepath = generate_excel(
        df=df,
        project_id="test-project",
        dataset_id="test_dataset",
        table_id="test_table",
        output_dir=output_dir
    )
    
    print("[OK] Test exitoso!")
    print(f"[OK] Archivo generado: {filepath}")
    print(f"\n[OK] El sistema basado en template funciona correctamente!")
    
    # Intentar abrir el archivo
    try:
        os.startfile(filepath)
        print("[OK] Abriendo archivo generado...")
    except:
        pass
        
except Exception as e:
    print(f"❌ Error en el test:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
