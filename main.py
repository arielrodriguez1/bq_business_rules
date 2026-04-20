"""
╔══════════════════════════════════════════════════════════════════╗
║         BQ Business Rules Generator — Walmart Tech              ║
║  Genera un Excel con reglas de negocio desde BigQuery            ║
║  Basado en INFORMATION_SCHEMA + profiling de datos reales        ║
╚══════════════════════════════════════════════════════════════════╝

Uso:
    python main.py

El script solicita al inicio:
    • Proyecto GCP
    • Dataset
    • Tabla (se puede procesar más de una por sesión)
"""

import os
import sys

# ── Asegurar que el directorio del módulo esté en el path ───────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from bq_analyzer    import analyze_table
from excel_generator import generate_excel


# ──────────────────────────────────────────────
#  Configuración de salida
# ──────────────────────────────────────────────
OUTPUT_DIR = os.path.join(
    os.path.expanduser("~"),
    "OneDrive - Walmart Inc",
    "Documentos",
    "bq_business_rules",
    "output",
)


# ──────────────────────────────────────────────
#  Helpers de UI en consola
# ──────────────────────────────────────────────
BLUE   = "\033[94m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _banner():
    print(f"""
{BLUE}{BOLD}==================================================================
    BQ Business Rules Generator - Walmart Tech
    Genera reglas de negocio desde BigQuery Information Schema
=================================================================={RESET}
""")


def _ask(label: str, example: str = "") -> str:
    hint = f"  {YELLOW}(ej. {example}){RESET}" if example else ""
    while True:
        value = input(f"  {BOLD}{label}{RESET}{hint}: ").strip()
        if value:
            return value
        print(f"  {RED}[!] Este campo es obligatorio. Por favor ingresa un valor.{RESET}")


def _separator():
    print(f"{BLUE}{'=' * 66}{RESET}")


# ──────────────────────────────────────────────
#  Sesión de credenciales (se piden una vez)
# ──────────────────────────────────────────────
def _get_session_credentials() -> tuple[str, str, str]:
    """
    Solicita proyecto y dataset al inicio de la sesión.
    Retorna (project_id, dataset_id, billing_project).
    """
    _separator()
    print(f"\n{BOLD}  >> Configuracion de sesion{RESET}\n")
    project_id = _ask("Proyecto GCP (donde estan los datos)",  "wmt-intl-cons-mc-k1-prod")
    dataset_id = _ask("Dataset en GCP", "mi_dataset")
    
    print(f"\n  {YELLOW}[?] Necesitas usar un proyecto diferente para ejecutar queries (billing)?{RESET}")
    print(f"      (Presiona ENTER para usar el mismo proyecto: {project_id})")
    billing_project = input(f"  {BOLD}Billing Project{RESET}: ").strip()
    
    if not billing_project:
        billing_project = project_id
    
    return project_id, dataset_id, billing_project


# ──────────────────────────────────────────────
#  Procesamiento de una tabla
# ──────────────────────────────────────────────
def _process_table(project_id: str, dataset_id: str, table_id: str, billing_project: str = None):
    print()
    _separator()
    print(f"\n{BOLD}  >> Procesando tabla: {project_id}.{dataset_id}.{table_id}{RESET}\n")
    if billing_project and billing_project != project_id:
        print(f"  {YELLOW}[i] Usando billing project: {billing_project}{RESET}\n")
    _separator()

    try:
        # 1. Analizar la tabla en BigQuery
        df = analyze_table(project_id, dataset_id, table_id, billing_project)

        # 2. Mostrar preview en consola
        _separator()
        print(f"\n{BOLD}  >> Vista previa de resultados ({len(df)} columnas){RESET}\n")
        preview_cols = ["Columna", "Descripcion", "Tipo", "Criticidad", "Clasificacion de Sensibilidad"]
        print(df[preview_cols].to_string(index=False, max_colwidth=60))
        print()

        # 3. Generar Excel
        filepath = generate_excel(
            df         = df,
            project_id = project_id,
            dataset_id = dataset_id,
            table_id   = table_id,
            output_dir = OUTPUT_DIR,
        )

        print(f"  {GREEN}[OK] Archivo listo:{RESET}")
        print(f"      {filepath}\n")

        # Intentar abrir la carpeta de salida (Windows)
        try:
            os.startfile(OUTPUT_DIR)
        except Exception:
            pass

    except Exception as exc:
        print(f"\n  {RED}[ERROR] Error al procesar la tabla:{RESET}")
        print(f"      {exc}\n")


# ──────────────────────────────────────────────
#  Loop principal
# ──────────────────────────────────────────────
def main():
    _banner()

    # Solicitar credenciales una sola vez por sesión
    project_id, dataset_id, billing_project = _get_session_credentials()

    while True:
        _separator()
        print(f"\n{BOLD}  >> Nueva consulta  {YELLOW}(proyecto: {project_id} | dataset: {dataset_id}){RESET}\n")

        table_id = _ask("Nombre de la tabla", "mi_tabla")

        _process_table(project_id, dataset_id, table_id, billing_project)

        # -- Continuar? ----------------------------------------------------------
        _separator()
        print(f"\n  {BOLD}Que deseas hacer a continuacion?{RESET}")
        print("    [1] Analizar otra tabla en el mismo dataset")
        print("    [2] Cambiar proyecto / dataset")
        print("    [3] Salir")
        opcion = input("\n  Opción: ").strip()

        if opcion == "1":
            continue
        elif opcion == "2":
            project_id, dataset_id, billing_project = _get_session_credentials()
        else:
            print(f"\n  {GREEN}Hasta pronto!{RESET}\n")
            break


if __name__ == "__main__":
    main()
