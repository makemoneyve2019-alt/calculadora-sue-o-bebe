import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF          # ←←← CORREGIDO (paquete fpdf)
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="🌙 Calculadora Sueño Bebé",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos calmantes
st.markdown("""
<style>
    .stApp { background-color: #2C3E50; }
    .title { color: #6B4E7E; font-size: 2.3rem; font-weight: bold; text-align: center; margin-bottom: 0; }
    .subtitle { color: #8FBF9F; text-align: center; font-size: 1.15rem; margin-top: 0; }
    .stButton>button { background-color: #6B4E7E; color: white; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="title">🌙 Calculadora Instantánea del Sueño de tu Bebé</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Menos de 5 minutos • Personalizado • ±30 minutos</p>', unsafe_allow_html=True)

# Base de datos pediátrica
data = {
    "0-4 semanas": {"wake_min": 55, "num_siestas": 6, "diurno_h": 8.0, "nocturno_h": 8.5, "total_h": 16.5,
                    "cues": "bostezos intensos, movimientos espasmódicos, chupar manos, mirada perdida"},
    "5-8 semanas": {"wake_min": 75, "num_siestas": 5, "diurno_h": 7.0, "nocturno_h": 9.0, "total_h": 16.0,
                    "cues": "frotar ojos, tirar orejas, llanto suave"},
    "9-12 semanas": {"wake_min": 95, "num_siestas": 4, "diurno_h": 6.0, "nocturno_h": 9.5, "total_h": 15.5,
                     "cues": "frotar ojos/orejas, mirar al vacío"},
    "3-4 meses": {"wake_min": 120, "num_siestas": 4, "diurno_h": 5.0, "nocturno_h": 10.0, "total_h": 15.0,
                  "cues": "bostezo fuerte, clingy, menos interés en juguetes"},
    "5-6 meses": {"wake_min": 150, "num_siestas": 3, "diurno_h": 4.25, "nocturno_h": 10.5, "total_h": 14.75,
                  "cues": "frotar cara, whining, second wind"},
    "7-9 meses": {"wake_min": 180, "num_siestas": 3, "diurno_h": 3.5, "nocturno_h": 10.75, "total_h": 14.25,
                  "cues": "frotar ojos, hiperactividad + llanto"},
    "10-12 meses": {"wake_min": 210, "num_siestas": 2, "diurno_h": 3.0, "nocturno_h": 11.0, "total_h": 14.0,
                    "cues": "clingy fuerte, desinterés, quejidos"},
    "13-18 meses": {"wake_min": 240, "num_siestas": 2, "diurno_h": 2.5, "nocturno_h": 11.0, "total_h": 13.5,
                    "cues": "tantrums, pedir nana, torpeza"},
    "19-24 meses": {"wake_min": 270, "num_siestas": 1, "diurno_h": 2.0, "nocturno_h": 11.0, "total_h": 13.0,
                    "cues": "hiperactividad → meltdown, pedir dormir"}
}

# Inputs
edad = st.selectbox("Edad aproximada del bebé", options=list(data.keys()), index=4)
hora_despertar = st.time_input("Hora habitual de despertar", value=datetime.strptime("07:00", "%H:%M").time(), step=300)
num_siestas = st.slider("¿Cuántas siestas quieres planificar hoy?", min_value=1, max_value=6, value=data[edad]["num_siestas"])
duracion_siesta_min = st.number_input("Duración promedio de cada siesta (minutos)", 
                                      min_value=30, max_value=180, value=int(data[edad]["diurno_h"] / data[edad]["num_siestas"] * 60))

# Cálculo
info = data[edad]
wake_window = timedelta(minutes=info["wake_min"])
nap_duration = timedelta(minutes=duracion_siesta_min)

current_time = datetime.combine(datetime.today(), hora_despertar)
schedule = []

schedule.append({
    "Actividad": "Despertar",
    "Hora": current_time.strftime("%I:%M %p"),
    "Rango": f"{(current_time - timedelta(minutes=30)).strftime('%I:%M %p')} - {(current_time + timedelta(minutes=30)).strftime('%I:%M %p')}"
})

for i in range(num_siestas):
    nap_start = current_time + wake_window
    nap_end = nap_start + nap_duration
    schedule.append({
        "Actividad": f"Siesta {i+1}",
        "Hora": f"{nap_start.strftime('%I:%M %p')} - {nap_end.strftime('%I:%M %p')}",
        "Rango": f"{(nap_start - timedelta(minutes=30)).strftime('%I:%M %p')} - {(nap_end + timedelta(minutes=30)).strftime('%I:%M %p')}"
    })
    current_time = nap_end

bedtime = current_time + timedelta(minutes=int(info["wake_min"] * 0.75))
if bedtime.hour > 21:
    bedtime = bedtime - timedelta(minutes=60)

schedule.append({
    "Actividad": "Hora de dormir sugerida",
    "Hora": bedtime.strftime("%I:%M %p"),
    "Rango": f"{(bedtime - timedelta(minutes=30)).strftime('%I:%M %p')} - {(bedtime + timedelta(minutes=30)).strftime('%I:%M %p')}"
})

df = pd.DataFrame(schedule)

# Resultados
st.markdown("### ✅ Tu horario mágico para hoy")
st.dataframe(df, use_container_width=True, hide_index=True)

total_diurno = round(num_siestas * duracion_siesta_min / 60, 1)
total_24h = round(total_diurno + info["nocturno_h"], 1)

st.markdown(f"""
**Total sueño estimado hoy:**  
**{total_diurno} h diurnas + {info['nocturno_h']} h nocturnas = {total_24h} h**
""")

st.info(f"**Señales de sueño para tu bebé ({edad}):** {info['cues']}")
st.caption("💡 Recuerda: siempre observa las señales de TU bebé. Esto es una guía aproximada ±30 min.")

# Función PDF (sin emojis, 100% compatible)
def create_pdf():
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(107, 78, 126)
    pdf.cell(0, 12, "Calculadora Instantanea del Sueno de tu Bebe", ln=1, align="C")
    pdf.ln(8)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Edad: {edad}   |   Despertar: {hora_despertar.strftime('%I:%M %p')}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    for row in schedule:
        pdf.cell(0, 8, f"{row['Actividad']}: {row['Hora']}   ({row['Rango']})", ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Total sueño estimado: {total_24h} horas", ln=1)
    pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "Recuerda: cada bebé es único. Usa siempre sus señales de sueño. ¡Dulces sueños!")
    
    return pdf.output(dest="S").encode("latin-1")

# Botón descarga
if st.button("📥 Descargar mi horario en PDF", type="primary", use_container_width=True):
    pdf_bytes = create_pdf()
    st.download_button(
        label="💾 Guardar PDF ahora",
        data=pdf_bytes,
        file_name=f"horario_sueño_{edad.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("---")
st.markdown("Hecho con ❤️ para mamás agotadas • Criar Mejor")
