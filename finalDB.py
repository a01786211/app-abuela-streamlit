import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Guía para usar apps",
    page_icon="💻",
    layout="centered"
)

# ==================== CONEXIÓN A MONGODB ====================
# Para pruebas locales rápidas:
# puedes dejar el URI directo aquí temporalmente.
# Para Streamlit Cloud, luego lo moveremos a st.secrets.

MONGODB_URI = "mongodb+srv://a01786211_user:1234test@clusterapp.2wlkl3c.mongodb.net/?appName=ClusterApp"
MONGODB_DB = "app_abuela"
PUBLIC_ACCESS_PASSWORD = "1234"

@st.cache_resource
def get_mongo_client():
    return MongoClient(MONGODB_URI)

client = get_mongo_client()
db = client[MONGODB_DB]

guias_col = db["guias"]
dudas_col = db["dudas_resueltas"]


# ==================== ACCESO ====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso privado")
    st.write("Esta app es solo para uso autorizado.")

    password_input = st.text_input("Ingresa la contraseña", type="password")

    if st.button("Entrar"):
        if password_input == PUBLIC_ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")

    st.stop()

# ==================== BASE DE DATOS ====================
def seed_data():
    total = guias_col.count_documents({})
    if total == 0:
        datos = [
            {
                "app_nombre": "Mail",
                "tarea": "Abrir un correo",
                "paso_numero": 1,
                "instruccion": "Busca el ícono de Mail y haz clic para abrirlo.",
                "imagen": "imagenes/mail1.png"
            },
            {
                "app_nombre": "Mail",
                "tarea": "Abrir un correo",
                "paso_numero": 2,
                "instruccion": "Busca el correo que quieras leer en la lista.",
                "imagen": "imagenes/mail2.png"
            },
            {
                "app_nombre": "Mail",
                "tarea": "Abrir un correo",
                "paso_numero": 3,
                "instruccion": "Haz clic una sola vez sobre ese correo.",
                "imagen": "imagenes/mail3.png"
            },
            {
                "app_nombre": "Mail",
                "tarea": "Abrir un correo",
                "paso_numero": 4,
                "instruccion": "Lee el mensaje. Si quieres salir, busca la flecha de regreso.",
                "imagen": "imagenes/mail4.png"
            },

            {
                "app_nombre": "Netflix",
                "tarea": "Ver una serie",
                "paso_numero": 1,
                "instruccion": "Abre Netflix desde su ícono.",
                "imagen": "imagenes/netflix1.png"
            },
            {
                "app_nombre": "Netflix",
                "tarea": "Ver una serie",
                "paso_numero": 2,
                "instruccion": "Haz clic en la barra de búsqueda si quieres encontrar algo específico.",
                "imagen": "imagenes/netflix2.png"
            },
            {
                "app_nombre": "Netflix",
                "tarea": "Ver una serie",
                "paso_numero": 3,
                "instruccion": "Escribe el nombre de la serie o elige una portada.",
                "imagen": "imagenes/netflix3.png"
            },
            {
                "app_nombre": "Netflix",
                "tarea": "Ver una serie",
                "paso_numero": 4,
                "instruccion": "Haz clic en el botón de reproducir.",
                "imagen": "imagenes/netflix4.png"
            },

            {
                "app_nombre": "Banco",
                "tarea": "Entrar a mi cuenta",
                "paso_numero": 1,
                "instruccion": "Abre la app o página del banco.",
                "imagen": "imagenes/banco1.png"
            },
            {
                "app_nombre": "Banco",
                "tarea": "Entrar a mi cuenta",
                "paso_numero": 2,
                "instruccion": "Escribe tu usuario o número de cliente.",
                "imagen": "imagenes/banco2.png"
            },
            {
                "app_nombre": "Banco",
                "tarea": "Entrar a mi cuenta",
                "paso_numero": 3,
                "instruccion": "Escribe tu contraseña con calma.",
                "imagen": "imagenes/banco3.png"
            },
            {
                "app_nombre": "Banco",
                "tarea": "Entrar a mi cuenta",
                "paso_numero": 4,
                "instruccion": "Haz clic en Entrar o Iniciar sesión.",
                "imagen": "imagenes/banco4.png"
            },

            {
                "app_nombre": "Zoom",
                "tarea": "Entrar a una reunión",
                "paso_numero": 1,
                "instruccion": "Abre Zoom desde su ícono.",
                "imagen": "imagenes/zoom1.png"
            },
            {
                "app_nombre": "Zoom",
                "tarea": "Entrar a una reunión",
                "paso_numero": 2,
                "instruccion": "Haz clic en Unirse.",
                "imagen": "imagenes/zoom2.png"
            },
            {
                "app_nombre": "Zoom",
                "tarea": "Entrar a una reunión",
                "paso_numero": 3,
                "instruccion": "Escribe el ID de la reunión si te lo piden.",
                "imagen": "imagenes/zoom3.png"
            },
            {
                "app_nombre": "Zoom",
                "tarea": "Entrar a una reunión",
                "paso_numero": 4,
                "instruccion": "Haz clic en Join o Unirse para entrar.",
                "imagen": "imagenes/zoom4.png"
            },
        ]
        guias_col.insert_many(datos)

def obtener_apps():
    apps = guias_col.distinct("app_nombre")
    return sorted(apps)

def obtener_tareas(app_nombre):
    tareas = guias_col.distinct("tarea", {"app_nombre": app_nombre})
    return sorted(tareas)

def obtener_pasos(app_nombre, tarea):
    docs = list(
        guias_col.find(
            {"app_nombre": app_nombre, "tarea": tarea},
            {"_id": 0, "paso_numero": 1, "instruccion": 1, "imagen": 1}
        ).sort("paso_numero", 1)
    )
    return pd.DataFrame(docs)

def registrar_duda_resuelta(app_nombre, tarea):
    dudas_col.insert_one({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "app_nombre": app_nombre,
        "tarea": tarea
    })

def agregar_guia(app_nombre, tarea, pasos):
    docs = []
    for i, paso in enumerate(pasos, start=1):
        docs.append({
            "app_nombre": app_nombre,
            "tarea": tarea,
            "paso_numero": i,
            "instruccion": paso,
            "imagen": None
        })
    if docs:
        guias_col.insert_many(docs)

seed_data()

# ==================== ESTADO ====================
if "paso_actual" not in st.session_state:
    st.session_state.paso_actual = 1
if "ultima_app" not in st.session_state:
    st.session_state.ultima_app = None
if "ultima_tarea" not in st.session_state:
    st.session_state.ultima_tarea = None

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Menú")
    opcion = st.radio("Ir a", ["Inicio", "Usar guía", "Agregar nueva guía", "Historial"])

# ==================== INTERFAZ ====================
st.title("💻 Guía para usar apps")
st.markdown("### Ayuda paso a paso para personas mayores")

if opcion == "Inicio":
    st.subheader("Bienvenida")
    st.write("Esta app ayuda a usar aplicaciones de forma clara, sencilla y con texto grande.")
    st.info("Elige una app, elige lo que quieres hacer y sigue los pasos uno por uno.")
    st.success("✔️ Esta app te ayuda a usar tecnología sin miedo")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Apps disponibles", len(obtener_apps()))
    with col2:
        total = dudas_col.count_documents({})
        st.metric("Dudas resueltas", total)

elif opcion == "Usar guía":
    st.subheader("Selecciona la ayuda que necesitas")

    apps = obtener_apps()
    if not apps:
        st.warning("No hay apps registradas todavía.")
        st.stop()

    app_seleccionada = st.selectbox("¿Qué app quieres usar?", apps)
    tareas = obtener_tareas(app_seleccionada)

    if not tareas:
        st.warning("No hay tareas registradas para esta app.")
        st.stop()

    tarea_seleccionada = st.selectbox("¿Qué quieres hacer?", tareas)

    if (
        st.session_state.ultima_app != app_seleccionada
        or st.session_state.ultima_tarea != tarea_seleccionada
    ):
        st.session_state.paso_actual = 1
        st.session_state.ultima_app = app_seleccionada
        st.session_state.ultima_tarea = tarea_seleccionada

    pasos_df = obtener_pasos(app_seleccionada, tarea_seleccionada)
    total_pasos = len(pasos_df)

    if total_pasos > 0:
        if st.session_state.paso_actual > total_pasos:
            st.session_state.paso_actual = total_pasos

        st.progress(st.session_state.paso_actual / total_pasos)
        paso = pasos_df.iloc[st.session_state.paso_actual - 1]

        st.markdown(f"## Paso {int(paso['paso_numero'])} de {total_pasos}")
        st.markdown(f"### 👉 {paso['instruccion']}")

        if pd.notna(paso["imagen"]) and paso["imagen"]:
            if os.path.exists(paso["imagen"]):
                st.image(paso["imagen"], width=350)
            else:
                st.warning(f"No se encontró la imagen: {paso['imagen']}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("⬅️ Anterior") and st.session_state.paso_actual > 1:
                st.session_state.paso_actual -= 1
                st.rerun()

        with col2:
            if st.button("➡️ Siguiente") and st.session_state.paso_actual < total_pasos:
                st.session_state.paso_actual += 1
                st.rerun()

        with col3:
            if st.button("✅ Ya entendí"):
                registrar_duda_resuelta(app_seleccionada, tarea_seleccionada)
                st.balloons()
                st.success("¡Excelente! Terminaste la guía correctamente.")

        with col4:
            if st.button("❌ No entiendo"):
                st.warning("No pasa nada 😊 Intenta repetir el paso o pide ayuda.")

        st.divider()
        st.write("### Todos los pasos")
        for _, fila in pasos_df.iterrows():
            st.write(f"**Paso {int(fila['paso_numero'])}:** {fila['instruccion']}")
    else:
        st.warning("No se encontraron pasos para esta guía.")

elif opcion == "Agregar nueva guía":
    st.subheader("Agregar nueva guía")

    nueva_app = st.text_input("Nombre de la app")
    nueva_tarea = st.text_input("¿Qué quieres enseñar?")
    cantidad_pasos = st.number_input("¿Cuántos pasos tendrá?", min_value=1, max_value=15, value=3)

    pasos = []
    for i in range(cantidad_pasos):
        paso = st.text_input(f"Paso {i+1}", key=f"paso_{i}")
        pasos.append(paso)

    if st.button("Guardar guía"):
        if nueva_app.strip() and nueva_tarea.strip() and all(p.strip() for p in pasos):
            agregar_guia(nueva_app.strip(), nueva_tarea.strip(), pasos)
            st.success("✅ Guía guardada correctamente")
        else:
            st.error("Completa todos los campos antes de guardar.")

elif opcion == "Historial":
    st.subheader("Historial de dudas resueltas")

    docs = list(dudas_col.find({}, {"_id": 0}).sort("timestamp", -1))
    df = pd.DataFrame(docs)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Todavía no hay historial registrado.")