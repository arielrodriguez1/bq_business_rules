# 📋 Actualización: Sistema Basado en Template

**Fecha**: 2026-04-20  
**Versión**: v2.1.0  
**Autor**: Code Puppy 🐶

---

## 🎯 Objetivo del Cambio

Actualizar el generador de reglas de negocio para que **siempre use el archivo template** `Reglas_Negocio_template.xlsx` como base, garantizando:

✅ Formato corporativo 100% consistente  
✅ Estilos y colores Walmart estandarizados  
✅ Facilidad de personalización (logos, headers, footers)  
✅ Compatibilidad con herramientas de auditoría  

---

## 🔄 Cambios Realizados

### 1. **excel_generator.py**

#### ✨ Nuevo Comportamiento

**Antes:**
- Creaba un Excel desde cero usando `pd.ExcelWriter`
- Aplicaba estilos programáticamente

**Ahora:**
- 📁 Copia el template `Reglas_Negocio_template.xlsx`
- 📝 Renombra con timestamp: `Reglas_Negocio_{tabla}_{timestamp}.xlsx`
- 🎨 Mantiene todo el formato del template
- 📊 Solo puebla los datos en las hojas existentes

#### 🔧 Modificaciones Técnicas

```python
# Nueva constante
TEMPLATE_PATH = Path(r"C:\Users\vn59q13\OneDrive - Walmart Inc\Documentos\bq_business_rules\Reglas_Negocio_template.xlsx")

# Nuevo flujo en generate_excel():
1. Verificar que el template exista
2. Copiar template → archivo de salida
3. Cargar archivo copiado con openpyxl
4. Limpiar datos previos (mantener headers)
5. Escribir datos fila por fila
6. Aplicar estilos condicionales (criticidad, sensibilidad)
7. Actualizar pestañas Metadatos y Resumen
8. Guardar archivo final
```

#### 🛡️ Validaciones Añadidas

- ✅ Verifica que el template exista antes de copiar
- ✅ Valida que las hojas necesarias estén en el template
- ✅ Manejo seguro de valores None/vacíos en celdas

---

### 2. **README.md**

#### 📚 Documentación Actualizada

- ✨ Nueva sección **"Template Base"** con ubicación y flujo
- 📋 Diagrama de estructura actualizado
- 📝 Changelog con versión v2.1.0

---

## 🎨 Estructura del Template

El template debe contener **3 hojas** con estas columnas:

### Hoja 1: "Reglas de Negocio"
```
Columna | Descripción | Tabla Origen | Tipo | Formato | Valores Permitidos | 
Valor Nulo Permitido | Criticidad | Justificación de Criticidad | Ejemplo | 
Clasificación de Sensibilidad | Referencia Standard | Observación
```

### Hoja 2: "Resumen por Clasificacion"
Se puebla dinámicamente con datos agrupados por sensibilidad.

### Hoja 3: "Metadatos"
```
Proyecto GCP | Dataset | Tabla | Total columnas | Fecha generación | Generado por
```

---

## ✅ Validación de Cambios

### ✔️ Compilación
```bash
python -m py_compile excel_generator.py
# ✅ Sin errores
```

### ✔️ Template Detectado
```bash
python -c "from excel_generator import TEMPLATE_PATH; print(TEMPLATE_PATH.exists())"
# ✅ True
```

### ✔️ Estructura Verificada
- ✅ 3 hojas detectadas
- ✅ 13 columnas en "Reglas de Negocio"
- ✅ Headers coinciden con el código

---

## 🚀 Próximos Pasos

### Para usar el sistema actualizado:

1. **Verificar el template:**
   ```
   C:\Users\vn59q13\OneDrive - Walmart Inc\Documentos\bq_business_rules\Reglas_Negocio_template.xlsx
   ```

2. **Ejecutar el generador:**
   ```bash
   python main.py
   ```

3. **El sistema automáticamente:**
   - ✅ Copia el template
   - ✅ Puebla con datos de BigQuery
   - ✅ Guarda en `output/` con timestamp

---

## 📌 Personalización del Template

Si necesitas personalizar el formato:

1. Abre `Reglas_Negocio_template.xlsx`
2. Modifica:
   - 🎨 Colores corporativos
   - 🖼️ Logos en headers/footers
   - 📏 Anchos de columna
   - 🔤 Fuentes y estilos
   - 📊 Configuración de impresión
3. Guarda el template
4. **¡Todos los archivos futuros usarán el nuevo formato!**

---

## 🐛 Troubleshooting

### ❌ Error: "Template no encontrado"

**Solución:**
```python
# Verificar la ruta en excel_generator.py línea 23
TEMPLATE_PATH = Path(r"C:\Users\vn59q13\OneDrive - Walmart Inc\Documentos\bq_business_rules\Reglas_Negocio_template.xlsx")
```

### ❌ Error: "La hoja 'Reglas de Negocio' no existe"

**Solución:**  
El template debe tener exactamente estas hojas:
- Reglas de Negocio
- Resumen por Clasificacion
- Metadatos

---

## 📊 Comparación: Antes vs Ahora

| Aspecto | Antes (v2.0) | Ahora (v2.1) |
|---------|-------------|--------------|
| **Método** | Crear desde cero | Copiar template |
| **Formato** | Programático | Pre-diseñado |
| **Consistencia** | Variable | 100% idéntico |
| **Personalización** | Modificar código | Modificar template |
| **Mantenimiento** | Alto | Bajo |
| **Compatibilidad** | Básica | Corporativa |

---

## ✨ Beneficios del Cambio

1. **Consistencia Garantizada** 🎯
   - Todos los archivos tienen formato idéntico
   - Cumple estándares corporativos Walmart

2. **Facilidad de Personalización** 🎨
   - No requiere modificar código
   - Diseñadores pueden actualizar el template

3. **Mantenimiento Simplificado** 🔧
   - Menos código de estilos
   - Separación de lógica y presentación

4. **Compatibilidad Mejorada** 📊
   - Compatible con herramientas de auditoría
   - Formatos predefinidos para exportación

---

## 📞 Soporte

¿Preguntas o problemas?

- **Autor**: Ariel Rodriguez
- **Email**: ariel.rodriguez1@walmart.com
- **Teams**: Walmart Tech Data Governance

---

**🐶 Generado por Code Puppy - Tu asistente de código más fiel**
