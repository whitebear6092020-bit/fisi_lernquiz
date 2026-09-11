"""
play_quiz.py
Eigenständiger Quiz-Player für Kollegen.
Benötigt kein Ollama und keine Extraktoren – nur Python, Streamlit und eine JSON-Datei.

Start in PyCharm-Terminal: streamlit run play_quiz.py
"""

import json
import os
import streamlit as st

st.set_page_config(page_title="FiSi Quiz-Player", page_icon="🎯", layout="centered")

st.title("🎯 FiSi Prüfungs-Trainer (Offline-Modus)")
st.caption("Teste dein Wissen – komplett lokal, ohne KI-Abhängigkeit.")

# Nach der JSON-Datei im Projektordner suchen
json_filename = "fisi_uebungsaufgaben.json"

if not os.path.exists(json_filename):
    st.error(f"❌ Die Datei `{json_filename}` wurde im Projektordner nicht gefunden!")
    st.info(
        "**So geht's:** Kopiere die von deinem Teamkollegen generierte `fisi_uebungsaufgaben.json` "
        "einfach direkt in diesen Projektordner und lade die Seite neu."
    )
    st.stop()

# JSON-Daten laden
with open(json_filename, "r", encoding="utf-8") as f:
    quizzes = json.load(f)

# Dokument-Auswahl (falls mehrere Dateien exportiert wurden)
selected_file = st.selectbox("Wähle ein Lernpaket / Dokument aus:", list(quizzes.keys()))
quiz_data = quizzes[selected_file]

st.divider()

# Quiz-Schleife durchlaufen
for idx, frage in enumerate(quiz_data):
    st.markdown(f"### Frage {idx + 1} von {len(quiz_data)}")
    st.write(f"**{frage.get('frage', '')}**")

    # Zustand für diese spezifische Frage im Session State speichern
    show_key = f"revealed_{selected_file}_{idx}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    typ = frage.get("typ", "offen")
    user_choice = None

    # Antwortmöglichkeiten darstellen (ohne Lösung zu verraten)
    if typ == "multiple_choice":
        options = frage.get("optionen", [])
        user_choice = st.radio(
            "Wähle deine Antwort:",
            options,
            key=f"choice_{selected_file}_{idx}",
            index=None  # Verhindert, dass automatisch die erste Option ausgewählt ist
        )
    else:
        user_choice = st.text_input("Deine Antwort eingeben:", key=f"choice_{selected_file}_{idx}")

    # Button zum Prüfen
    col1, col2 = st.columns([1, 4])
    with col1:
        if not st.session_state[show_key]:
            if st.button("Antwort prüfen", key=f"btn_check_{selected_file}_{idx}"):
                st.session_state[show_key] = True
                st.rerun()
        else:
            st.write("✅ *Ausgewertet*")

    # Lösung und Erklärung erst anzeigen, nachdem der Button gedrückt wurde
    if st.session_state[show_key]:
        richtige_loesung = frage.get("loesung", "")
        erklaerung = frage.get("erklaerung", "")

        st.success(f"🎯 **Richtige Lösung:** {richtige_loesung}")
        if erklaerung:
            st.info(f"💡 **Erklärung:** {erklaerung}")

        # Optional: Reset-Button, falls man die Frage nochmal probieren will
        if st.button("Frage zurücksetzen", key=f"reset_{selected_file}_{idx}"):
            st.session_state[show_key] = False
            st.rerun()

    st.markdown("---")

st.caption("Tipp: Du kannst die `fisi_uebungsaufgaben.json` jederzeit austauschen, um andere Themen zu lernen.")