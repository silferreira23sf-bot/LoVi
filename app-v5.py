
import math
import os
import sqlite3
from datetime import date, datetime, timedelta
import pandas as pd
from PIL import Image, ImageDraw
import plotly.express as px
import streamlit as st

# =======================================================
# CONFIGURACIÓN GENERAL Y RUTAS RELATIVAS
# =======================================================
DB_PATH = 'encuentracan.db'
IMAGES_DIR = 'images/'

# Asegurar directorios locales
os.makedirs(IMAGES_DIR, exist_ok=True)

# =======================================================
# BASE DE DATOS DE BARRIOS DE MONTEVIDEO Y URUGUAY
# =======================================================
MONTEVIDEO_BARRIOS = {
    "Pocitos 🏖️": (-34.9100, -56.1550),
    "Punta Carretas 🛍️": (-34.9220, -56.1600),
    "Tres Cruces 🚌": (-34.8940, -56.1650),
    "Centro 🏙️": (-34.9040, -56.1900),
    "Ciudad Vieja ⚓": (-34.9060, -56.2050),
    "Cordón ☕": (-34.9000, -56.1750),
    "Buceo ⛵": (-34.8980, -56.1350),
    "Carrasco 🌳": (-34.8870, -56.0750),
    "Malvín 🌊": (-34.8930, -56.1000),
    "Prado 🌹": (-34.8650, -56.2000),
    "La Blanqueada 🏥": (-34.8850, -56.1550),
    "Parque Rodó 🎢": (-34.9120, -56.1700),
    "Aguada 🏢": (-34.8900, -56.1900),
    "Unión 🛍️": (-34.8800, -56.1350),
    "Paso de la Arena 🚜": (-34.8450, -56.2750),
    "Cerro 🏰": (-34.8900, -56.2550),
    "Maroñas 🐎": (-34.8600, -56.1200),
    "Sayago 🚂": (-34.8350, -56.2050),
    "Colón 🍇": (-34.8050, -56.2150),
    "Ciudad de la Costa 🌅": (-34.8250, -55.9800),
    "Maldonado / Punta del Este 🐬": (-34.9100, -54.9500),
}

# Configuración de página de Streamlit
st.set_page_config(
    page_title="LoVi 🐾 - Red Comunitaria de Mascotas (Uruguay)",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales amigables: Paleta pastel de verdes, amarillos suaves, huellitas y tipografía curva
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Quicksand:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Quicksand', 'Segoe UI', sans-serif;
    }

    .main-header {
        font-family: 'Fredoka', cursive, sans-serif;
        font-size: 2.6rem;
        color: #2E7D32; /* Verde bosque */
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .sub-header {
        font-size: 1.15rem;
        color: #555555;
        margin-bottom: 1.8rem;
    }
    
    /* Hero Banner Portada Pastel */
    .hero-banner {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFDE7 50%, #F1F8E9 100%);
        border: 2px dashed #A5D6A7;
        border-radius: 24px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.08);
        position: relative;
    }
    
    .hero-title {
        font-family: 'Fredoka', cursive, sans-serif;
        color: #1B5E20;
        font-size: 3.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #43A047;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }

    .badge-pill {
        background-color: #FFFFFF;
        color: #2E7D32;
        padding: 0.4rem 1.1rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-block;
        border: 1.5px solid #C8E6C9;
        margin: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    
    /* Tarjetas Pasteles con Huellitas */
    .feature-card-green {
        background: #E8F5E9;
        border: 2px solid #C8E6C9;
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
    }
    
    .feature-card-yellow {
        background: #FFFDE7;
        border: 2px solid #FFF59D;
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
    }
    
    .feature-card-orange {
        background: #FFF3E0;
        border: 2px solid #FFE0B2;
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        height: 100%;
    }
    
    .card-title {
        font-family: 'Fredoka', cursive, sans-serif;
        font-size: 1.35rem;
        color: #2E7D32;
        margin-bottom: 0.6rem;
    }

    .emergency-card {
        background-color: #FFFDE7; /* Amarillo crema suave */
        border-left: 6px solid #FBC02D; /* Amarillo dorado */
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #5D4037;
    }
    
    .success-card {
        background-color: #E8F5E9; /* Verde pastel suave */
        border-left: 6px solid #4CAF50; /* Verde brillante */
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #1B5E20;
    }
    
    .reward-pill {
        background-color: #FFE0B2; /* Naranja pastel */
        color: #E65100;
        padding: 0.38rem 0.9rem;
        border-radius: 9999px;
        font-weight: bold;
        font-size: 0.95rem;
        display: inline-block;
        border: 1px solid #FFB74D;
        margin-top: 5px;
    }
    
    .match-pill-high {
        background-color: #C8E6C9; /* Verde éxito */
        color: #1B5E20;
        padding: 0.4rem 1rem;
        border-radius: 9999px;
        font-weight: bold;
        font-size: 0.95rem;
        display: inline-block;
    }
    
    .match-pill-med {
        background-color: #FFF9C4; /* Amarillo moderado */
        color: #F57F17;
        padding: 0.4rem 1rem;
        border-radius: 9999px;
        font-weight: bold;
        font-size: 0.95rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# =======================================================
# CONTROL DE PANTALLA (PORTADA AMIGABLE / APP PRINCIPAL)
# =======================================================
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'portada'

if st.session_state.pantalla == 'portada':
    # Banner Hero con fondo pastel, tipografía amigable y huellitas
    st.markdown("""
    <div class="hero-banner">
        <div style="font-size: 2.2rem; margin-bottom: 5px;">🐾 🐾 🐾</div>
        <div class="hero-title">¡Bienvenid@ a LoVi! 🐶🐱</div>
        <div class="hero-subtitle">La red comunitaria más amigable para reencontrar mascotas en Uruguay 🇺🇾</div>
        <div>
            <span class="badge-pill">🐾 100% Gratuito y Solidario</span>
            <span class="badge-pill">📍 Montevideo y Canelones</span>
            <span class="badge-pill">⚡ Coincidencias en Tiempo Real</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 3 Tarjetas informativas con estética pastel
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card-green">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📍🐾</div>
            <div class="card-title">Mapa de Barrios</div>
            <p style="color: #37474F; font-size: 0.98rem;">Visualizá en tiempo real los avistamientos y alertas de mascotas perdidas en Montevideo y alrededores.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card-yellow">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍🐾</div>
            <div class="card-title">Cruces Inteligentes</div>
            <p style="color: #37474F; font-size: 0.98rem;">Cruzamos fotos, colores, ropa, chapitas y distancia GPS para conectarte con la persona que vio a tu compañero.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card-orange">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📲🐾</div>
            <div class="card-title">Contacto Directo</div>
            <p style="color: #37474F; font-size: 0.98rem;">Reportá una pérdida o avistamiento en menos de 1 minuto y conectate directo por WhatsApp con otros vecinos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Botón principal estilizado alineado en 3 columnas
    col_a, col_b, col_c = st.columns([1, 2])
    with col_b:
        if st.button("🚀 ENTRAR A LA APLICACIÓN 🐾", use_container_width=True):
            st.session_state.pantalla = 'app'
            st.rerun()
            
    # Detiene la ejecución para mostrar únicamente la portada hasta hacer clic
    st.stop()

# Botón en la barra lateral para volver a la portada en cualquier momento
if st.sidebar.button("🏠 Inicio / Portada"):
    st.session_state.pantalla = 'portada'
    st.rerun()

# =======================================================
# MOTOR DE BASE DE DATOS Y PLACEHOLDERS
# =======================================================

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_placeholder_image(filename, text, bg_color):
    """Crea una imagen temporal hermosa con PIL si no se sube una foto real"""
    path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(path):
        return path
    img = Image.new('RGB', (400, 300), color=bg_color)
    d = ImageDraw.Draw(img)
    d.rectangle([(10, 10), (390, 290)], outline=(255, 255, 255), width=3)
    d.text((30, 80), "LoVi 🐾 (Uruguay)", fill=(255, 255, 255))
    d.text((30, 120), text, fill=(255, 255, 255))
    img.save(path)
    return path

def init_db():
    """Crea las tablas y precarga datos de prueba de Uruguay si la base de datos está vacía"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tablas con soporte para RECOMPENSA (pesos uruguayos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mascotas_perdidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foto_path TEXT,
        nombre TEXT,
        raza TEXT,
        color_primario TEXT,
        color_secundario TEXT,
        tiene_collar INTEGER,
        tiene_ropa INTEGER,
        detalles_fisicos TEXT,
        latitud REAL,
        longitud REAL,
        zona_nombre TEXT,
        fecha_perdida TEXT,
        contacto_telefono TEXT,
        monto_recompensa TEXT,
        estado TEXT DEFAULT 'activo'
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS avistamientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foto_path TEXT,
        color_primario TEXT,
        color_secundario TEXT,
        tiene_collar INTEGER,
        tiene_ropa INTEGER,
        detalles_observados TEXT,
        latitud REAL,
        longitud REAL,
        zona_nombre TEXT,
        fecha_avistamiento TEXT,
        estado TEXT DEFAULT 'pendiente'
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS coincidencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        perdido_id INTEGER,
        avistamiento_id INTEGER,
        score_similitud REAL,
        fecha_calculo TEXT,
        FOREIGN KEY (perdido_id) REFERENCES mascotas_perdidas (id),
        FOREIGN KEY (avistamiento_id) REFERENCES avistamientos (id),
        UNIQUE(perdido_id, avistamiento_id)
    )
    ''')
    conn.commit()
    
    # Si la columna monto_recompensa no existe en instalaciones previas, la agregamos
    try:
        cursor.execute("SELECT monto_recompensa FROM mascotas_perdidas LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE mascotas_perdidas ADD COLUMN monto_recompensa TEXT")
        conn.commit()

    # Verificar si ya hay datos, sino insertamos ejemplos de Montevideo, Uruguay
    cursor.execute("SELECT COUNT(*) AS total FROM mascotas_perdidas")
    r = cursor.fetchone()
    if r and int(r['total']) == 0:
        p1_img = create_placeholder_image("toby.png", "Toby\nGolden Retriever\nDorado\nCollar: SI", (218, 165, 32))
        p2_img = create_placeholder_image("lola.png", "Lola\nCaniche\nBlanco\nRopa: SI", (245, 245, 220))
        p3_img = create_placeholder_image("rocco.png", "Rocco\nMestizo\nNegro/Marron\nCollar: SI", (50, 50, 50))
        
        a1_img = create_placeholder_image("visto1.png", "AVISTAMIENTO #1\nDorado\nCollar: SI", (200, 150, 30))
        a2_img = create_placeholder_image("visto2.png", "AVISTAMIENTO #2\nBlanco\nRopa: SI", (230, 230, 210))
        a3_img = create_placeholder_image("visto3.png", "AVISTAMIENTO #3\nNegro/Marron\nCollar: SI", (40, 40, 40))
        
        hoy = date.today().isoformat()
        hace_un_dia = (date.today() - timedelta(days=1)).isoformat()
        
        # Insertar mascotas perdidas (Ubicaciones reales en Montevideo, Uruguay)
        cursor.executemany('''
        INSERT INTO mascotas_perdidas (foto_path, nombre, raza, color_primario, color_secundario, tiene_collar, tiene_ropa, detalles_fisicos, latitud, longitud, zona_nombre, fecha_perdida, contacto_telefono, monto_recompensa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            (p1_img, "Toby", "Golden Retriever", "Dorado", "Blanco", 1, 0, "Mancha blanca en el pecho, muy amigable y juguetón.", -34.9125, -56.1480, "Pocitos (Montevideo)", hace_un_dia, "+59899123456", "$ 5.000 UYU"),
            (p2_img, "Lola", "Caniche", "Blanco", "Ninguno", 0, 1, "Tiene un saquito tejido de abrigo, es temerosa.", -34.8622, -56.1950, "Prado (Montevideo)", hace_un_dia, "+59899123456", "Sin recompensa"),
            (p3_img, "Rocco", "Mestizo", "Negro", "Marron", 1, 0, "De tamaño pequeño, orejita derecha un poco caída.", -34.8872, -56.0685, "Carrasco (Montevideo)", hace_un_dia, "+59899123456", "$ 10.000 UYU")
        ])
        
        # Insertar avistamientos correspondientes cercanos en Montevideo
        cursor.executemany('''
        INSERT INTO avistamientos (foto_path, color_primario, color_secundario, tiene_collar, tiene_ropa, detalles_observados, latitud, longitud, zona_nombre, fecha_avistamiento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            (a1_img, "Dorado", "Blanco", 1, 0, "Daba vueltas asustado cerca de la rambla y Av. Brasil.", -34.9110, -56.1495, "Rambla de Pocitos", hoy),
            (a2_img, "Blanco", "Ninguno", 0, 1, "Llevaba un saquito tejido puesto, estaba sentado temblando bajo un árbol del Rosedal.", -34.8610, -56.1970, "Rosedal del Prado", hoy),
            (a3_img, "Negro", "Marron", 1, 0, "Corría rápido por Av. Italia en dirección al norte, se lo veía muy desorientado.", -34.8850, -56.0710, "Av. Italia y Carrasco", hoy)
        ])
        conn.commit()
    conn.close()

# Inicializar DB en cada ejecución
init_db()

# =======================================================
# MOTOR DE COINCIDENCIAS (Matching Engine integrado)
# =======================================================

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia real en kilómetros entre dos coordenadas GPS"""
    R = 6371.0 # Radio de la Tierra en km
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def compute_total_match(p_lat, p_lon, p_color1, p_color2, p_collar, p_ropa, p_date_str,
                        s_lat, s_lon, s_color1, s_color2, s_collar, s_ropa, s_date_str):
    """Calcula el score de similitud ponderado (Geo 40%, Visual 45%, Tiempo 15%)"""
    # 1. Puntaje Geográfico (40 pts)
    dist = calculate_haversine_distance(p_lat, p_lon, s_lat, s_lon)
    if dist <= 1.0:
        score_geo = 40.0
    elif dist <= 5.0:
        score_geo = 40.0 * (1.0 - (dist - 1.0) / 4.0)
    else:
        score_geo = 0.0
        
    # 2. Puntaje Visual (45 pts)
    score_visual = 0.0
    if p_color1.lower() == s_color1.lower():
        score_visual += 15.0
    if p_color2.lower() == s_color2.lower() and p_color2.lower() != 'ninguno':
        score_visual += 10.0
    if int(p_collar) == int(s_collar):
        score_visual += 10.0
    if int(p_ropa) == int(s_ropa):
        score_visual += 10.0
        
    # 3. Puntaje Temporal (15 pts)
    try:
        p_date = datetime.strptime(p_date_str, "%Y-%m-%d").date()
        s_date = datetime.strptime(s_date_str, "%Y-%m-%d").date()
        diff_days = abs((p_date - s_date).days)
    except:
        diff_days = 10
        
    if diff_days <= 1:
        score_temp = 15.0
    elif diff_days <= 7:
        score_temp = 15.0 * (1.0 - (diff_days - 1) / 6.0)
    else:
        score_temp = 0.0
        
    total_score = score_geo + score_visual + score_temp
    return round(total_score, 1), round(dist, 2)

def run_matching_engine_for_all():
    """Recalcula las coincidencias para todos los reportes activos en la DB"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    perdidos = cursor.execute("SELECT * FROM mascotas_perdidas WHERE estado = 'activo'").fetchall()
    avistamientos = cursor.execute("SELECT * FROM avistamientos WHERE estado = 'pendiente'").fetchall()
    
    matches_inserted = 0
    hoy_str = date.today().isoformat()
    
    for p in perdidos:
        for a in avistamientos:
            score, dist = compute_total_match(
                p['latitud'], p['longitud'], p['color_primario'], p['color_secundario'], p['tiene_collar'], p['tiene_ropa'], p['fecha_perdida'],
                a['latitud'], a['longitud'], a['color_primario'], a['color_secundario'], a['tiene_collar'], a['tiene_ropa'], a['fecha_avistamiento']
            )
            
            if score >= 40.0:
                cursor.execute('''
                INSERT INTO coincidencias (perdido_id, avistamiento_id, score_similitud, fecha_calculo)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(perdido_id, avistamiento_id) DO UPDATE SET
                    score_similitud = excluded.score_similitud,
                    fecha_calculo = excluded.fecha_calculo
                ''', (p['id'], a['id'], score, hoy_str))
                matches_inserted += 1
            else:
                cursor.execute("DELETE FROM coincidencias WHERE perdido_id = ? AND avistamiento_id = ?", (p['id'], a['id']))
                
    conn.commit()
    conn.close()
    return matches_inserted

def run_matching_engine_for_pet(pet_id):
    """Calcula las coincidencias para un perrito recién registrado"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    p = cursor.execute("SELECT * FROM mascotas_perdidas WHERE id = ?", (pet_id,)).fetchone()
    if not p:
        conn.close()
        return 0
        
    avistamientos = cursor.execute("SELECT * FROM avistamientos WHERE estado = 'pendiente'").fetchall()
    matches_count = 0
    hoy_str = date.today().isoformat()
    
    for a in avistamientos:
        score, dist = compute_total_match(
            p['latitud'], p['longitud'], p['color_primario'], p['color_secundario'], p['tiene_collar'], p['tiene_ropa'], p['fecha_perdida'],
            a['latitud'], a['longitud'], a['color_primario'], a['color_secundario'], a['tiene_collar'], a['tiene_ropa'], a['fecha_avistamiento']
        )
        
        if score >= 40.0:
            cursor.execute('''
            INSERT INTO coincidencias (perdido_id, avistamiento_id, score_similitud, fecha_calculo)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(perdido_id, avistamiento_id) DO UPDATE SET
                score_similitud = excluded.score_similitud,
                fecha_calculo = excluded.fecha_calculo
            ''', (p['id'], a['id'], score, hoy_str))
            matches_count += 1
            
    conn.commit()
    conn.close()
    return matches_count

# =======================================================
# --- SIDEBAR DE NAVEGACIÓN ---
# =======================================================
st.sidebar.image("https://images.unsplash.com/photo-1543466835-00a7907e9de1?q=80&w=200", width=120)
st.sidebar.title("🐾 LoVi Uruguay")
st.sidebar.markdown("*¡Ayudanos a que vuelvan a casa! Red comunitaria uruguaya para mascotas perdidas* 🇺🇾")
st.sidebar.write("---")

menu = st.sidebar.radio(
    "Navegación / Menú",
    [
        "📊 Panel de Control y Alertas",
        "🚨 Reportar Perro Perdido (Dueño)",
        "👁️ Reportar Avistamiento (Vecino)",
        "✨ Centro de Coincidencias Inteligentes"
    ]
)

st.sidebar.write("---")
st.sidebar.markdown("""
💡 **UX Solidario:**
* Reportar una pérdida toma menos de 1 minuto.
* Los avistamientos se cruzan geográficamente con las alertas activas en tiempo real.
* El mapa está centrado por defecto en **Montevideo, Uruguay**.
""")

# =======================================================
# PANTALLA 1: PANEL DE CONTROL Y ALERTAS
# =======================================================
if menu == "📊 Panel de Control y Alertas":
    st.markdown("<div class='main-header'>🐾 Panel de Control y Alertas Activas</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Monitoreá mascotas perdidas y avistamientos en tiempo real en todo Uruguay.</div>", unsafe_allow_html=True)
    
    # KPIs rápidos usando AS total y int(r['total']) para garantizar entero nativo de Python
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) AS total FROM mascotas_perdidas WHERE estado = 'activo'")
    r1 = c.fetchone()
    total_perdidos = int(r1['total']) if r1 else 0
    
    c.execute("SELECT COUNT(*) AS total FROM avistamientos WHERE estado = 'pendiente'")
    r2 = c.fetchone()
    total_avistamientos = int(r2['total']) if r2 else 0
    
    # Calcular coincidencias con score >= 60%
    run_matching_engine_for_all()
    c.execute("SELECT COUNT(*) AS total FROM coincidencias WHERE score_similitud >= 60.0")
    r3 = c.fetchone()
    total_matches = int(r3['total']) if r3 else 0
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🚨 Alertas de Pérdida Activas", total_perdidos)
    with col2:
        st.metric("👁️ Avistamientos en la Calle", total_avistamientos)
    with col3:
        st.metric("✨ Coincidencias Altas (>60%)", total_matches, delta="Cruces inteligentes", delta_color="normal")
        
    st.write("---")
    
    # Mapa interactivo de Uruguay (Plotly)
    st.subheader("🗺️ Mapa Solidario de Búsqueda (Montevideo y alrededores)")
    
    conn = get_db_connection()
    df_perdidos = pd.read_sql_query("SELECT id, nombre, latitud, longitud, 'Perdido (Dueño)' as Tipo, raza as Info FROM mascotas_perdidas WHERE estado = 'activo'", conn)
    df_avistamientos = pd.read_sql_query("SELECT id, latitud, longitud, 'Avistamiento (Calle)' as Tipo, detalles_observados as Info FROM avistamientos WHERE estado = 'pendiente'", conn)
    conn.close()
    
    if not df_perdidos.empty or not df_avistamientos.empty:
        df_mapa = pd.concat([df_perdidos, df_avistamientos], ignore_index=True)
        
        # Plotly Scatter Plot centrado en Montevideo
        fig = px.scatter(
            df_mapa,
            x="longitud",
            y="latitud",
            color="Tipo",
            text=df_mapa["nombre"].fillna("Avistamiento"),
            hover_data=["Info"],
            color_discrete_map={"Perdido (Dueño)": "#4CAF50", "Avistamiento (Calle)": "#FBC02D"},
            title="Coordenadas de Pérdidas vs. Avistamientos Recientes"
        )
        fig.update_traces(marker=dict(size=16, opacity=0.9, line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(
            xaxis_title="Longitud",
            yaxis_title="Latitud",
            legend_title="Tipo de Reporte",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay reportes cargados aún para mostrar en el mapa.")

    # Listas de datos rápidas
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🚨 Últimas Mascotas Perdidas")
        conn = get_db_connection()
        perdidas = conn.execute("SELECT * FROM mascotas_perdidas WHERE estado = 'activo' ORDER BY id DESC LIMIT 5").fetchall()
        conn.close()
        
        for p in perdidas:
            recompensa_str = f" | 💰 **Recompensa:** {p['monto_recompensa']}" if p['monto_recompensa'] and p['monto_recompensa'] != 'Sin recompensa' else ""
            with st.expander(f"🐶 {p['nombre']} - {p['raza']} ({p['zona_nombre']})"):
                col_img, col_txt = st.columns(2)
                with col_img:
                    if os.path.exists(p['foto_path']):
                        st.image(p['foto_path'], use_container_width=True)
                with col_txt:
                    st.write(f"**Color:** {p['color_primario']} / {p['color_secundario']}")
                    st.write(f"**Collar:** {'Sí' if p['tiene_collar'] else 'No'} | **Ropa:** {'Sí' if p['tiene_ropa'] else 'No'}")
                    st.write(f"**Última vez visto:** {p['fecha_perdida']}")
                    st.write(f"**Detalles:** {p['detalles_fisicos']}")
                    if p['monto_recompensa'] and p['monto_recompensa'] != 'Sin recompensa':
                        st.markdown(f"<div class='reward-pill'>💰 Recompensa Ofrecida: {p['monto_recompensa']}</div>", unsafe_allow_html=True)
                    
    with col_right:
        st.subheader("👁️ Avistamientos de Vecinos")
        conn = get_db_connection()
        avistamientos = conn.execute("SELECT * FROM avistamientos WHERE estado = 'pendiente' ORDER BY id DESC LIMIT 5").fetchall()
        conn.close()
        
        for a in avistamientos:
            with st.expander(f"📍 Avistamiento en {a['zona_nombre']} ({a['fecha_avistamiento']})"):
                col_img, col_txt = st.columns(2)
                with col_img:
                    if os.path.exists(a['foto_path']):
                        st.image(a['foto_path'], use_container_width=True)
                with col_txt:
                    st.write(f"**Color Primario:** {a['color_primario']} / {a['color_secundario']}")
                    st.write(f"**Collar:** {'Sí' if a['tiene_collar'] else 'No'} | **Ropa:** {'Sí' if a['tiene_ropa'] else 'No'}")
                    st.write(f"**Detalles Observados:** {a['detalles_observados']}")

# =======================================================
# PANTALLA 2: REPORTAR PERRO PERDIDO
# =======================================================
elif menu == "🚨 Reportar Perro Perdido (Dueño)":
    st.markdown("<div class='main-header'>🚨 Reportar Mascota Perdida</div>", unsafe_allow_html=True)
    st.markdown("<div class='emergency-card'><strong>🐾 ¡Mucha fuerza!</strong> Completa estos datos rápidos para activar de inmediato las alertas en la red comunitaria de Uruguay.</div>", unsafe_allow_html=True)
    
    with st.form("form_perdido"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la mascota *", placeholder="Ej: Toby")
            raza = st.text_input("Raza o mestizaje *", placeholder="Ej: Caniche, Ovejero o Mestizo")
            color_primario = st.selectbox("Color Primario *", ["Dorado", "Blanco", "Negro", "Marron", "Gris", "Crema"])
            color_secundario = st.selectbox("Color Secundario (Si tiene)", ["Ninguno", "Dorado", "Blanco", "Negro", "Marron", "Gris", "Crema"])
            detalles_fisicos = st.text_area("Señas particulares / Detalles físicos", placeholder="Ej: Mancha negra en ojo derecho, renguea de la patita trasera.")
            
            # Campo de Recompensa
            monto_recompensa = st.text_input("💰 Ofrecer Recompensa (Opcional)", placeholder="Ej: $ 5.000 UYU o Sin recompensa")
            
        with col2:
            tiene_collar = st.checkbox("¿Tiene collar puesto?")
            tiene_ropa = st.checkbox("¿Tiene ropa/abrigo puesto?")
            fecha_perdida = st.date_input("Fecha en que se perdió *", value=date.today())
            
            st.markdown("**Ubicación aproximada de pérdida:**")
            barrio_seleccionado = st.selectbox("Barrio o Zona de Uruguay *", list(MONTEVIDEO_BARRIOS.keys()))
            detalle_direccion = st.text_input("Esquina / Calle o Detalles (Opcional)", placeholder="Ej: Av. Brasil y Lázaro Gadea")
            
            # Latitud y longitud asignadas automáticamente sin marear al usuario
            latitud, longitud = MONTEVIDEO_BARRIOS[barrio_seleccionado]
            if detalle_direccion:
                zona_nombre = f"{barrio_seleccionado} ({detalle_direccion})"
            else:
                zona_nombre = barrio_seleccionado
            
            contacto_telefono = st.text_input("Celular de contacto (WhatsApp) *", placeholder="Ej: +598 99 123 456")
            
        foto_subida = st.file_uploader("Sube una foto clara de tu mascota (OBLIGATORIO)", type=["png", "jpg", "jpeg"])
        
        enviar = st.form_submit_button("🐾 REGISTRAR ALERTA Y BUSCAR COINCIDENCIAS")
        
        if enviar:
            if not nombre or not raza or not zona_nombre or not contacto_telefono:
                st.error("Por favor completa todos los campos obligatorios (*) antes de enviar.")
            elif not foto_subida:
                st.error("Es obligatorio subir una foto de tu mascota para contrastar con los avistamientos.")
            else:
                # Guardar foto
                foto_filename = f"user_lost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                foto_path = os.path.join(IMAGES_DIR, foto_filename)
                
                try:
                    img = Image.open(foto_subida)
                    img.save(foto_path)
                except Exception as e:
                    create_placeholder_image(foto_filename, f"{nombre}\n{raza}\nColor: {color_primario}\nCollar: {tiene_collar}", (255, 75, 75))
                
                # Recompensa por defecto si queda vacía
                recompensa_final = monto_recompensa if monto_recompensa.strip() != "" else "Sin recompensa"
                
                # Insertar en DB
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO mascotas_perdidas (foto_path, nombre, raza, color_primario, color_secundario, tiene_collar, tiene_ropa, detalles_fisicos, latitud, longitud, zona_nombre, fecha_perdida, contacto_telefono, monto_recompensa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (foto_path, nombre, raza, color_primario, color_secundario, int(tiene_collar), int(tiene_ropa), detalles_fisicos, latitud, longitud, zona_nombre, str(fecha_perdida), contacto_telefono, recompensa_final))
                pet_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Calcular coincidencias inmediatas
                matches_calc = run_matching_engine_for_pet(pet_id)
                
                # Celebración y Alerta
                st.balloons()
                st.markdown(f"""
                <div class='success-card'>
                    <h4>🎉 ¡Alerta de Búsqueda Activada en Uruguay!</h4>
                    <p>La ficha de <strong>{nombre}</strong> ya está cargada en el sistema.</p>
                    <p><strong>El motor de LoVi detectó {matches_calc} posibles avistamientos en la zona.</strong> Dirigite a la sección de <em>"Centro de Coincidencias Inteligentes"</em> en el menú de la izquierda para ver las fotos.</p>
                </div>
                """, unsafe_allow_html=True)

# =======================================================
# PANTALLA 3: REPORTAR AVISTAMIENTO (VECINO)
# =======================================================
elif menu == "👁️ Reportar Avistamiento (Vecino)":
    st.markdown("<div class='main-header'>👁️ Reportar un Perro que Viste en la Calle</div>", unsafe_allow_html=True)
    st.markdown("<div class='success-card'><strong>💪 ¡Tu reporte puede traerlo a casa!</strong> No hace falta que sepas su nombre. Sácale una foto, dinos en qué zona lo viste y nosotros cruzamos los datos al instante.</div>", unsafe_allow_html=True)
    
    with st.form("form_avistamiento"):
        col1, col2 = st.columns(2)
        with col1:
            color_primario = st.selectbox("Color Primario del perrito *", ["Dorado", "Blanco", "Negro", "Marron", "Gris", "Crema"])
            color_secundario = st.selectbox("Color Secundario (Si tiene)", ["Ninguno", "Dorado", "Blanco", "Negro", "Marron", "Gris", "Crema"])
            detalles_observados = st.text_area("Detalles observados (ej: llevaba saquito, asustado, rengo, amigable...)", placeholder="Ej: Corría asustado, tiene collar pero no se le ve chapita.")
            
        with col2:
            tiene_collar = st.checkbox("¿Tenía collar puesto?")
            tiene_ropa = st.checkbox("¿Tenía ropa o abrigo?")
            fecha_avistamiento = st.date_input("Fecha del avistamiento *", value=date.today())
            
            st.markdown("**Ubicación del avistamiento:**")
            barrio_seleccionado = st.selectbox("Barrio o Zona de Uruguay *", list(MONTEVIDEO_BARRIOS.keys()))
            detalle_direccion = st.text_input("Esquina / Calle o Detalles (Opcional)", placeholder="Ej: Av. Brasil y Lázaro Gadea / Frente a la plaza")
            
            # Latitud y longitud asignadas automáticamente sin marear al usuario
            latitud, longitud = MONTEVIDEO_BARRIOS[barrio_seleccionado]
            if detalle_direccion:
                zona_nombre = f"{barrio_seleccionado} ({detalle_direccion})"
            else:
                zona_nombre = barrio_seleccionado
            
        foto_subida = st.file_uploader("Saca o sube una foto del perrito (OBLIGATORIO)", type=["png", "jpg", "jpeg"])
        
        enviar_av = st.form_submit_button("🐾 REPORTAR AVISTAMIENTO Y AYUDAR")
        
        if enviar_av:
            if not zona_nombre:
                st.error("Por favor dinos la zona o esquina aproximada de Uruguay donde lo viste.")
            elif not foto_subida:
                st.error("Por favor sube una foto del perro para poder contrastar con los reportes.")
            else:
                # Guardar foto
                foto_filename = f"user_sighting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                foto_path = os.path.join(IMAGES_DIR, foto_filename)
                
                try:
                    img = Image.open(foto_subida)
                    img.save(foto_path)
                except Exception as e:
                    create_placeholder_image(foto_filename, f"AVISTAMIENTO NUEVO\nColor: {color_primario}\nCollar: {tiene_collar}", (128, 128, 128))
                
                # Insertar en DB
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO avistamientos (foto_path, color_primario, color_secundario, tiene_collar, tiene_ropa, detalles_observados, latitud, longitud, zona_nombre, fecha_avistamiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (foto_path, color_primario, color_secundario, int(tiene_collar), int(tiene_ropa), detalles_observados, latitud, longitud, zona_nombre, str(fecha_avistamiento)))
                conn.commit()
                conn.close()
                
                # Recalcular todas las coincidencias
                run_matching_engine_for_all()
                
                # Efecto nieve para denotar solidaridad / calma
                st.snow()
                st.markdown(f"""
                <div class='success-card'>
                    <h4>🎉 ¡Avistamiento Registrado con Éxito en LoVi!</h4>
                    <p>El avistamiento en <strong>{zona_nombre}</strong> ya está en nuestra base de datos activa.</p>
                    <p>Muchísimas gracias por involucrarte, ¡tu empatía vale oro para una familia uruguaya que busca a su mascota! ❤️</p>
                </div>
                """, unsafe_allow_html=True)

# =======================================================
# PANTALLA 4: CENTRO DE COINCIDENCIAS
# =======================================================
elif menu == "✨ Centro de Coincidencias Inteligentes":
    st.markdown("<div class='main-header'>🐾 Centro de Coincidencias de LoVi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Nuestro motor de cruce compara de forma autónoma la ubicación geográfica, marcas visuales y tiempo para sugerirte posibles reencuentros.</div>", unsafe_allow_html=True)
    
    # Recalcular coincidencias antes de mostrar
    run_matching_engine_for_all()
    
    conn = get_db_connection()
    coincidencias_query = '''
    SELECT 
        c.id as match_id,
        c.score_similitud,
        p.id as perdido_id,
        p.nombre,
        p.raza,
        p.color_primario as p_color,
        p.tiene_collar as p_collar,
        p.tiene_ropa as p_ropa,
        p.foto_path as p_foto,
        p.zona_nombre as p_zona,
        p.contacto_telefono,
        p.monto_recompensa,
        a.id as avistamiento_id,
        a.color_primario as a_color,
        a.tiene_collar as a_collar,
        a.tiene_ropa as a_ropa,
        a.foto_path as a_foto,
        a.zona_nombre as a_zona,
        a.detalles_observados,
        a.fecha_avistamiento
    FROM coincidencias c
    JOIN mascotas_perdidas p ON c.perdido_id = p.id
    JOIN avistamientos a ON c.avistamiento_id = a.id
    WHERE p.estado = 'activo' AND a.estado = 'pendiente'
    ORDER BY c.score_similitud DESC
    '''
    matches = conn.execute(coincidencias_query).fetchall()
    conn.close()
    
    if len(matches) == 0:
        st.info("Aún no detectamos coincidencias de alto score en las zonas reportadas. El sistema seguirá buscando de forma autónoma con cada nuevo avistamiento ingresado.")
    else:
        for m in matches:
            score = m['score_similitud']
            
            # Definir estilo según el score
            if score >= 80:
                score_html = f"<span class='match-pill-high'>🔥 Coincidencia Crítica: {score}%</span>"
            else:
                score_html = f"<span class='match-pill-med'>✨ Posible Coincidencia: {score}%</span>"
                
            st.markdown(f"### {score_html}", unsafe_allow_html=True)
            
            col_pet, col_vs, col_sighting = st.columns(3)
            
            with col_pet:
                st.markdown(f"**🐕 Mascota Buscada: {m['nombre']}** ({m['raza']})")
                if os.path.exists(m['p_foto']):
                    st.image(m['p_foto'], use_container_width=True)
                st.write(f"📍 **Perdido en:** {m['p_zona']}")
                st.write(f"🎨 **Color:** {m['p_color']} | 🏷️ **Collar:** {'Sí' if m['p_collar'] else 'No'} | 👕 **Ropa:** {'Sí' if m['p_ropa'] else 'No'}")
                if m['monto_recompensa'] and m['monto_recompensa'] != 'Sin recompensa':
                    st.markdown(f"<div class='reward-pill'>💰 Recompensa: {m['monto_recompensa']}</div>", unsafe_allow_html=True)
                
            with col_vs:
                st.markdown("<h2 style='text-align: center; margin-top: 100px; color: #4CAF50;'>🐾</h2>", unsafe_allow_html=True)
                
            with col_sighting:
                st.markdown(f"**📍 Perro Avistado en la Calle (ID #{m['avistamiento_id']})**")
                if os.path.exists(m['a_foto']):
                    st.image(m['a_foto'], use_container_width=True)
                st.write(f"📍 **Visto en:** {m['a_zona']} ({m['fecha_avistamiento']})")
                st.write(f"🎨 **Color:** {m['a_color']} | 🏷️ **Collar:** {'Sí' if m['a_collar'] else 'No'} | 👕 **Ropa:** {'Sí' if m['a_ropa'] else 'No'}")
                st.write(f"📝 **Detalles del vecino:** *\"{m['detalles_observados']}\"*")
                
            # Acciones de resolución
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                # Generar enlace pre-llenado de WhatsApp con el código de país de Uruguay (+598)
                msg = f"¡Hola! Vi el reporte de tu mascota {m['nombre']} en LoVi. Encontramos un avistamiento muy similar en {m['a_zona']}. ¡Ojalá sea él!"
                wp_link = f"https://wa.me/{m['contacto_telefono'].replace(' ', '').replace('+', '').replace('-', '')}?text={msg.replace(' ', '%20')}"
                st.markdown(f"#### [💬 Enviar WhatsApp al Dueño (+598)]({wp_link})")
            with col_act2:
                if st.button("💚 ¡Reunidos! (Marcar Resuelto)", key=f"resolv_{m['match_id']}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE mascotas_perdidas SET estado = 'reunido' WHERE id = ?", (m['perdido_id'],))
                    cursor.execute("UPDATE avistamientos SET estado = 'resuelto' WHERE id = ?", (m['avistamiento_id'],))
                    cursor.execute("DELETE FROM coincidencias WHERE perdido_id = ? OR avistamiento_id = ?", (m['perdido_id'], m['avistamiento_id']))
                    conn.commit()
                    conn.close()
                    st.balloons()
                    st.success("¡Qué enorme felicidad! Nos alegra muchísimo que se hayan reencontrado. Alerta cerrada con éxito. 🎉🐾")
                    st.rerun()
            with col_act3:
                if st.button("❌ Descartar Coincidencia", key=f"desc_{m['match_id']}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM coincidencias WHERE id = ?", (m['match_id'],))
                    conn.commit()
                    conn.close()
                    st.warning("Coincidencia descartada.")
                    st.rerun()
                    
            st.markdown("<hr style='border: 1px dashed #ddd;' />", unsafe_allow_html=True)
