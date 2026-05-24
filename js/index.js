document.addEventListener('DOMContentLoaded', async () => {
    // Verificar si hay usuario logueado
    const usuarioId = localStorage.getItem('usuario_id');
    const usuarioNombre = localStorage.getItem('usuario_nombre');
    
    if (usuarioId && usuarioNombre) {
        document.getElementById('nav-user').innerHTML = `
            <span class="user-name">👤 ${usuarioNombre}</span>
            <a href="#" class="nav-link" onclick="cerrarSesion()">Cerrar sesión</a>
        `;
    }
    
    await cargarTemas();
});

async function cargarTemas() {
    const lista = document.getElementById('tema-list');
    
    try {
        const res = await fetch('/api/temas');
        const data = await res.json();
        
        if (!data.success || !data.temas.length) {
            lista.innerHTML = '<li class="loading">No hay temas disponibles</li>';
            return;
        }
        
        // ✅ CORREGIDO: Usar t.id y t.nombre
        lista.innerHTML = data.temas.map(t => `
            <li class="tema-item" onclick="seleccionarTema(${t.id}, '${t.nombre}', this)">
                <span>${t.nombre}</span>
                <span class="tema-arrow">›</span>
            </li>
        `).join('');
        
    } catch (error) {
        console.error('Error:', error);
        lista.innerHTML = '<li class="loading">Error al cargar temas</li>';
    }
}

async function seleccionarTema(temaId, temaNombre, elemento) {
    // Quitar clase active de todos
    document.querySelectorAll('.tema-item').forEach(el => el.classList.remove('active'));
    // Agregar active al clickeado
    elemento.classList.add('active');
    
    // Actualizar título
    document.getElementById('panel-title').textContent = temaNombre;
    document.getElementById('panel-subtitle').textContent = 'Selecciona un subtema para comenzar a estudiar';
    
    // Cargar subtemas
    const grid = document.getElementById('subtemas-grid');
    grid.innerHTML = '<div class="loading">Cargando subtemas...</div>';
    
    try {
        // ✅ CORREGIDO: Usar temaId (número) en la URL
        const res = await fetch(`/api/temas/${temaId}/subtemas`);
        const data = await res.json();
        
        if (!data.success || !data.subtemas.length) {
            grid.innerHTML = '<div class="empty-state"><p>No hay subtemas disponibles</p></div>';
            return;
        }
        
        // ✅ CORREGIDO: Usar s.nombre o s.subtema según tu API
        grid.innerHTML = data.subtemas.map((s, i) => `
            <a href="/contenido.html?id=${s.id}" class="subtema-card">
                <span class="subtema-title">${s.nombre || s.subtema}</span>
                <span class="subtema-number">${i + 1}</span>
            </a>
        `).join('');
        
    } catch (error) {
        console.error('Error:', error);
        grid.innerHTML = '<div class="empty-state"><p>Error al cargar subtemas</p></div>';
    }
}

function cerrarSesion() {
    localStorage.removeItem('usuario_id');
    localStorage.removeItem('usuario_nombre');
    window.location.reload();
}