# 🔧 Fix: Error 'MergedCell' object attribute 'value' is read-only

**Fecha**: 2026-04-20  
**Error**: `'MergedCell' object attribute 'value' is read-only`  
**Status**: ✅ RESUELTO

---

## 🐛 Problema Original

Al ejecutar el generador, openpyxl lanzaba un error cuando intentaba limpiar las hojas "Metadatos" y "Resumen por Clasificacion" del template:

```python
# ❌ Código problemático
for row in ws_meta.iter_rows():
    for cell in row:
        cell.value = None  # ❌ Falla si la celda está fusionada
```

**Causa raíz:**  
- El template contiene celdas fusionadas (merged cells)
- En openpyxl, las celdas fusionadas son de solo lectura
- Solo la celda superior izquierda de una fusión es modificable

---

## ✅ Solución Implementada

En lugar de **limpiar** las hojas, ahora las **eliminamos y recreamos**:

```python
# ✅ Código corregido

# Para Metadatos
if "Metadatos" in wb.sheetnames:
    wb.remove(wb["Metadatos"])  # Eliminar hoja completa
ws_meta = wb.create_sheet("Metadatos")  # Recrear desde cero

# Para Resumen por Clasificacion
if "Resumen por Clasificacion" in wb.sheetnames:
    wb.remove(wb["Resumen por Clasificacion"])
ws_summary = wb.create_sheet("Resumen por Clasificacion", 1)
```

**Ventajas:**
- ✅ Elimina el problema de celdas fusionadas
- ✅ Código más simple y robusto
- ✅ No requiere desfusionar celdas
- ✅ Más eficiente (no itera sobre todas las celdas)

---

## 🧪 Validación

### Test Ejecutado
```bash
python test_template.py
```

### Resultado
```
[TEST] Iniciando prueba del generador basado en template...

[i] Usando template: Reglas_Negocio_template.xlsx

[OK] Excel generado exitosamente:
    C:\...\output\Reglas_Negocio_test_table_20260420_145751.xlsx

[OK] El sistema basado en template funciona correctamente!
```

✅ **Sin errores**  
✅ **Archivo generado correctamente**  
✅ **Template copiado y poblado**

---

## 📝 Archivos Modificados

### excel_generator.py (líneas ~160-180)

**Cambio 1: Hoja Metadatos**
```diff
- # Si ya existe la hoja, la limpiamos
- if "Metadatos" in wb.sheetnames:
-     ws_meta = wb["Metadatos"]
-     for row in ws_meta.iter_rows():
-         for cell in row:
-             cell.value = None
- else:
-     ws_meta = wb.create_sheet("Metadatos")

+ # Eliminar y recrear la hoja
+ if "Metadatos" in wb.sheetnames:
+     wb.remove(wb["Metadatos"])
+ ws_meta = wb.create_sheet("Metadatos")
```

**Cambio 2: Hoja Resumen por Clasificacion**
```diff
- # Si ya existe la hoja, la limpiamos
- if "Resumen por Clasificacion" in wb.sheetnames:
-     ws_summary = wb["Resumen por Clasificacion"]
-     for row in ws_summary.iter_rows():
-         for cell in row:
-             cell.value = None
-             cell.fill = PatternFill(fill_type=None)
-             cell.font = Font()
-             cell.border = Border()
- else:
-     ws_summary = wb.create_sheet("Resumen por Clasificacion", 1)

+ # Eliminar y recrear la hoja
+ if "Resumen por Clasificacion" in wb.sheetnames:
+     wb.remove(wb["Resumen por Clasificacion"])
+ ws_summary = wb.create_sheet("Resumen por Clasificacion", 1)
```

---

## 🔍 Por Qué Funciona

1. **Eliminar hoja completa** (`wb.remove()`)
   - Libera todas las celdas, incluidas las fusionadas
   - Limpia toda la estructura de la hoja

2. **Recrear desde cero** (`wb.create_sheet()`)
   - Hoja nueva sin celdas fusionadas
   - Código puede escribir libremente
   - Estilos se aplican programáticamente

3. **No afecta otras hojas**
   - "Reglas de Negocio" mantiene su estructura del template
   - Solo se recrean las hojas que poblamos completamente

---

## 🎯 Comportamiento Final

### Flujo Completo

```
1. Copiar template → archivo_salida.xlsx
2. Cargar archivo con openpyxl
3. Hoja "Reglas de Negocio":
   ├─ Limpiar filas de datos (mantener header)
   └─ Escribir datos nuevos
4. Hoja "Metadatos":
   ├─ Eliminar hoja completa
   ├─ Recrear desde cero
   └─ Poblar con metadatos del proyecto
5. Hoja "Resumen por Clasificacion":
   ├─ Eliminar hoja completa
   ├─ Recrear desde cero
   └─ Poblar con resumen por sensibilidad
6. Guardar archivo final
```

---

## 🚀 Próximos Pasos

Sistema listo para producción. Puedes ejecutar:

```bash
cd "C:\Users\vn59q13\OneDrive - Walmart Inc\Documentos\bq_business_rules"
python main.py
```

Y el sistema:
- ✅ Usa el template correctamente
- ✅ No tiene errores de celdas fusionadas
- ✅ Genera archivos con formato consistente

---

## 📚 Referencias

- **openpyxl docs**: [Working with Merged Cells](https://openpyxl.readthedocs.io/en/stable/worksheet_merge.html)
- **Issue tracker**: Similar issues en openpyxl GitHub
- **Best practice**: Eliminar y recrear es preferible a limpiar cuando hay fusiones

---

**🐶 Fix implementado por Code Puppy**
