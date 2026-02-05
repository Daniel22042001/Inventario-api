# Sistema de Gestión de Inventario

**Estudiante:** YAGUACHI GALARZA DANIEL ALEJANDRO

API REST completa para la gestión de items de inventario construida con FastAPI y PostgreSQL.

## 📋 Entidad: ItemInventario

### Atributos:
- **id**: INTEGER (Primary Key, Auto-increment)
- **nombre**: VARCHAR(255) - Nombre del item
- **categoria**: VARCHAR(100) - Categoría del item
- **cantidad**: INTEGER - Cantidad en inventario (≥ 0)
- **precioUnitario**: DECIMAL(10,2) - Precio unitario (> 0)

## 🚀 Características

- ✅ **CRUD Completo** de items de inventario
- ✅ **Validaciones** de datos con Pydantic
- ✅ **Consultas avanzadas** (búsqueda por categoría, items bajo stock)
- ✅ **Estadísticas** (valor total, estadísticas por categoría)
- ✅ **Documentación automática** con Swagger UI
- ✅ **Base de datos PostgreSQL**
- ✅ **Índices** para optimizar consultas
- ✅ **CORS habilitado**
- ✅ **Health check** endpoint

## 📚 Endpoints Disponibles

### **CRUD Básico**

#### 1. Listar todos los items
```http
GET /api/inventario
```
Retorna todos los items del inventario.

#### 2. Obtener un item específico
```http
GET /api/inventario/{id}
```
Retorna un item por su ID.

#### 3. Crear nuevo item
```http
POST /api/inventario
Content-Type: application/json

{
  "nombre": "Laptop Dell",
  "categoria": "Tecnología",
  "cantidad": 15,
  "precioUnitario": 1200.50
}
```

#### 4. Actualizar item
```http
PUT /api/inventario/{id}
Content-Type: application/json

{
  "cantidad": 20,
  "precioUnitario": 1150.00
}
```
Nota: Todos los campos son opcionales en la actualización.

#### 5. Eliminar item
```http
DELETE /api/inventario/{id}
```

### **Consultas Avanzadas**

#### 6. Buscar por categoría
```http
GET /api/inventario/categoria/{categoria}
```
Ejemplo: `/api/inventario/categoria/Tecnología`

#### 7. Items con bajo stock
```http
GET /api/inventario/bajo-stock/{cantidad_minima}
```
Ejemplo: `/api/inventario/bajo-stock/10` - Retorna items con 10 o menos unidades

### **Estadísticas**

#### 8. Valor total del inventario
```http
GET /api/inventario/estadisticas/valor-total
```
Retorna:
- Total de items diferentes
- Total de unidades
- Valor total del inventario
- Precio promedio

#### 9. Estadísticas por categoría
```http
GET /api/inventario/estadisticas/por-categoria
```
Retorna estadísticas agrupadas por cada categoría.

### **Otros Endpoints**

#### 10. Información del sistema
```http
GET /
```

#### 11. Health Check
```http
GET /health
```

#### 12. Documentación interactiva
```http
GET /docs
```

## 🛠️ Instalación y Ejecución Local

### **Prerrequisitos**
- Python 3.11 o superior
- PostgreSQL instalado y corriendo

### **Pasos:**

1. **Clonar/Extraer el proyecto**

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
# Crear base de datos en PostgreSQL
createdb inventario_db

# O usando psql
psql -U postgres
CREATE DATABASE inventario_db;
\q
```

5. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

6. **Ejecutar la aplicación**
```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## 🌐 Despliegue en Railway

### **Opción 1: Desde GitHub (Recomendado)**

1. **Subir código a GitHub**
```bash
git init
git add .
git commit -m "Sistema de Gestión de Inventario"
git branch -M main
git remote add origin <tu-repo-url>
git push -u origin main
```

2. **Crear proyecto en Railway**
- Ve a [Railway.app](https://railway.app)
- Click "New Project"
- Selecciona "Deploy from GitHub repo"
- Selecciona tu repositorio

3. **Agregar PostgreSQL**
- En tu proyecto, click "+ New"
- Selecciona "Database" → "PostgreSQL"
- Railway conectará automáticamente `DATABASE_URL`

4. **Generar dominio**
- Ve a Settings → Networking
- Click "Generate Domain"
- Tu API estará disponible públicamente

### **Opción 2: Railway CLI**

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Agregar PostgreSQL
railway add

# Desplegar
railway up
```

## 📊 Ejemplos de Uso

### **Crear items de ejemplo**

```bash
# Item 1: Laptop
curl -X POST "http://localhost:8000/api/inventario" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell Inspiron 15",
    "categoria": "Tecnología",
    "cantidad": 25,
    "precioUnitario": 899.99
  }'

# Item 2: Mouse
curl -X POST "http://localhost:8000/api/inventario" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mouse Logitech MX Master 3",
    "categoria": "Tecnología",
    "cantidad": 50,
    "precioUnitario": 99.99
  }'

# Item 3: Silla
curl -X POST "http://localhost:8000/api/inventario" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Silla Ergonómica",
    "categoria": "Mobiliario",
    "cantidad": 15,
    "precioUnitario": 249.99
  }'
```

### **Consultar items**

```bash
# Listar todos
curl "http://localhost:8000/api/inventario"

# Ver item específico
curl "http://localhost:8000/api/inventario/1"

# Buscar por categoría
curl "http://localhost:8000/api/inventario/categoria/Tecnología"

# Items con bajo stock (≤ 20 unidades)
curl "http://localhost:8000/api/inventario/bajo-stock/20"

# Estadísticas
curl "http://localhost:8000/api/inventario/estadisticas/valor-total"
```

### **Actualizar item**

```bash
curl -X PUT "http://localhost:8000/api/inventario/1" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad": 30,
    "precioUnitario": 849.99
  }'
```

### **Eliminar item**

```bash
curl -X DELETE "http://localhost:8000/api/inventario/1"
```

## 🔍 Validaciones Implementadas

- ✅ **nombre**: Mínimo 1 carácter, máximo 255
- ✅ **categoria**: Mínimo 1 carácter, máximo 100
- ✅ **cantidad**: Debe ser ≥ 0 (no puede ser negativa)
- ✅ **precioUnitario**: Debe ser > 0 (debe ser positivo)

## 📊 Estructura de la Base de Datos

```sql
CREATE TABLE item_inventario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX idx_categoria ON item_inventario(categoria);
CREATE INDEX idx_nombre ON item_inventario(nombre);
```

## 🎯 Puntos Clave para el Examen

1. **CRUD Completo** ✅
   - Create (POST)
   - Read (GET)
   - Update (PUT)
   - Delete (DELETE)

2. **Validaciones de Datos** ✅
   - Campos requeridos
   - Tipos de datos correctos
   - Restricciones de valores

3. **Consultas Avanzadas** ✅
   - Búsqueda por categoría
   - Filtros personalizados
   - Estadísticas

4. **Documentación** ✅
   - Swagger UI automático
   - Descripciones de endpoints
   - Ejemplos de uso

5. **Manejo de Errores** ✅
   - Códigos HTTP apropiados
   - Mensajes descriptivos

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL
```
Solución: Verifica que PostgreSQL esté corriendo y la URL sea correcta
```

### Error al crear item con cantidad negativa
```
Solución: La cantidad debe ser ≥ 0 por restricción de base de datos
```

### Error al crear item con precio 0
```
Solución: El precio debe ser > 0 por validación de Pydantic
```

## 📄 Licencia

Proyecto académico - Universidad Católica de Cuenca

## 👨‍💻 Autor

**YAGUACHI GALARZA DANIEL ALEJANDRO**  
Sistema de Gestión de Inventario - Examen Final

---


