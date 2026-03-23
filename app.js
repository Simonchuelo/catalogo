/**
 * RETROVAULT - Sistema de Gestión de Catálogo Gamer
 * Desarrollado para: Startup de soluciones IoT y Seguridad
 */

let baseDeDatosJuegos = {};
let consolaActual = "";
let listaFavoritos = JSON.parse(localStorage.getItem('mis_favoritos_retro')) || [];

// --- CONFIGURACIÓN DE SONIDO ---
const sonidoCoin = new Audio('assets/sounds/coin.mp3');
sonidoCoin.volume = 0.4; 

// --- BASE DE DATOS DE CONSOLAS ---
const baseDeDatosConsolas = [
    { id: "PS1", nombre: "PlayStation 1", imagen: "assets/images/ps1/default.jpg" },
    { id: "PS2", nombre: "PlayStation 2", imagen: "assets/images/ps2/default.jpg" },
    { id: "PS3", nombre: "PlayStation 3", imagen: "assets/images/ps3/default.jpg" },
    { id: "PSP", nombre: "PlayStation Portable", imagen: "assets/images/psp/default.jpg" },
    { id: "PSVITA", nombre: "PlayStation Vita", imagen: "assets/images/psvita/default.jpg" },
    { id: "Wii", nombre: "Wii", imagen: "assets/images/wii/default.jpg" },
    { id: "WIIU", nombre: "Nintendo Wii U", imagen: "assets/images/wiiu/default.jpg" },
    { id: "Switch", nombre: "Switch", imagen: "assets/images/switch/default.jpg" },
    { id: "DS", nombre: "3DS / 2DS", imagen: "assets/images/ds/default.jpg" },
    { id: "Xbox360", nombre: "Xbox 360", imagen: "assets/images/xbox360/default.jpg" }
];

// --- CARGA INICIAL DE DATOS ---
async function cargarDatos() {
    const loader = document.getElementById('loader-wrapper');
    try {
        const res = await fetch('juegos.json');
        if (!res.ok) throw new Error("Archivo juegos.json no encontrado");
        
        baseDeDatosJuegos = await res.json();
        
        setTimeout(() => {
            if (loader) loader.style.display = 'none';
            renderizarConsolas();
            actualizarContadorFavoritos();
        }, 800);
    } catch (err) {
        console.error("Error al cargar juegos.json:", err);
        const loaderMsg = document.querySelector('.loader-content p');
        if (loaderMsg) loaderMsg.innerText = "ERROR: ARCHIVO DE DATOS NO ENCONTRADO";
    }
}

// --- RENDERIZADO DE VISTA HOME ---
function renderizarConsolas() {
    const container = document.getElementById('consolas-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    baseDeDatosConsolas.forEach(c => {
        const juegos = baseDeDatosJuegos[c.id] || [];
        const totalJuegos = juegos.length;
        
        const div = document.createElement('div');
        div.className = 'consola-card';
        div.setAttribute('data-id', c.id);
        div.innerHTML = `
            <div class="card-img-container" style="height:150px; overflow:hidden;">
                <img src="${c.imagen}" style="width:100%; height:100%; object-fit:cover;" 
                     onerror="this.src='https://via.placeholder.com/300x200?text=${c.id}'">
            </div>
            <h3 style="padding:15px; text-align:center; font-family:'Orbitron'">${c.nombre} (${totalJuegos})</h3>
        `;
        div.onclick = () => abrirCatalogo(c.id, c.nombre);
        container.appendChild(div);
    });
}

// --- LÓGICA DEL CATÁLOGO ---
function abrirCatalogo(id, nombre) {
    consolaActual = id;
    document.getElementById('vista-home').style.display = 'none';
    document.getElementById('vista-catalogo').style.display = 'block';
    document.getElementById('titulo-consola').innerText = nombre;
    window.scrollTo(0,0);
    renderizarJuegos();
}

function renderizarJuegos() {
    const container = document.getElementById('juegos-container');
    const busqueda = document.getElementById('input-busqueda').value.toLowerCase();
    const orden = document.getElementById('ordenar-por').value;
    
    if (!container) return;
    container.innerHTML = '';

    let juegos = [...(baseDeDatosJuegos[consolaActual] || [])];

    // Filtrar por búsqueda
    if (busqueda) {
        juegos = juegos.filter(j => j.nombre.toLowerCase().includes(busqueda));
    }

    // Ordenar
    juegos.sort((a, b) => {
        if (orden === 'nombre-asc') return a.nombre.localeCompare(b.nombre);
        if (orden === 'anio-desc') return (b.anio || 0) - (a.anio || 0);
        return 0;
    });

    juegos.forEach(j => {
        const esFav = listaFavoritos.some(fav => fav.nombre === j.nombre);
        const div = document.createElement('div');
        div.className = 'juego-card';
        div.innerHTML = `
            <div class="juego-portada">
                <img src="${j.imagen}" alt="${j.nombre}" loading="lazy">
                <button class="btn-fav ${esFav ? 'active' : ''}" onclick="toggleFavorito(event, '${j.nombre.replace(/'/g, "\\'")}')">
                    <i class="fa-solid fa-star"></i>
                </button>
            </div>
            <div style="padding:10px;">
                <h4 style="font-size:0.9rem; margin-bottom:5px;">${j.nombre}</h4>
                <p style="font-size:0.75rem; color:var(--accent-neon)">${j.anio || 'Retro'}</p>
            </div>
        `;
        container.appendChild(div);
    });
}

// --- GESTIÓN DE FAVORITOS ---
function toggleFavorito(event, nombreJuego) {
    event.stopPropagation();
    
    const index = listaFavoritos.findIndex(f => f.nombre === nombreJuego);
    
    if (index > -1) {
        listaFavoritos.splice(index, 1);
    } else {
        listaFavoritos.push({ nombre: nombreJuego });
        // Intentar reproducir sonido de moneda
        try { sonidoCoin.play(); } catch(e) {}
    }

    localStorage.setItem('mis_favoritos_retro', JSON.stringify(listaFavoritos));
    actualizarContadorFavoritos();
    renderizarJuegos();
}

function borrarTodosFavoritos() {
    if (listaFavoritos.length === 0) return;
    
    if (confirm("¿Estás seguro de que quieres vaciar tu lista de favoritos?")) {
        listaFavoritos = [];
        localStorage.setItem('mis_favoritos_retro', JSON.stringify(listaFavoritos));
        actualizarContadorFavoritos();
        renderizarJuegos();
    }
}

function actualizarContadorFavoritos() {
    const contador = document.getElementById('fav-count');
    if (contador) contador.innerText = listaFavoritos.length;
}

// --- WHATSAPP ---
function enviarFavoritosWhatsApp() {
    if (listaFavoritos.length === 0) {
        alert("Tu lista está vacía. Selecciona algunos juegos primero.");
        return;
    }

    const numero = "5491164673729"; // Tu número configurado
    let mensaje = "Hola! Elegí estos juegos de RetroVault para instalar:%0A%0A";
    
    listaFavoritos.forEach((fav, i) => {
        mensaje += `${i + 1}. *${fav.nombre}*%0A`;
    });

    const url = `https://api.whatsapp.com/send?phone=${numero}&text=${mensaje}`;
    window.open(url, '_blank');
}

// --- EVENTOS Y NAVEGACIÓN ---
document.getElementById('btn-volver').onclick = () => {
    document.getElementById('vista-catalogo').style.display = 'none';
    document.getElementById('vista-home').style.display = 'block';
    document.getElementById('input-busqueda').value = '';
};

document.getElementById('logo-inicio').onclick = () => {
    location.reload();
};

document.getElementById('input-busqueda').oninput = renderizarJuegos;
document.getElementById('ordenar-por').onchange = renderizarJuegos;

// Iniciar aplicación
document.addEventListener('DOMContentLoaded', cargarDatos);
// Función para borrar todos los favoritos de una vez
function borrarTodosFavoritos() {
    if (listaFavoritos.length === 0) return;

    const confirmar = confirm("¿Estás seguro de que quieres vaciar tu lista de favoritos?");
    
    if (confirmar) {
        // Vaciar el array
        listaFavoritos = [];
        
        // Actualizar LocalStorage
        localStorage.setItem('mis_favoritos_retro', JSON.stringify(listaFavoritos));
        
        // Actualizar la interfaz
        actualizarContadorFavoritos();
        
        // Si estamos viendo el catálogo, refrescar las estrellas
        if (typeof renderizarJuegos === 'function') {
            renderizarJuegos();
        }
        
        // Opcional: Sonido de "error" o "delete" si tienes uno
        console.log("Lista de favoritos vaciada.");
    }
}