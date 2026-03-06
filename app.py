import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF
import pandas as pd

st.set_page_config(page_title="Calculadora Sueño Bebé", page_icon="🌙", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #F8F1E9; }
    .title { color: #0066FF; font-size: 2.3rem; font-weight: bold; text-align: center; }
    .subtitle { color: #8FBF9F; text-align: center; font-size: 1.15rem; }
    .sids-alert { background-color: #FFEBEE; padding: 18px; border-radius: 12px; border-left: 6px solid #FF4D6B; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">🌙 Calculadora Instantánea del Sueño de tu Bebé</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Menos de 5 minutos • Personalizado • ±30 minutos</p>', unsafe_allow_html=True)

# ================== BASE DE DATOS ==================
data = {
    "0-4 semanas": {"wake_min": 55, "num_siestas": 6, "diurno_h": 8.0, "nocturno_h": 8.5, "total_h": 16.5, "cues": "bostezos intensos, movimientos espasmódicos, chupar manos, mirada perdida"},
    "5-8 semanas": {"wake_min": 75, "num_siestas": 5, "diurno_h": 7.0, "nocturno_h": 9.0, "total_h": 16.0, "cues": "frotar ojos, tirar orejas, llanto suave"},
    "9-12 semanas": {"wake_min": 95, "num_siestas": 4, "diurno_h": 6.0, "nocturno_h": 9.5, "total_h": 15.5, "cues": "frotar ojos/orejas, mirar al vacio"},
    "3-4 meses": {"wake_min": 120, "num_siestas": 4, "diurno_h": 5.0, "nocturno_h": 10.0, "total_h": 15.0, "cues": "bostezo fuerte, clingy, menos interes en juguetes"},
    "5-6 meses": {"wake_min": 150, "num_siestas": 3, "diurno_h": 4.25, "nocturno_h": 10.5, "total_h": 14.75, "cues": "frotar cara, whining, second wind"},
    "7-9 meses": {"wake_min": 180, "num_siestas": 3, "diurno_h": 3.5, "nocturno_h": 10.75, "total_h": 14.25, "cues": "frotar ojos, hiperactividad + llanto"},
    "10-12 meses": {"wake_min": 210, "num_siestas": 2, "diurno_h": 3.0, "nocturno_h": 11.0, "total_h": 14.0, "cues": "clingy fuerte, desinteres, quejidos"},
    "13-18 meses": {"wake_min": 240, "num_siestas": 2, "diurno_h": 2.5, "nocturno_h": 11.0, "total_h": 13.5, "cues": "tantrums, pedir nana, torpeza"},
    "19-24 meses": {"wake_min": 270, "num_siestas": 1, "diurno_h": 2.0, "nocturno_h": 11.0, "total_h": 13.0, "cues": "hiperactividad → meltdown, pedir dormir"}
}

edad = st.selectbox("Edad aproximada del bebé", options=list(data.keys()), index=4)
hora_despertar = st.time_input("Hora habitual de despertar", value=datetime.strptime("07:00", "%H:%M").time(), step=300)

# ================== 0-3 MESES - RITMO DE SUPERVIVENCIA ==================
if edad in ["0-4 semanas", "5-8 semanas"]:
    st.markdown("### 🍼 Ritmo de Supervivencia a Demanda (0-3 meses)")
    st.info("En los primeros 3 meses **NO se recomienda horario rígido**. El sueño debe ser completamente a demanda.")

    st.markdown("**Recomendaciones clave:**")
    st.markdown("- Ventanas de vigilia cortas: 45-60 min (0-4 semanas) / 60-90 min (5-8 semanas)\n- Alimentación y sueño a demanda\n- Observa siempre las señales de tu bebé")

    st.markdown('<div class="sids-alert">', unsafe_allow_html=True)
    st.markdown("**🚨 ALERTAS IMPORTANTES DE SEGURIDAD (SIDS)**\n"
                "• Acuesta siempre boca arriba\n"
                "• Superficie firme y plana\n"
                "• Sin almohadas, mantas ni peluches\n"
                "• Comparte habitación pero NO cama\n"
                "• Temperatura 18-22°C")
    st.markdown('</div>', unsafe_allow_html=True)

    def create_pdf_0_3():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Ritmo de Supervivencia a Demanda - 0-3 meses", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, "Este documento NO es un horario rigido.\n\n"
                            "Ventanas de vigilia:\n"
                            "- 0-4 semanas: 45-60 minutos\n"
                            "- 5-8 semanas: 60-90 minutos\n\n"
                            "ALERTAS SIDS:\n"
                            "- Boca arriba siempre\n"
                            "- Superficie firme\n"
                            "- Sin objetos suaves en la cuna\n"
                            "- Habitacion compartida sin cama compartida")
        return pdf.output(dest="S").encode("latin-1")

    if st.button("📥 Descargar Ritmo de Supervivencia (PDF)", type="primary"):
        pdf_bytes = create_pdf_0_3()
        st.download_button("Guardar PDF", data=pdf_bytes, file_name="ritmo_supervivencia_0_3_meses.pdf", mime="application/pdf")

else:
    # ================== HORARIO NORMAL (3+ meses) ==================
    info = data[edad]
    num_siestas = st.slider("¿Cuántas siestas quieres planificar hoy?", 1, 6, info["num_siestas"])
    duracion_siesta = st.number_input("Duración promedio de cada siesta (minutos)", 30, 180, int(info["diurno_h"] / info["num_siestas"] * 60))

    current_time = datetime.combine(datetime.today(), hora_despertar)
    schedule = []

    schedule.append({"Actividad": "Despertar", "Hora": current_time.strftime("%I:%M %p"), "Rango": "±30 min"})

    for i in range(num_siestas):
        nap_start = current_time + timedelta(minutes=info["wake_min"])
        nap_end = nap_start + timedelta(minutes=duracion_siesta)
        schedule.append({"Actividad": f"Siesta {i+1}", "Hora": f"{nap_start.strftime('%I:%M %p')} - {nap_end.strftime('%I:%M %p')}", "Rango": "±30 min"})
        current_time = nap_end

    bedtime = current_time + timedelta(minutes=int(info["wake_min"] * 0.75))
    if bedtime.hour > 21:
        bedtime = bedtime - timedelta(minutes=60)

    schedule.append({"Actividad": "Hora de dormir sugerida", "Hora": bedtime.strftime("%I:%M %p"), "Rango": "±30 min"})

    df = pd.DataFrame(schedule)
    st.markdown("### ✅ Tu horario mágico para hoy")
    st.dataframe(df, use_container_width=True, hide_index=True)

    total = round(num_siestas * duracion_siesta / 60, 1)
    st.markdown(f"**Total sueño estimado hoy:** {total} h diurnas + {info['nocturno_h']} h nocturnas = **{round(total + info['nocturno_h'],1)} h**")

    # PDF limpio y estable
    def create_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Horario del Sueno", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        for row in schedule:
            pdf.cell(0, 8, f"{row['Actividad']}: {row['Hora']} ({row['Rango']})", ln=1)
        pdf.ln(10)
        pdf.cell(0, 8, f"Total sueno estimado: {round(total + info['nocturno_h'],1)} horas", ln=1)
        return pdf.output(dest="S").encode("latin-1")

    if st.button("📥 Descargar Horario (PDF)", type="primary"):
        pdf_bytes = create_pdf()
        st.download_button("Guardar PDF", data=pdf_bytes, file_name=f"horario_sueño_{edad}.pdf", mime="application/pdf")

st.caption("💡 Hecho con ❤️ para mamás agotadas • Criar Mejor.")
