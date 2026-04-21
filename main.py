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

from bq_analyzer    import analyze_table, validate_bigquery_permissions
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
#  Proyectos predefinidos de Walmart
# ──────────────────────────────────────────────
WALMART_PROJECTS = [
    "wmt-intl-cons-local-k1-prod",
    "wmt-intl-cons-mc-k1-prod",
    "wmt-k1-dwh-data-prod",
    "wmt-edw-prod",
    "wmt-k1-cons-data-users",
]


def _select_project() -> str:
    """
    Muestra un menú de proyectos predefinidos + opción 'Otro'.
    Retorna el project_id seleccionado.
    """
    print(f"\n{BOLD}  Selecciona un proyecto GCP:{RESET}\n")
    
    for idx, proj in enumerate(WALMART_PROJECTS, start=1):
        print(f"    [{idx}] {proj}")
    print(f"    [{len(WALMART_PROJECTS) + 1}] {YELLOW}Otro (digitar manualmente){RESET}")
    
    while True:
        choice = input(f"\n  {BOLD}Opción{RESET}: ").strip()
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(WALMART_PROJECTS):
                return WALMART_PROJECTS[idx - 1]
            elif idx == len(WALMART_PROJECTS) + 1:
                return _ask("Proyecto GCP", "mi-proyecto-gcp")
        
        print(f"  {RED}[!] Opción inválida. Por favor selecciona un número del 1 al {len(WALMART_PROJECTS) + 1}.{RESET}")


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
    
    # Selección de proyecto desde menú
    project_id = _select_project()
    
    # Validar permisos de BigQuery en el proyecto
    print(f"\n  {YELLOW}[i] Validando permisos de BigQuery en {project_id}...{RESET}")
    has_permissions = validate_bigquery_permissions(project_id)
    
    if not has_permissions:
        print(f"\n  {RED}[!] ERROR: No tienes permisos 'bigquery.jobs.create' en el proyecto {project_id}.{RESET}")
        print(f"      Solicita acceso o selecciona otro proyecto.\n")
        return _get_session_credentials()  # Recursión para volver a intentar
    
    print(f"  {GREEN}[OK] Permisos validados correctamente.{RESET}\n")
    
    dataset_id = _ask("Dataset en GCP", "mi_dataset")
    
    print(f"\n  {YELLOW}[?] Necesitas usar un proyecto diferente para ejecutar queries (billing)?{RESET}")
    print(f"      (Presiona ENTER para usar el mismo proyecto: {project_id})")
    billing_project = input(f"  {BOLD}Billing Project{RESET}: ").strip()
    
    if not billing_project:
        billing_project = project_id
    else:
        # Validar permisos en billing project también
        print(f"\n  {YELLOW}[i] Validando permisos en billing project {billing_project}...{RESET}")
        has_billing_permissions = validate_bigquery_permissions(billing_project)
        
        if not has_billing_permissions:
            print(f"\n  {RED}[!] ERROR: No tienes permisos 'bigquery.jobs.create' en {billing_project}.{RESET}")
            print(f"      Usando el proyecto principal para billing.\n")
            billing_project = project_id
        else:
            print(f"  {GREEN}[OK] Permisos de billing validados.{RESET}\n")
    
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
