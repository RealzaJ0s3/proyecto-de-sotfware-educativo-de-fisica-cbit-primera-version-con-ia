import os
from supabase import create_client

class Database:
    _instance = None
    supabase = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        # Debug: Imprimir si están configuradas
        print(f"SUPABASE_URL configurada: {bool(url)}")
        print(f"SUPABASE_KEY configurada: {bool(key)}")
        
        if not url or not key:
            raise Exception("Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")
        
        self.supabase = create_client(url, key)
        print("✅ Supabase conectado")
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
