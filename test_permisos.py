"""
test_permisos.py
----------------
Script de prueba para validar permisos de BigQuery en proyectos.
Uso rápido para verificar acceso sin ejecutar toda la aplicación.

Uso:
    python test_permisos.py
"""

from bq_analyzer import validate_bigquery_permissions

# Proyectos de Walmart a probar
PROYECTOS = [
    "wmt-intl-cons-local-k1-prod",
    "wmt-intl-cons-mc-k1-prod",
    "wmt-k1-dwh-data-prod",
    "wmt-edw-prod",
]

def test_all_projects():
    """Prueba permisos en todos los proyectos predefinidos."""
    print("\n" + "="*70)
    print("  🔍 VALIDACIÓN DE PERMISOS BIGQUERY - PROYECTOS WALMART")
    print("="*70 + "\n")
    
    resultados = {}
    
    for proyecto in PROYECTOS:
        print(f"📦 Probando proyecto: {proyecto}...")
        tiene_permisos = validate_bigquery_permissions(proyecto)
        resultados[proyecto] = tiene_permisos
        
        if tiene_permisos:
            print(f"   ✅ ACCESO CONFIRMADO\n")
        else:
            print(f"   ❌ SIN PERMISOS o SIN ACCESO\n")
    
    # Resumen
    print("="*70)
    print("  📊 RESUMEN DE PERMISOS")
    print("="*70 + "\n")
    
    proyectos_ok = [p for p, ok in resultados.items() if ok]
    proyectos_error = [p for p, ok in resultados.items() if not ok]
    
    if proyectos_ok:
        print("✅ PROYECTOS CON ACCESO:")
        for p in proyectos_ok:
            print(f"   • {p}")
        print()
    
    if proyectos_error:
        print("❌ PROYECTOS SIN ACCESO:")
        for p in proyectos_error:
            print(f"   • {p}")
        print()
        print("💡 Solicita acceso al owner del proyecto o al equipo de GCP Admin.")
        print()
    
    print("="*70)
    print(f"  Total: {len(proyectos_ok)}/{len(PROYECTOS)} proyectos accesibles")
    print("="*70 + "\n")


def test_custom_project():
    """Permite probar un proyecto personalizado."""
    print("\n" + "="*70)
    print("  🔍 PRUEBA DE PROYECTO PERSONALIZADO")
    print("="*70 + "\n")
    
    proyecto = input("Ingresa el ID del proyecto a probar: ").strip()
    
    if not proyecto:
        print("❌ No ingresaste un proyecto válido.\n")
        return
    
    print(f"\n📦 Probando proyecto: {proyecto}...")
    tiene_permisos = validate_bigquery_permissions(proyecto)
    
    print("\n" + "="*70)
    if tiene_permisos:
        print(f"  ✅ TIENES ACCESO al proyecto '{proyecto}'")
    else:
        print(f"  ❌ NO TIENES ACCESO al proyecto '{proyecto}'")
        print("\n  💡 Posibles causas:")
        print("     • No tienes el permiso 'bigquery.jobs.create'")
        print("     • El proyecto no existe")
        print("     • No estás conectado a Walmart VPN/Eagle WiFi")
        print("     • Credenciales de GCP no configuradas (gcloud auth login)")
    print("="*70 + "\n")


def main():
    """Menú principal del script de prueba."""
    while True:
        print("\n" + "="*70)
        print("  🐶 TEST DE PERMISOS BIGQUERY")
        print("="*70)
        print("\n  ¿Qué deseas hacer?\n")
        print("    [1] Probar todos los proyectos predefinidos")
        print("    [2] Probar un proyecto personalizado")
        print("    [3] Salir")
        
        opcion = input("\n  Opción: ").strip()
        
        if opcion == "1":
            test_all_projects()
        elif opcion == "2":
            test_custom_project()
        elif opcion == "3":
            print("\n  👋 ¡Hasta pronto!\n")
            break
        else:
            print("\n  ❌ Opción inválida. Por favor selecciona 1, 2 o 3.\n")


if __name__ == "__main__":
    main()
