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
        print(f"🔍 SUPABASE_URL: {'✅' if self.url else '❌'}")
        print(f"🔍 SUPABASE_KEY: {'✅' if self.key else '❌'}")
        print("=" * 50)
        
        if not self.url or not self.key:
            raise Exception("Faltan variables de entorno")
        
        # Creamos un cliente simple con requests
        self.supabase = self  # Para mantener compatibilidad
        print("✅ Cliente Supabase inicializado")
    
    def table(self, nombre):
        return SupabaseTable(self.url, self.key, nombre)


class SupabaseTable:
    def __init__(self, url, key, table_name):
        self.url = url.rstrip('/')
        self.key = key
        self.table_name = table_name
        self.filters = []
    
    def select(self, columns='*'):
        self.columns = columns
        return self
    
    def eq(self, column, value):
        self.filters.append(f"{column}=eq.{value}")
        return self
    
    def order(self, column, desc=False):
        self.order_by = f"{column}.{'desc' if desc else 'asc'}"
        return self
    
    def execute(self):
        # Construir URL
        endpoint = f"{self.url}/rest/v1/rpc/{self.table_name}"
        if hasattr(self, 'columns'):
            endpoint = f"{self.url}/rest/v1/{self.table_name}?select={self.columns}"
        else:
            endpoint = f"{self.url}/rest/v1/{self.table_name}"
        
        # Agregar filtros
        if self.filters:
            endpoint += "&" + "&".join(self.filters)
        
        # Agregar order
        if hasattr(self, 'order_by'):
            endpoint += f"&order={self.order_by}"
        
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        
        response = requests.get(endpoint, headers=headers)
        
        class Response:
            def __init__(self, data):
                self.data = data
        
        return Response(response.json() if response.status_code == 200 else [])
