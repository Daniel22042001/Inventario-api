from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
from decimal import Decimal

app = FastAPI(
    title="Sistema de Gestión de Inventario",
    description="API REST para gestión de items de inventario - YAGUACHI GALARZA DANIEL ALEJANDRO",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/inventario_db")

# Convertir formato Railway si es necesario
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

@contextmanager
def get_db_connection():
    """Context manager para manejar conexiones a la base de datos"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Modelos Pydantic
class ItemInventarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del item")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoría del item")
    cantidad: int = Field(..., ge=0, description="Cantidad en inventario (debe ser mayor o igual a 0)")
    precioUnitario: float = Field(..., gt=0, description="Precio unitario del item (debe ser mayor a 0)")

class ItemInventarioCreate(ItemInventarioBase):
    """Modelo para crear un nuevo item de inventario"""
    pass

class ItemInventarioUpdate(BaseModel):
    """Modelo para actualizar un item de inventario (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    cantidad: Optional[int] = Field(None, ge=0)
    precioUnitario: Optional[float] = Field(None, gt=0)

class ItemInventario(ItemInventarioBase):
    """Modelo completo del item de inventario con ID"""
    id: int

    class Config:
        from_attributes = True

# Inicializar base de datos
@app.on_event("startup")
async def startup():
    """Crear tabla de items de inventario si no existe"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS item_inventario (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    categoria VARCHAR(100) NOT NULL,
                    cantidad INTEGER NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
                    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario > 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Crear índices para mejorar el rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_categoria ON item_inventario(categoria);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nombre ON item_inventario(nombre);
            """)
            
            cursor.close()
            print("✅ Base de datos inicializada correctamente")
            print("✅ Tabla 'item_inventario' creada/verificada")
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo conectar a la base de datos: {e}")
        print("⚠️  Asegúrate de agregar PostgreSQL en Railway")

# ==================== ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz - Información del sistema
    """
    return {
        "sistema": "Sistema de Gestión de Inventario",
        "estudiante": "YAGUACHI GALARZA DANIEL ALEJANDRO",
        "version": "1.0.0",
        "entidad": "ItemInventario",
        "endpoints": {
            "documentacion": "/docs",
            "health_check": "/health",
            "listar_items": "GET /api/inventario",
            "obtener_item": "GET /api/inventario/{id}",
            "crear_item": "POST /api/inventario",
            "actualizar_item": "PUT /api/inventario/{id}",
            "eliminar_item": "DELETE /api/inventario/{id}",
            "buscar_por_categoria": "GET /api/inventario/categoria/{categoria}",
            "items_bajo_stock": "GET /api/inventario/bajo-stock/{cantidad}",
            "valor_total_inventario": "GET /api/inventario/estadisticas/valor-total"
        }
    }

@app.get("/health", tags=["Health"])
@app.head("/health", tags=["Health"])
async def health_check():
    """
    Health check - Verificar estado de la API y base de datos
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM item_inventario")
            count = cursor.fetchone()[0]
            cursor.close()
        return {
            "status": "healthy",
            "database": "connected",
            "total_items": count
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@app.get("/api/inventario", response_model=List[ItemInventario], tags=["Inventario - CRUD"])
async def listar_items():
    """
    Listar todos los items del inventario
    
    Retorna una lista completa de todos los items registrados en el sistema.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nombre, categoria, cantidad, 
                   precio_unitario as "precioUnitario"
            FROM item_inventario 
            ORDER BY id
        """)
        items = cursor.fetchall()
        cursor.close()
    return items

@app.get("/api/inventario/{item_id}", response_model=ItemInventario, tags=["Inventario - CRUD"])
async def obtener_item(item_id: int):
    """
    Obtener un item específico por su ID
    
    - **item_id**: ID del item a buscar
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nombre, categoria, cantidad, 
                   precio_unitario as "precioUnitario"
            FROM item_inventario 
            WHERE id = %s
        """, (item_id,))
        item = cursor.fetchone()
        cursor.close()
    
    if not item:
        raise HTTPException(
            status_code=404, 
            detail=f"Item con ID {item_id} no encontrado en el inventario"
        )
    return item

@app.post("/api/inventario", response_model=ItemInventario, status_code=201, tags=["Inventario - CRUD"])
async def crear_item(item: ItemInventarioCreate):
    """
    Crear un nuevo item en el inventario
    
    - **nombre**: Nombre del item (requerido)
    - **categoria**: Categoría del item (requerido)
    - **cantidad**: Cantidad en inventario (≥ 0)
    - **precioUnitario**: Precio unitario (> 0)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO item_inventario (nombre, categoria, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
            RETURNING id, nombre, categoria, cantidad, 
                      precio_unitario as "precioUnitario"
        """, (item.nombre, item.categoria, item.cantidad, item.precioUnitario))
        nuevo_item = cursor.fetchone()
        cursor.close()
    return nuevo_item

@app.put("/api/inventario/{item_id}", response_model=ItemInventario, tags=["Inventario - CRUD"])
async def actualizar_item(item_id: int, item: ItemInventarioUpdate):
    """
    Actualizar un item existente en el inventario
    
    - **item_id**: ID del item a actualizar
    - Todos los campos son opcionales, solo se actualizarán los campos proporcionados
    """
    # Verificar si el item existe
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id FROM item_inventario WHERE id = %s", (item_id,))
        if not cursor.fetchone():
            cursor.close()
            raise HTTPException(
                status_code=404, 
                detail=f"Item con ID {item_id} no encontrado en el inventario"
            )
        
        # Construir query de actualización dinámicamente
        update_fields = []
        values = []
        
        if item.nombre is not None:
            update_fields.append("nombre = %s")
            values.append(item.nombre)
        if item.categoria is not None:
            update_fields.append("categoria = %s")
            values.append(item.categoria)
        if item.cantidad is not None:
            update_fields.append("cantidad = %s")
            values.append(item.cantidad)
        if item.precioUnitario is not None:
            update_fields.append("precio_unitario = %s")
            values.append(item.precioUnitario)
        
        if not update_fields:
            raise HTTPException(
                status_code=400, 
                detail="No se proporcionaron campos para actualizar"
            )
        
        # Agregar timestamp de actualización
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(item_id)
        
        query = f"""
            UPDATE item_inventario 
            SET {', '.join(update_fields)} 
            WHERE id = %s 
            RETURNING id, nombre, categoria, cantidad, 
                      precio_unitario as "precioUnitario"
        """
        
        cursor.execute(query, values)
        item_actualizado = cursor.fetchone()
        cursor.close()
    
    return item_actualizado

@app.delete("/api/inventario/{item_id}", tags=["Inventario - CRUD"])
async def eliminar_item(item_id: int):
    """
    Eliminar un item del inventario
    
    - **item_id**: ID del item a eliminar
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            DELETE FROM item_inventario 
            WHERE id = %s 
            RETURNING id, nombre
        """, (item_id,))
        item_eliminado = cursor.fetchone()
        cursor.close()
    
    if not item_eliminado:
        raise HTTPException(
            status_code=404, 
            detail=f"Item con ID {item_id} no encontrado en el inventario"
        )
    
    return {
        "message": "Item eliminado exitosamente del inventario",
        "id": item_eliminado["id"],
        "nombre": item_eliminado["nombre"]
    }

# ==================== ENDPOINTS ADICIONALES ====================

@app.get("/api/inventario/categoria/{categoria}", response_model=List[ItemInventario], tags=["Consultas Avanzadas"])
async def buscar_por_categoria(categoria: str):
    """
    Buscar items por categoría
    
    - **categoria**: Categoría a buscar (búsqueda exacta, no sensible a mayúsculas)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nombre, categoria, cantidad, 
                   precio_unitario as "precioUnitario"
            FROM item_inventario 
            WHERE LOWER(categoria) = LOWER(%s)
            ORDER BY nombre
        """, (categoria,))
        items = cursor.fetchall()
        cursor.close()
    
    if not items:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron items en la categoría '{categoria}'"
        )
    
    return items

@app.get("/api/inventario/bajo-stock/{cantidad_minima}", response_model=List[ItemInventario], tags=["Consultas Avanzadas"])
async def items_bajo_stock(cantidad_minima: int):
    """
    Obtener items con stock bajo
    
    - **cantidad_minima**: Cantidad mínima para considerar como "bajo stock"
    
    Retorna todos los items cuya cantidad sea menor o igual al valor especificado.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, nombre, categoria, cantidad, 
                   precio_unitario as "precioUnitario"
            FROM item_inventario 
            WHERE cantidad <= %s
            ORDER BY cantidad ASC, nombre
        """, (cantidad_minima,))
        items = cursor.fetchall()
        cursor.close()
    
    return items

@app.get("/api/inventario/estadisticas/valor-total", tags=["Estadísticas"])
async def valor_total_inventario():
    """
    Calcular el valor total del inventario
    
    Retorna el valor total calculado como: suma(cantidad × precioUnitario)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                SUM(cantidad) as total_unidades,
                SUM(cantidad * precio_unitario) as valor_total_inventario,
                AVG(precio_unitario) as precio_promedio
            FROM item_inventario
        """)
        estadisticas = cursor.fetchone()
        cursor.close()
    
    return {
        "total_items_diferentes": estadisticas["total_items"],
        "total_unidades": estadisticas["total_unidades"] or 0,
        "valor_total_inventario": float(estadisticas["valor_total_inventario"] or 0),
        "precio_promedio": float(estadisticas["precio_promedio"] or 0)
    }

@app.get("/api/inventario/estadisticas/por-categoria", tags=["Estadísticas"])
async def estadisticas_por_categoria():
    """
    Obtener estadísticas agrupadas por categoría
    
    Retorna cantidad de items, total de unidades y valor por cada categoría.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                categoria,
                COUNT(*) as total_items,
                SUM(cantidad) as total_unidades,
                SUM(cantidad * precio_unitario) as valor_categoria
            FROM item_inventario
            GROUP BY categoria
            ORDER BY valor_categoria DESC
        """)
        estadisticas = cursor.fetchall()
        cursor.close()
    
    return [
        {
            "categoria": stat["categoria"],
            "total_items": stat["total_items"],
            "total_unidades": stat["total_unidades"],
            "valor_categoria": float(stat["valor_categoria"] or 0)
        }
        for stat in estadisticas
    ]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
