// ============================================
// FLASHCARDS.JS - Estudiar con flashcards
// ============================================

const urlParams = new URLSearchParams(window.location.search);
const subtemaId = urlParams.get('subtema');
const modoTodos = urlParams.get('modo') === 'todos';
let cantidadDeseada = parseInt(urlParams.get('cantidad')) || 10;

if (cantidadDeseada < 5) cantidadDeseada = 5;
if (cantidadDeseada > 20) cantidadDeseada = 20;

let flashcardsOriginales = [];
let flashcards = [];
let indiceActual = 0;
let progreso = { estudiadas: 0, sabe: 0, total: 0 };
let usuarioId = localStorage.getItem('usuario_id');
let nombreSubtema = '';

document.addEventListener('DOMContentLoaded', async () => {
    console.log(`📊 Estudiando ${cantidadDeseada} flashcards`);
    
    if (!subtemaId && !modoTodos) {
        window.location.href = '/elegir-flashcards.html';
        return;
    }

    if (modoTodos) {
        await cargarTodasFlashcards();
    } else {
        await cargarFlashcards();
    }

    await cargarProgreso();
});

async function cargarFlashcards() {
    try {
        const res = await fetch(`/api/flashcards/${subtemaId}`);
        const data = await res.json();

        if (!data.success) {
            mostrarError(data.message);
            return;
        }

        flashcardsOriginales = data.flashcards;
        nombreSubtema = data.tema_nombre || 'Flashcards';

        document.getElementById('nav-info').innerHTML = `
            <span class="progreso-tag">📚 ${nombreSubtema}</span>
        `;

        if (flashcardsOriginales.length === 0) {
            mostrarSinFlashcards();
            return;
        }

        seleccionarFlashcardsPorCantidad();

    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error al cargar flashcards');
    }
}

function seleccionarFlashcardsPorCantidad() {
    let totalDisponibles = flashcardsOriginales.length;
    let cantidadEstudiar = Math.min(cantidadDeseada, totalDisponibles);
    
    const mezcladas = [...flashcardsOriginales];
    for (let i = mezcladas.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [mezcladas[i], mezcladas[j]] = [mezcladas[j], mezcladas[i]];
    }
    
    flashcards = mezcladas.slice(0, cantidadEstudiar);
    mostrarInfoCantidad(totalDisponibles, flashcards.length);
    
    if (flashcards.length === 0) {
        mostrarSinFlashcards();
        return;
    }
    
    mostrarFlashcard(0);
}

function mostrarInfoCantidad(totalDisponibles, seleccionadas) {
    const infoDiv = document.createElement('div');
    infoDiv.className = 'info-cantidad';
    infoDiv.style.cssText = `
        background: rgba(255,255,255,0.15);
        padding: 12px 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
        color: white;
        font-size: 0.9rem;
    `;
    
    if (totalDisponibles > cantidadDeseada) {
        infoDiv.innerHTML = `🎲 Estudiando <strong>${seleccionadas}</strong> de <strong>${totalDisponibles}</strong> flashcards disponibles. Selección aleatoria.`;
    } else if (totalDisponibles < cantidadDeseada) {
        infoDiv.innerHTML = `📚 Solo hay <strong>${totalDisponibles}</strong> flashcards disponibles (pediste ${cantidadDeseada}).`;
    } else {
        infoDiv.innerHTML = `📚 Estudiando todas las <strong>${totalDisponibles}</strong> flashcards disponibles.`;
    }
    
    const container = document.querySelector('.flashcards-container');
    const progresoPanel = document.getElementById('progreso-panel');
    container.insertBefore(infoDiv, progresoPanel);
    setTimeout(() => infoDiv.remove(), 5000);
}

async function cargarTodasFlashcards() {
    try {
        const resTemas = await fetch('/api/temas/1/subtemas');
        const dataTemas = await resTemas.json();

        if (!dataTemas.success) {
            mostrarError('Error cargando temas');
            return;
        }

        const todas = [];
        for (const subtema of dataTemas.subtemas) {
            try {
                const res = await fetch(`/api/flashcards/${subtema.id}`);
                const data = await res.json();
                if (data.success && data.flashcards) {
                    todas.push(...data.flashcards);
                }
            } catch (e) {
                console.error(`Error cargando subtema ${subtema.id}:`, e);
            }
        }

        flashcardsOriginales = todas;
        nombreSubtema = 'Todos los temas';

        document.getElementById('nav-info').innerHTML = `
            <span class="progreso-tag">🎯 Todos los temas</span>
        `;

        if (flashcardsOriginales.length === 0) {
            mostrarSinFlashcards();
            return;
        }

        seleccionarFlashcardsPorCantidad();

    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error al cargar flashcards');
    }
}

function mostrarFlashcard(indice) {
    if (indice < 0 || indice >= flashcards.length) return;

    indiceActual = indice;
    const f = flashcards[indice];

    document.getElementById('tarjeta').classList.remove('girada');

    document.getElementById('tarjeta-numero').textContent = `${indice + 1} / ${flashcards.length}`;
    document.getElementById('tarjeta-pregunta').textContent = f.pregunta;
    document.getElementById('tarjeta-respuesta').textContent = f.respuesta;

    document.getElementById('btn-anterior').disabled = indice === 0;
    document.getElementById('btn-siguiente').disabled = indice === flashcards.length - 1;
}

function girarTarjeta() {
    document.getElementById('tarjeta').classList.toggle('girada');
}

function anteriorFlashcard() {
    if (indiceActual > 0) {
        mostrarFlashcard(indiceActual - 1);
    }
}

function siguienteFlashcard() {
    if (indiceActual < flashcards.length - 1) {
        mostrarFlashcard(indiceActual + 1);
    }
}

async function evaluarFlashcard(laSabe) {
    if (!usuarioId) {
        alert('Debes iniciar sesión para guardar tu progreso');
        return;
    }

    const flashcardId = flashcards[indiceActual].id;

    try {
        const res = await fetch('/api/flashcards/estudiar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                usuario_id: usuarioId,
                flashcard_id: flashcardId,
                la_sabe: laSabe
            })
        });

        const data = await res.json();

        if (data.success) {
            const btn = laSabe ? document.querySelector('.btn-sabe') : document.querySelector('.btn-repasar');
            btn.style.transform = 'scale(1.1)';
            setTimeout(() => btn.style.transform = '', 200);

            await cargarProgreso();

            if (indiceActual < flashcards.length - 1) {
                setTimeout(() => siguienteFlashcard(), 300);
            } else {
                mostrarCompletado();
            }
        } else {
            alert('Error al guardar: ' + data.message);
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión al guardar progreso');
    }
}

async function cargarProgreso() {
    if (!usuarioId || (!subtemaId && !modoTodos)) return;

    try {
        let url;
        if (modoTodos) {
            url = `/api/flashcards/progreso/todos?usuario_id=${usuarioId}`;
            const res = await fetch(url);
            const data = await res.json();
            if (data.success) {
                progreso = data;
                actualizarBarraProgreso();
            }
        } else {
            url = `/api/flashcards/progreso/${subtemaId}?usuario_id=${usuarioId}`;
            const res = await fetch(url);
            const data = await res.json();
            if (data.success) {
                progreso = data;
                actualizarBarraProgreso();
            }
        }
    } catch (error) {
        console.error('Error progreso:', error);
    }
}

function actualizarBarraProgreso() {
    const fill = document.getElementById('progreso-fill');
    const texto = document.getElementById('progreso-texto');

    const porcentaje = progreso.porcentaje || 0;
    fill.style.width = `${porcentaje}%`;
    texto.textContent = `${porcentaje}% completado (${progreso.estudiadas || 0}/${progreso.total || flashcards.length})`;
}

function mostrarCompletado() {
    const modal = document.getElementById('modal-completado');
    const stats = document.getElementById('modal-stats');
    const btnExamen = document.getElementById('btn-examen');

    stats.innerHTML = `
        <p>📚 Flashcards estudiadas: ${flashcards.length}</p>
        <p>✅ Que sabes: ${progreso.sabe || 0}</p>
        <p>📖 Dominio: ${Math.round(((progreso.sabe || 0) / flashcards.length) * 100)}%</p>
    `;

    const porcentaje = ((progreso.sabe || 0) / flashcards.length) * 100;
    if (porcentaje >= 70) {
        btnExamen.style.display = 'inline-block';
    } else {
        btnExamen.style.display = 'none';
        stats.innerHTML += `<p style="color: #dc2626; margin-top: 12px;">Necesitas estudiar más para hacer el examen (mínimo 70%)</p>`;
    }

    modal.classList.remove('hidden');
}

function cerrarModal() {
    document.getElementById('modal-completado').classList.add('hidden');
    window.location.href = '/elegir-flashcards.html';
}

function irAExamen() {
    if (subtemaId) {
        window.location.href = `/examen.html?subtema=${subtemaId}`;
    } else {
        window.location.href = '/elegir-flashcards.html';
    }
}

function mostrarFormularioCrear() {
    if (!usuarioId) {
        alert('Debes iniciar sesión para crear flashcards');
        return;
    }
    document.getElementById('formulario-crear').classList.remove('hidden');
}

function ocultarFormularioCrear() {
    document.getElementById('formulario-crear').classList.add('hidden');
    document.getElementById('nueva-pregunta').value = '';
    document.getElementById('nueva-respuesta').value = '';
    document.getElementById('mensaje-validacion').textContent = '';
}

async function crearFlashcard() {
    const pregunta = document.getElementById('nueva-pregunta').value.trim();
    const respuesta = document.getElementById('nueva-respuesta').value.trim();
    const mensajeDiv = document.getElementById('mensaje-validacion');

    if (!pregunta || !respuesta) {
        mensajeDiv.textContent = 'Escribe la pregunta y la respuesta';
        return;
    }

    try {
        const res = await fetch('/api/flashcards/crear', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subtema_id: parseInt(subtemaId),
                pregunta: pregunta,
                respuesta: respuesta,
                usuario_id: usuarioId
            })
        });

        const data = await res.json();

        if (data.success) {
            alert('✅ Flashcard creada exitosamente');
            ocultarFormularioCrear();
            await cargarFlashcards();
        } else {
            mensajeDiv.textContent = data.message;
        }

    } catch (error) {
        console.error('Error:', error);
        mensajeDiv.textContent = 'Error de conexión';
    }
}

function mostrarSinFlashcards() {
    const wrapper = document.querySelector('.tarjeta-wrapper');
    if (wrapper) {
        wrapper.innerHTML = `
            <div style="text-align: center; padding: 60px; color: white;">
                <h2>📭 No hay flashcards</h2>
                <p style="margin: 16px 0;">Sé el primero en crear una</p>
                <button onclick="mostrarFormularioCrear()" class="btn-crear" style="margin-top: 20px;">
                    ➕ Crear flashcard
                </button>
            </div>
        `;
    }
    const evaluacion = document.getElementById('evaluacion-botones');
    const navegacion = document.querySelector('.navegacion-botones');
    const progreso = document.getElementById('progreso-panel');
    if (evaluacion) evaluacion.style.display = 'none';
    if (navegacion) navegacion.style.display = 'none';
    if (progreso) progreso.style.display = 'none';
}

function mostrarError(mensaje) {
    const container = document.querySelector('.flashcards-container');
    if (container) {
        container.innerHTML = `
            <div style="text-align: center; padding: 100px 20px; color: white;">
                <h2>😕 ${mensaje}</h2>
                <a href="/elegir-flashcards.html" style="color: #86efac; margin-top: 20px; display: inline-block;">
                    ← Elegir otro tema
                </a>
            </div>
        `;
    }
}

// ============================================
// CHATBOT GROQ - CON PUERTO 5001
// ============================================

function toggleChatbot() {
    const window = document.getElementById('chatbot-window');
    window.classList.toggle('hidden');
    if (!window.classList.contains('hidden')) {
        document.getElementById('chatbot-input').focus();
    }
}

function handleChatbotKeyPress(event) {
    if (event.key === 'Enter') {
        enviarMensaje();
    }
}

async function enviarMensaje() {
    const input = document.getElementById('chatbot-input');
    const mensaje = input.value.trim();
    
    if (!mensaje) return;
    
    agregarMensaje(mensaje, 'user');
    input.value = '';
    
    const preguntaActual = document.getElementById('tarjeta-pregunta').textContent;
    const respuestaActual = document.getElementById('tarjeta-respuesta').textContent;
    
    const loadingId = mostrarLoading();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mensaje: mensaje,
                contexto: {
                    pregunta: preguntaActual,
                    respuesta: respuestaActual
                }
            })
        });
        
        const data = await response.json();
        removerLoading(loadingId);
        
        if (data.success) {
            agregarMensaje(data.respuesta, 'bot');
        } else {
            agregarMensaje('Lo siento, hubo un error: ' + (data.message || 'desconocido'), 'bot');
        }
    } catch (error) {
        removerLoading(loadingId);
        console.error('Error de conexión:', error);
        agregarMensaje('⚠️ Error de conexión con el chatbot. Intenta de nuevo.', 'bot');
    }
}

function agregarMensaje(texto, tipo) {
    const messagesDiv = document.getElementById('chatbot-messages');
    const mensajeDiv = document.createElement('div');
    mensajeDiv.className = `chatbot-message ${tipo}`;
    
    let textoFormateado = texto.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    textoFormateado = textoFormateado.replace(/\n/g, '<br>');
    
    mensajeDiv.innerHTML = `<div class="message-content">${textoFormateado}</div>`;
    messagesDiv.appendChild(mensajeDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function mostrarLoading() {
    const messagesDiv = document.getElementById('chatbot-messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chatbot-message bot';
    loadingDiv.id = 'loading-' + Date.now();
    loadingDiv.innerHTML = `<div class="message-content">🤔 Pensando...</div>`;
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return loadingDiv.id;
}

function removerLoading(id) {
    const loading = document.getElementById(id);
    if (loading) loading.remove();
}

function preguntarSobreFlashcard() {
    const pregunta = document.getElementById('tarjeta-pregunta').textContent;
    const input = document.getElementById('chatbot-input');
    input.value = `¿Puedes explicarme más sobre: "${pregunta}"?`;
    enviarMensaje();
    if (document.getElementById('chatbot-window').classList.contains('hidden')) {
        toggleChatbot();
    }
}