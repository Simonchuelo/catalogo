import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from unicodedata import normalize
from urllib.parse import urlparse

# ==========================================
# 1. CONFIGURACIÓN Y HEADERS
# ==========================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# ==========================================
# 2. FUNCIONES DE UTILIDAD
# ==========================================
def limpiar_nombre_archivo(nombre):
    """Sanea el nombre del juego para usarlo como nombre de archivo."""
    nombre = normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = re.sub(r'[^\w\s-]', '', nombre).strip().lower()
    return re.sub(r'[-\s]+', '_', nombre)

def crear_carpetas_consola(nombre_consola):
    """Crea la estructura de carpetas: assets/images/[consola]"""
    ruta_base = os.path.join("assets", "images", nombre_consola.lower())
    if not os.path.exists(ruta_base):
        os.makedirs(ruta_base, exist_ok=True)
        print(f"📁 Carpeta verificada/creada: {ruta_base}")
    return ruta_base

def descargar_imagen_local(url_imagen, ruta_carpeta, nombre_juego):
    """Descarga la imagen y devuelve la ruta relativa para el JSON."""
    if not url_imagen:
        return "assets/images/no_image.png"

    path_url = urlparse(url_imagen).path
    ext = os.path.splitext(path_url)[1]
    if not ext or len(ext) > 5: ext = ".jpg"

    nombre_archivo = f"{limpiar_nombre_archivo(nombre_juego)}{ext}"
    ruta_completa_archivo = os.path.join(ruta_carpeta, nombre_archivo)
    ruta_relativa_frontend = ruta_completa_archivo.replace("\\", "/")

    if os.path.exists(ruta_completa_archivo):
        return ruta_relativa_frontend

    try:
        res = requests.get(url_imagen, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            with open(ruta_completa_archivo, 'wb') as f:
                f.write(res.content)
            return ruta_relativa_frontend
    except:
        pass
    return "assets/images/no_image.png"

# ==========================================
# 3. LÓGICA DE SCRAPEO
# ==========================================
def ejecutar_scrapeo(url_entrada, consola_key, max_paginas=1):
    """Extrae datos de la web, descarga imágenes y genera lista de juegos."""
    
    url_limpia = url_entrada.rstrip("/")
    if "/page/" in url_limpia:
        url_base = url_limpia.split("/page/")[0] + "/page/"
    else:
        url_base = url_limpia + "/page/"

    ruta_imagenes = crear_carpetas_consola(consola_key)
    juegos_scrapedados = []
    
    for pagina in range(1, max_paginas + 1):
        print(f"\n--- 📄 Extrayendo Página {pagina} de {max_paginas} ---")
        url_actual = f"{url_base}{pagina}/"
        
        try:
            res = requests.get(url_actual, headers=HEADERS, timeout=15)
            if res.status_code != 200: 
                print(f"⚠️ Fin de páginas o error (Status: {res.status_code})")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            articulos = soup.select('article') or soup.select('.post-column') or soup.select('.item-list') or soup.find_all('div', class_=re.compile(r'post|entry|item'))

            if not articulos:
                print("⚠️ No se encontraron elementos de juego en esta página.")
                continue

            for art in articulos:
                titulo_tag = art.find('h2') or art.find('h3') or art.find('a', class_='post-title')
                img_tag = art.find('img')
                
                if titulo_tag and img_tag:
                    nombre_sucio = titulo_tag.get_text().strip()
                    if len(nombre_sucio) < 3: continue 

                    # Limpieza del título (Añadidas las nuevas plataformas al Regex)
                    regex_limpieza = r'(PS3|PSP|PSVITA|VITA|WIIU|WII U|ISO|FREE DOWNLOAD|USA|EUR|JPN|FULL PKG|PSN|Rpcs3|PS2|PCSX2|WII|SWITCH|XBOX360|3DS)'
                    nombre_limpio = re.sub(regex_limpieza, '', nombre_sucio, flags=re.IGNORECASE).strip()
                    nombre_limpio = re.sub(r'[-–()] +$', '', nombre_limpio).strip()

                    url_img_src = img_tag.get('data-src') or img_tag.get('data-lazy-src') or img_tag.get('src')
                    
                    if url_img_src:
                        if url_img_src.startswith('//'):
                            url_img_src = 'https:' + url_img_src
                        
                        print(f"🎮 Procesando: {nombre_limpio}")
                        ruta_local_img = descargar_imagen_local(url_img_src, ruta_imagenes, nombre_limpio)

                        juego = {
                            "id": f"{consola_key.lower()}_{limpiar_nombre_archivo(nombre_limpio)[:15]}",
                            "nombre": nombre_limpio,
                            "anio": 2010,
                            "genero": "Acción / Aventura",
                            "imagen": ruta_local_img,
                            "descripcion": f"Juego de {consola_key} extraído automáticamente."
                        }
                        juegos_scrapedados.append(juego)
            
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error en página {pagina}: {e}")
            break

    return juegos_scrapedados

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
def Menu_Interactivo():
    print("\n==========================================")
    print("🚀 SCRAPER DE VIDEOJUEGOS PROFESIONAL 🚀")
    print("==========================================\n")

    # Lista de consolas actualizada
    consolas = ["PS1", "PS2", "PS3", "PSP", "PSVITA", "Wii", "WIIU", "Switch", "DS", "Xbox360"]
    
    for i, con in enumerate(consolas, 1):
        print(f"{i}. {con}")
    
    try:
        sel = int(input("\n👉 Selecciona el número de consola: "))
        consola_elegida = consolas[sel - 1]
    except:
        print("❌ Selección no válida.")
        return

    url_input = input(f"🔗 Pega el link de la categoría de {consola_elegida}: ").strip()
    if not url_input.startswith("http"):
        print("❌ URL no válida.")
        return

    try:
        pags = int(input("📄 ¿Cuántas páginas quieres procesar?: "))
    except:
        pags = 1

    resultados = ejecutar_scrapeo(url_input, consola_elegida, pags)

    if resultados:
        archivo_json = 'juegos.json'
        datos_totales = {}

        if os.path.exists(archivo_json):
            with open(archivo_json, 'r', encoding='utf-8') as f:
                try: 
                    datos_totales = json.load(f)
                except: 
                    datos_totales = {}

        # Actualizamos solo la consola elegida en el JSON
        datos_totales[consola_elegida] = resultados

        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(datos_totales, f, indent=4, ensure_ascii=False)

        print(f"\n✅ ¡LISTO! {len(resultados)} juegos guardados en 'juegos.json' para {consola_elegida}.")
    else:
        print("\n❌ No se extrajo nada. Verifica la URL.")

if __name__ == "__main__":
    Menu_Interactivo()