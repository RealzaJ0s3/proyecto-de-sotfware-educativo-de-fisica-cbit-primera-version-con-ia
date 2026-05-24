// ============================================
// ELEGIR-FLASHCARDS.JS - Seleccionar tema a estudiar
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    await cargarSubtemas();
});

async function cargarSubtemas() {
    const grid = document.getElementById('temas-grid');
    const estudiarTodo = document.getElementById('estudiar-todo');

    const urlParams = new URLSearchParams(window.location.search);
    const temaId = urlParams.get('tema') || 1;

    try {
        const res = await fetch(`/api/temas/${temaId}/subtemas`);
        const data = await res.json();

        if (!data.success || !data.subtemas || data.subtemas.length === 0) {
            grid.innerHTML = `
                <div class="error-card">
                    <h3>😕 No hay subtemas disponibles</h3>
                    <p>No se encontraron temas para estudiar.</p>
                    <a href="/" style="color: #16a34a; margin-top: 16px; display: inline-block;">Volver al inicio</a>
                </div>
            `;
            return;
        }

        const subtemas = data.subtemas;

        const colores = [
            'linear-gradient(135deg, #16a34a, #22c55e)',
            'linear-gradient(135deg, #059669, #10b981)',
            'linear-gradient(135deg, #047857, #34d399)',
            'linear-gradient(135deg, #065f46, #6ee7b7)',
            'linear-gradient(135deg, #064e3b, #86efac)'
        ];

        const descripciones = {
            'Definición de Física': 'Qué es, de dónde viene y por qué es importante',
            'Importancia de la Física': 'Cómo la física está en todo lo que usas',
            'Ramas Principales': 'Mecánica, termodinámica, cuántica y más',
            'Método Científico': 'Cómo los científicos descubren cosas',
            'Grandes Científicos': 'Newton, Einstein, Curie y otros genios'
        };

        grid.innerHTML = subtemas.map((s, index) => {
            const color = colores[index % colores.length];
            const desc = descripciones[s.nombre] || 'Flashcards disponibles';
            const num = index + 1;

            return `
                <a href="/flashcards.html?subtema=${s.id}" class="tema-card" data-subtema="${s.id}">
                    <div class="tema-info">
                        <div class="tema-numero" style="background: ${color}">${num}</div>
                        <div>
                            <div class="tema-nombre">${s.nombre}</div>
                            <div class="tema-descripcion">${desc}</div>
                        </div>
                    </div>
                    <div class="tema-flecha">→</div>
                </a>
            `;
        }).join('');

        if (subtemas.length > 1) {
            estudiarTodo.style.display = 'block';
        }

    } catch (error) {
        console.error('Error cargando subtemas:', error);
        grid.innerHTML = `
            <div class="error-card">
                <h3>😕 Error de conexión</h3>
                <p>No se pudieron cargar los temas. Intenta de nuevo.</p>
                <button onclick="window.location.reload()" style="margin-top: 16px; padding: 10px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer;">🔄 Reintentar</button>
            </div>
        `;
    }
}