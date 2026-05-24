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
        
        # DEBUG: Imprimir para ver si llegan las variables
        print("=" * 50)
        print("🔍 DEBUG - Conexión a Supabase")
        print(f"SUPABASE_URL existe: {bool(url)}")
        print(f"SUPABASE_KEY existe: {bool(key)}")
        print(f"SUPABASE_URL valor: {url[:50] if url else 'NO EXISTE'}...")
        print("=" * 50)
        
        if not url or not key:
            raise Exception("❌ Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")
        
        try:
            self.supabase = create_client(url, key)
            print("✅ Supabase conectado exitosamente")
        except Exception as e:
            print(f"❌ Error al conectar a Supabase: {e}")
            raise
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
