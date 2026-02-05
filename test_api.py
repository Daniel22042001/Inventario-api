import requests
import json

# Configurar la URL base (cambia esto por tu URL de Railway cuando despliegues)
BASE_URL = "http://localhost:8000"

print("🧪 Probando Sistema de Gestión de Inventario")
print("=" * 60)
print()

# Test 1: Health Check
print("1️⃣ Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Asegúrate de que la API esté corriendo")
    exit(1)

# Test 2: Información del sistema
print("2️⃣ Información del sistema...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
data = response.json()
print(f"   Sistema: {data['sistema']}")
print(f"   Estudiante: {data['estudiante']}")
print()

# Test 3: Crear items de ejemplo
print("3️⃣ Creando items de inventario...")
items = [
    {
        "nombre": "Laptop Dell XPS 15",
        "categoria": "Tecnología",
        "cantidad": 25,
        "precioUnitario": 1299.99
    },
    {
        "nombre": "Mouse Logitech MX Master 3",
        "categoria": "Tecnología",
        "cantidad": 50,
        "precioUnitario": 99.99
    },
    {
        "nombre": "Teclado Mecánico Keychron K2",
        "categoria": "Tecnología",
        "cantidad": 35,
        "precioUnitario": 89.99
    },
    {
        "nombre": "Monitor LG 27 pulgadas",
        "categoria": "Tecnología",
        "cantidad": 15,
        "precioUnitario": 299.99
    },
    {
        "nombre": "Silla Ergonómica Herman Miller",
        "categoria": "Mobiliario",
        "cantidad": 10,
        "precioUnitario": 799.99
    },
    {
        "nombre": "Escritorio Adjustable",
        "categoria": "Mobiliario",
        "cantidad": 8,
        "precioUnitario": 449.99
    },
    {
        "nombre": "Lámpara LED Escritorio",
        "categoria": "Iluminación",
        "cantidad": 40,
        "precioUnitario": 29.99
    },
    {
        "nombre": "Audífonos Sony WH-1000XM5",
        "categoria": "Audio",
        "cantidad": 20,
        "precioUnitario": 349.99
    }
]

created_ids = []
for item in items:
    response = requests.post(f"{BASE_URL}/api/inventario", json=item)
    if response.status_code == 201:
        created_item = response.json()
        created_ids.append(created_item['id'])
        print(f"   ✅ Creado: {item['nombre']} (ID: {created_item['id']})")
    else:
        print(f"   ❌ Error creando: {item['nombre']}")

print()

# Test 4: Listar todos los items
print("4️⃣ Listando todos los items...")
response = requests.get(f"{BASE_URL}/api/inventario")
items = response.json()
print(f"   Total de items: {len(items)}")
print()

# Test 5: Obtener un item específico
print("5️⃣ Obteniendo item específico...")
if created_ids:
    item_id = created_ids[0]
    response = requests.get(f"{BASE_URL}/api/inventario/{item_id}")
    item = response.json()
    print(f"   ID: {item['id']}")
    print(f"   Nombre: {item['nombre']}")
    print(f"   Categoría: {item['categoria']}")
    print(f"   Cantidad: {item['cantidad']}")
    print(f"   Precio: ${item['precioUnitario']}")
print()

# Test 6: Buscar por categoría
print("6️⃣ Buscando items de categoría 'Tecnología'...")
response = requests.get(f"{BASE_URL}/api/inventario/categoria/Tecnología")
items_tech = response.json()
print(f"   Items encontrados: {len(items_tech)}")
for item in items_tech:
    print(f"   - {item['nombre']}: ${item['precioUnitario']}")
print()

# Test 7: Items con bajo stock
print("7️⃣ Items con stock menor o igual a 15...")
response = requests.get(f"{BASE_URL}/api/inventario/bajo-stock/15")
items_low = response.json()
print(f"   Items con bajo stock: {len(items_low)}")
for item in items_low:
    print(f"   ⚠️  {item['nombre']}: {item['cantidad']} unidades")
print()

# Test 8: Estadísticas - Valor total
print("8️⃣ Calculando valor total del inventario...")
response = requests.get(f"{BASE_URL}/api/inventario/estadisticas/valor-total")
stats = response.json()
print(f"   Items diferentes: {stats['total_items_diferentes']}")
print(f"   Total unidades: {stats['total_unidades']}")
print(f"   Valor total: ${stats['valor_total_inventario']:,.2f}")
print(f"   Precio promedio: ${stats['precio_promedio']:,.2f}")
print()

# Test 9: Estadísticas por categoría
print("9️⃣ Estadísticas por categoría...")
response = requests.get(f"{BASE_URL}/api/inventario/estadisticas/por-categoria")
cat_stats = response.json()
for cat in cat_stats:
    print(f"   📦 {cat['categoria']}:")
    print(f"      Items: {cat['total_items']}")
    print(f"      Unidades: {cat['total_unidades']}")
    print(f"      Valor: ${cat['valor_categoria']:,.2f}")
print()

# Test 10: Actualizar un item
print("🔟 Actualizando un item...")
if created_ids:
    item_id = created_ids[0]
    update_data = {
        "cantidad": 30,
        "precioUnitario": 1199.99
    }
    response = requests.put(f"{BASE_URL}/api/inventario/{item_id}", json=update_data)
    if response.status_code == 200:
        updated = response.json()
        print(f"   ✅ Actualizado: {updated['nombre']}")
        print(f"   Nueva cantidad: {updated['cantidad']}")
        print(f"   Nuevo precio: ${updated['precioUnitario']}")
print()

# Test 11: Eliminar un item
print("1️⃣1️⃣ Eliminando un item...")
if len(created_ids) > 1:
    item_id = created_ids[-1]
    response = requests.delete(f"{BASE_URL}/api/inventario/{item_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Eliminado: {result['nombre']} (ID: {result['id']})")
print()

# Resumen final
print("=" * 60)
print("✅ Pruebas completadas exitosamente!")
print()
print("📚 Documentación disponible en:")
print(f"   - Swagger UI: {BASE_URL}/docs")
print(f"   - ReDoc: {BASE_URL}/redoc")
print()
print("🎯 Sistema de Gestión de Inventario")
print("👨‍💻 YAGUACHI GALARZA DANIEL ALEJANDRO")
