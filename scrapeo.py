import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from unicodedata import normalize
from urllib.parse import urlparse

# ==========================================
# CONFIG
# ==========================================
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==========================================
# UTILIDADES
# ==========================================
def limpiar_nombre_archivo(nombre):
    nombre = normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = re.sub(r'[^\w\s-]', '', nombre).strip().lower()
    return re.sub(r'[-\s]+', '_', nombre)

def crear_carpetas_consola(nombre_consola):
    ruta = os.path.join("assets", "images", nombre_consola.lower())
    os.makedirs(ruta, exist_ok=True)
    return ruta

def descargar_imagen_local(url_imagen, carpeta, nombre):
    if not url_imagen:
        return "assets/images/no_image.png"

    ext = os.path.splitext(urlparse(url_imagen).path)[1]
    if not ext or len(ext) > 5:
        ext = ".jpg"

    archivo = f"{limpiar_nombre_archivo(nombre)}{ext}"
    ruta = os.path.join(carpeta, archivo)

    if os.path.exists(ruta):
        return ruta.replace("\\", "/")

    try:
        r = requests.get(url_imagen, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            with open(ruta, "wb") as f:
                f.write(r.content)
            return ruta.replace("\\", "/")
    except:
        pass

    return "assets/images/no_image.png"

# ==========================================
# SCRAPER NORMAL
# ==========================================
def ejecutar_scrapeo(url, consola, max_paginas=1):
    base = url.rstrip("/") + "/page/"
    carpeta = crear_carpetas_consola(consola)

    juegos = []

    for p in range(1, max_paginas + 1):
        print(f"\n📄 Página {p}")

        try:
            r = requests.get(base + str(p), headers=HEADERS, timeout=10)
            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "html.parser")
            articulos = soup.find_all("article")

            for art in articulos:
                titulo = art.find("h2")
                img = art.find("img")

                if not titulo or not img:
                    continue

                nombre = titulo.get_text().strip()

                if any(j["nombre"].lower() == nombre.lower() for j in juegos):
                    continue

                url_img = img.get("src")
                ruta_img = descargar_imagen_local(url_img, carpeta, nombre)

                juegos.append({
                    "id": f"{consola.lower()}_{limpiar_nombre_archivo(nombre)}",
                    "nombre": nombre,
                    "anio": 2010,
                    "genero": "Acción",
                    "imagen": ruta_img,
                    "descripcion": f"Juego de {consola}"
                })

            time.sleep(1)

        except Exception as e:
            print("❌ Error:", e)
            break

    return juegos

# ==========================================
# SCRAPER PRO PS1 (PUSHSQUARE)
# ==========================================
def scrapear_ps1_pushsquare_pro(url, consola, max_paginas=1):
    carpeta = crear_carpetas_consola(consola)
    juegos = []
    base_url = "https://www.pushsquare.com"

    for p in range(1, max_paginas + 1):
        url_actual = f"{url.split('&page=')[0]}&page={p}"
        print(f"\n🔥 PS1 Página {p}")

        try:
            r = requests.get(url_actual, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "html.parser")

            links = soup.select("a[href^='/games/']")

            for link in links:
                nombre = link.get_text(strip=True)
                href = link.get("href")

                if not nombre or len(nombre) < 2:
                    continue

                if any(j["nombre"].lower() == nombre.lower() for j in juegos):
                    continue

                url_juego = base_url + href
                print(f"🎮 {nombre}")

                try:
                    r2 = requests.get(url_juego, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, "html.parser")

                    # =========================
                    # IMAGEN (PRO)
                    # =========================
                    url_img = None

                    # 1. Open Graph
                    meta_img = soup2.find("meta", property="og:image")
                    if meta_img:
                        url_img = meta_img.get("content")

                    # 2. Figure
                    if not url_img:
                        img_tag = soup2.select_one("figure img")
                        if img_tag:
                            url_img = img_tag.get("src")

                    # 3. Fallback
                    if not url_img:
                        img_tag = soup2.find("img")
                        if img_tag:
                            url_img = img_tag.get("data-src") or img_tag.get("src")

                    if url_img and url_img.startswith("//"):
                        url_img = "https:" + url_img

                    if not url_img:
                        print(f"❌ Sin imagen: {nombre}")

                    ruta_img = descargar_imagen_local(url_img, carpeta, nombre)

                    # =========================
                    # AÑO
                    # =========================
                    texto = soup2.get_text()
                    match = re.search(r'(19\d{2}|20\d{2})', texto)
                    anio = int(match.group(0)) if match else 1995

                    juegos.append({
                        "id": f"{consola.lower()}_{limpiar_nombre_archivo(nombre)[:20]}",
                        "nombre": nombre,
                        "anio": anio,
                        "genero": "Desconocido",
                        "imagen": ruta_img,
                        "descripcion": f"Juego de {consola} (PushSquare)"
                    })

                    time.sleep(1)

                except Exception as e:
                    print(f"⚠️ Error juego: {e}")
                    continue

            time.sleep(1)

        except Exception as e:
            print(f"❌ Error página: {e}")
            break

    return juegos

# ==========================================
# MENÚ
# ==========================================
def Menu_Interactivo():
    print("\n🚀 SCRAPER VIDEOJUEGOS 🚀\n")

    consolas = ["PS1", "PS2", "PS3", "PSP", "PSVITA", "Wii", "WIIU", "Switch", "DS", "Xbox360"]

    for i, c in enumerate(consolas, 1):
        print(f"{i}. {c}")

    try:
        sel = int(input("\n👉 Consola: "))
        consola = consolas[sel - 1]
    except:
        print("❌ Error")
        return

    url = input("🔗 URL: ").strip()

    try:
        pags = int(input("📄 Páginas: ") or 1)
    except:
        pags = 1

    # 🔥 DETECCIÓN INTELIGENTE
    if consola.upper() == "PS1" and "pushsquare.com" in url:
        resultados = scrapear_ps1_pushsquare_pro(url, consola, pags)
    else:
        resultados = ejecutar_scrapeo(url, consola, pags)

    if not resultados:
        print("❌ No se extrajo nada")
        return

    archivo = "juegos.json"
    datos = {}

    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except:
                datos = {}

    existentes = datos.get(consola, [])
    datos[consola] = existentes + resultados

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    print(f"\n✅ {len(resultados)} juegos agregados a {consola}")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    Menu_Interactivo()