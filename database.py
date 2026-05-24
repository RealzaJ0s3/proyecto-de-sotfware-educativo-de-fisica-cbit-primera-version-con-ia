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
        print("🟢 Inicializando Database...")
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        print(f"SUPABASE_URL: {'✅' if url else '❌ NO'}")
        print(f"SUPABASE_KEY: {'✅' if key else '❌ NO'}")
        
        if not url or not key:
            error_msg = "Faltan variables de entorno: "
            if not url:
                error_msg += "SUPABASE_URL "
            if not key:
                error_msg += "SUPABASE_KEY"
            raise Exception(error_msg)
        
        try:
            self.supabase = create_client(url, key)
            print("✅ Conexión a Supabase exitosa")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            raise
    
    def get_cursor(self):
        return None
    
    def execute_query(self, query, params=None):
        return None
    
    def close(self):
        pass
