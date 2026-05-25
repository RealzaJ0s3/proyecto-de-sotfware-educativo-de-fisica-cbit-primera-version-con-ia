import os
import requests

class Database:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        print("=" * 50)
        print("🔍 Inicializando conexión a Supabase")
        print(f"SUPABASE_URL: {'✅' if self.url else '❌ NO EXISTE'}")
        print(f"SUPABASE_KEY: {'✅' if self.key else '❌ NO EXISTE'}")
        
        if not self.url or not self.key:
            raise Exception("❌ Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")
        
        # Guardamos referencia para usar en los métodos
        self.supabase = self
        print("✅ Cliente Supabase inicializado correctamente")
        print("=" * 50)
    
    def table(self, nombre):
        """Retorna un objeto para consultar una tabla"""
        return SupabaseTable(self.url, self.key, nombre)


class SupabaseTable:
    def __init__(self, url, key, table_name):
        self.url = url.rstrip('/')
        self.key = key
        self.table_name = table_name
        self.select_columns = '*'
        self.filters = []
        self.order_column = None
        self.order_direction = 'asc'
    
    def select(self, columns):
        """Especifica qué columnas seleccionar"""
        self.select_columns = columns
        return self
    
    def eq(self, column, value):
        """Agrega filtro de igualdad"""
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def order(self, column, desc=False):
        """Agrega ordenamiento"""
        self.order_column = column
        self.order_direction = 'desc' if desc else 'asc'
        return self
    
    def execute(self):
        """Ejecuta la consulta y retorna los resultados"""
        # Construir URL base
        endpoint = f"{self.url}/rest/v1/{self.table_name}?select={self.select_columns}"
        
        # Agregar filtros
        if self.filters:
            endpoint += "&" + "&".join(self.filters)
        
        # Agregar ordenamiento
        if self.order_column:
            endpoint += f"&order={self.order_column}.{self.order_direction}"
        
        # Headers de autenticación
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        print(f"🔄 Consultando: {endpoint}")
        
        response = requests.get(endpoint, headers=headers)
        
        # Crear objeto de respuesta compatible con el código existente
        class Response:
            def __init__(self, data):
                self.data = data
        
        if response.status_code == 200:
            return Response(response.json())
        else:
            print(f"❌ Error en consulta: {response.status_code} - {response.text}")
            return Response([])
    
    def insert(self, data):
        """Inserta un nuevo registro"""
        endpoint = f"{self.url}/rest/v1/{self.table_name}"
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        class Response:
            def __init__(self, data):
                self.data = data
        
        if response.status_code in [200, 201]:
            return Response(response.json() if response.text else [])
        else:
            print(f"❌ Error en insert: {response.status_code} - {response.text}")
            return Response([])
    
    def update(self, data):
        """Actualiza registros (requiere filtros previos con eq())"""
        if not self.filters:
            raise Exception("Se requiere un filtro (eq) para actualizar")
        
        endpoint = f"{self.url}/rest/v1/{self.table_name}"
        
        # Agregar filtros a la URL
        if self.filters:
            endpoint += "?" + "&".join(self.filters)
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        response = requests.patch(endpoint, headers=headers, json=data)
        
        class Response:
            def __init__(self, data):
                self.data = data
        
        if response.status_code in [200, 204]:
            return Response(response.json() if response.text else [])
        else:
            print(f"❌ Error en update: {response.status_code} - {response.text}")
            return Response([])
    
    def delete(self):
        """Elimina registros (requiere filtros previos con eq())"""
        if not self.filters:
            raise Exception("Se requiere un filtro (eq) para eliminar")
        
        endpoint = f"{self.url}/rest/v1/{self.table_name}?" + "&".join(self.filters)
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        response = requests.delete(endpoint, headers=headers)
        
        class Response:
            def __init__(self, data):
                self.data = data
        
        return Response([])
