from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import json
import uuid
import traceback
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
except ImportError:
    Database = None

app = Flask(__name__)
CORS(app)


# ============================================
# SERVIR ARCHIVOS ESTATICOS
# ============================================

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_html(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    return send_from_directory('.', filename)


# ============================================
# FUNCION AYUDANTE
# ============================================

def get_db():
    print("🟡 Llamando a get_db()")
    print(f"Database importado: {Database}")
    
    if Database:
        try:
            db = Database()
            print(f"🟡 db creada: {db}")
            if db and db.supabase:
                print(f"🟡 supabase existe: {bool(db.supabase)}")
            else:
                print("🟡 db.supabase es None")
            return db
        except Exception as e:
            print(f"❌ Error al crear Database: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print("❌ Database es None - no se pudo importar")
        return None


# ============================================
# API - REGISTRO
# ============================================

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not nombre or not email or not password:
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Minimo 6 caracteres'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('usuarios').select('id').eq('email', email).execute()
        if response.data:
            return jsonify({'success': False, 'message': 'Correo ya registrado'}), 400
        
        hashed = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        
        db.supabase.table('usuarios').insert({
            'id': user_id,
            'nombre': nombre,
            'email': email,
            'password_hash': hashed
        }).execute()
        
        return jsonify({'success': True, 'usuario_id': user_id})
    except Exception as e:
        print(f"ERROR REGISTRO: {e}")
        return jsonify({'success': False, 'message': 'Error al registrar'}), 500


# ============================================
# API - LOGIN
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('usuarios').select('id, nombre, password_hash').eq('email', email).execute()
        user = response.data[0] if response.data else None
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401
        
        return jsonify({'success': True, 'usuario_id': str(user['id']), 'nombre': user['nombre']})
    except Exception as e:
        print(f"ERROR LOGIN: {e}")
        return jsonify({'success': False, 'message': 'Error al iniciar sesion'}), 500


# ============================================
# API - TEMAS
# ============================================

@app.route('/api/temas', methods=['GET'])
def obtener_temas():
    print("🔵 Llamada a /api/temas")
    db = get_db()
    print(f"db obtenida: {db}")
    print(f"supabase: {db.supabase if db else 'NO DB'}")
    
    if not db:
        print("❌ db es None")
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        print("🔄 Consultando tabla 'temas'...")
        response = db.supabase.table('temas').select('*').order('orden').execute()
        print(f"✅ Respuesta: {len(response.data)} temas encontrados")
        return jsonify({'success': True, 'temas': response.data})
    except Exception as e:
        print(f"❌ ERROR EN TEMAS: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# API - SUBTEMAS
# ============================================

@app.route('/api/temas/<int:tema_id>/subtemas', methods=['GET'])
def obtener_subtemas(tema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('subtemas').select('*').eq('tema_id', tema_id).order('orden').execute()
        return jsonify({'success': True, 'subtemas': response.data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# API - CONTENIDO
# ============================================

@app.route('/api/contenido/<int:subtema_id>', methods=['GET'])
def obtener_contenido(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        subtemas = db.supabase.table('subtemas').select('*, temas(nombre)').eq('id', subtema_id).execute()
        subtema = subtemas.data[0] if subtemas.data else None
        
        contenidos = db.supabase.table('contenido').select('*').eq('subtema_id', subtema_id).order('orden').execute()
        
        usuario_id = request.args.get('usuario_id')
        leido = False
        if usuario_id:
            prog_response = db.supabase.table('progreso').select('leido').eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
            prog = prog_response.data[0] if prog_response.data else None
            leido = prog['leido'] if prog else False
        
        if not subtema:
            return jsonify({'success': False, 'message': 'Subtema no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'subtema': subtema,
            'contenido': contenidos.data,
            'leido': leido
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# API - FLASHCARDS
# ============================================

@app.route('/api/flashcards/<int:subtema_id>', methods=['GET'])
def obtener_flashcards(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        tema_response = db.supabase.table('subtemas').select('nombre').eq('id', subtema_id).execute()
        tema_info = tema_response.data[0] if tema_response.data else None
        
        response = db.supabase.table('flashcards').select('*').eq('subtema_id', subtema_id).eq('estado', 'aprobada').order('es_oficial', desc=True).execute()
        
        return jsonify({
            'success': True,
            'flashcards': response.data,
            'tema_nombre': tema_info['nombre'] if tema_info else '',
            'total': len(response.data)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flashcards/crear', methods=['POST'])
def crear_flashcard():
    data = request.get_json()
    subtema_id = data.get('subtema_id')
    pregunta = data.get('pregunta', '').strip()
    respuesta = data.get('respuesta', '').strip()
    usuario_id = data.get('usuario_id')
    
    if not subtema_id or not pregunta or not respuesta:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        es_oficial = not usuario_id
        
        db.supabase.table('flashcards').insert({
            'subtema_id': subtema_id,
            'pregunta': pregunta,
            'respuesta': respuesta,
            'es_oficial': es_oficial,
            'creado_por': usuario_id if usuario_id else None,
            'estado': 'aprobada' if es_oficial else 'pendiente'
        }).execute()
        
        return jsonify({'success': True, 'message': 'Flashcard creada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flashcards/estudiar', methods=['POST'])
def estudiar_flashcard():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    flashcard_id = data.get('flashcard_id')
    la_sabe = data.get('la_sabe')
    
    if not usuario_id or not flashcard_id:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        existing = db.supabase.table('estudio_flashcards').select('id').eq('usuario_id', usuario_id).eq('flashcard_id', flashcard_id).execute()
        
        if existing.data:
            db.supabase.table('estudio_flashcards').update({
                'la_sabe': la_sabe,
                'fecha_estudio': 'now()'
            }).eq('usuario_id', usuario_id).eq('flashcard_id', flashcard_id).execute()
        else:
            db.supabase.table('estudio_flashcards').insert({
                'usuario_id': usuario_id,
                'flashcard_id': flashcard_id,
                'la_sabe': la_sabe,
                'fecha_estudio': 'now()'
            }).execute()
        
        return jsonify({'success': True, 'message': 'Progreso guardado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flashcards/progreso/<int:subtema_id>', methods=['GET'])
def progreso_flashcards(subtema_id):
    usuario_id = request.args.get('usuario_id')
    
    if not usuario_id:
        return jsonify({'success': False, 'message': 'Usuario no identificado'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        flashcards_res = db.supabase.table('flashcards').select('id').eq('subtema_id', subtema_id).eq('estado', 'aprobada').execute()
        total = len(flashcards_res.data)
        
        estudiadas_res = db.supabase.table('estudio_flashcards').select('flashcard_id, la_sabe').eq('usuario_id', usuario_id).execute()
        
        estudiadas = len(estudiadas_res.data)
        sabe = sum(1 for e in estudiadas_res.data if e.get('la_sabe') == True)
        
        porcentaje = (estudiadas / total * 100) if total > 0 else 0
        
        return jsonify({
            'success': True,
            'total': total,
            'estudiadas': estudiadas,
            'sabe': sabe,
            'porcentaje': round(porcentaje, 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# API - EXAMENES
# ============================================

@app.route('/api/examen/<int:subtema_id>', methods=['GET'])
def obtener_examen(subtema_id):
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        response = db.supabase.table('examenes').select('*').eq('subtema_id', subtema_id).execute()
        preguntas = response.data
        
        for p in preguntas:
            if p.get('opciones'):
                try:
                    p['opciones'] = json.loads(p['opciones'])
                except:
                    p['opciones'] = []
            else:
                p['opciones'] = None
        
        return jsonify({'success': True, 'preguntas': preguntas, 'total': len(preguntas)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/examen/guardar-resultado', methods=['POST'])
def guardar_resultado():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    subtema_id = data.get('subtema_id')
    aciertos = data.get('aciertos')
    total = data.get('total')
    
    if not all([usuario_id, subtema_id, aciertos is not None, total]):
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        db.supabase.table('resultados_examenes').insert({
            'usuario_id': usuario_id,
            'subtema_id': subtema_id,
            'aciertos': aciertos,
            'total': total,
            'porcentaje': (aciertos / total) * 100
        }).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# API - PROGRESO DE LECTURA
# ============================================

@app.route('/api/progreso/<int:subtema_id>/marcar-leido', methods=['POST'])
def marcar_leido(subtema_id):
    data = request.get_json() or {}
    usuario_id = data.get('usuario_id')
    
    if not usuario_id:
        return jsonify({'success': False, 'message': 'Usuario no identificado'}), 401
    
    db = get_db()
    if not db:
        return jsonify({'success': False, 'message': 'Error de conexion'}), 500
    
    try:
        existe_response = db.supabase.table('progreso').select('id').eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
        existe = existe_response.data[0] if existe_response.data else None
        
        if existe:
            db.supabase.table('progreso').update({
                'leido': True,
                'ultimo_acceso': 'now()'
            }).eq('usuario_id', usuario_id).eq('subtema_id', subtema_id).execute()
        else:
            db.supabase.table('progreso').insert({
                'usuario_id': usuario_id,
                'subtema_id': subtema_id,
                'leido': True
            }).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/progreso/general', methods=['GET'])
def progreso_general():
    return jsonify({'temas_leidos': 0, 'total_temas': 0, 'porcentaje': 0, 'detalle': []})


# ============================================
# API - CHATBOT CON GROQ
# ============================================

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_con_groq():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        mensaje = data.get('mensaje', '')
        contexto = data.get('contexto', {})
        
        if not mensaje:
            return jsonify({'success': False, 'message': 'Mensaje vacío'}), 400
        
        if not GROQ_API_KEY:
            return jsonify({'success': False, 'message': 'API Key de Groq no configurada'}), 500
        
        prompt = f"""Eres un tutor de física para estudiantes de secundaria.
        
Contexto actual:
- Pregunta de la flashcard: {contexto.get('pregunta', 'Ninguna')}
- Respuesta de la flashcard: {contexto.get('respuesta', 'Ninguna')}

Pregunta del estudiante: {mensaje}

Responde en español, de manera clara, educativa y amigable. Sé conciso pero completo."""
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': [
                    {'role': 'system', 'content': 'Eres un tutor experto en física. Responde SIEMPRE en español.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            resultado = response.json()
            respuesta = resultado['choices'][0]['message']['content']
            return jsonify({'success': True, 'respuesta': respuesta})
        else:
            return jsonify({'success': False, 'message': f'Error API: {response.status_code}'}), 500
            
    except Exception as e:
        print(f"ERROR CHAT: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
