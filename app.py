"""
app.py
FiSi Prüfungs-Trainer – Zeigt Lösungen erst bei korrekter Antwort
"""

import glob
import json
import os
import streamlit as st

st.set_page_config(page_title="FiSi Quiz-Player", page_icon="🎯", layout="centered")

st.title("🎯 FiSi Prüfungs-Trainer")
st.caption("Teste dein Wissen – interaktiv und prüfungsrelevant.")

# Automatisch nach allen .json-Dateien im Projektordner suchen
json_files = glob.glob("*.json")

if not json_files:
    st.error("❌ Keine JSON-Quiz-Dateien im Projektordner gefunden!")
    st.info(
        "**So geht's:** Lade mindestens eine `.json`-Datei mit Übungsaufgaben "
        "in den Ordner (oder auf GitHub hoch)."
    )
    st.stop()

# Dropdown zeigt den Namen der JSON-Datei
selected_json_file = st.selectbox("📂 Wähle ein Lernpaket aus:", json_files)

# Die JSON-Datei laden
with open(selected_json_file, "r", encoding="utf-8") as f:
    quizzes = json.load(f)

# Alle Fragen aus der JSON-Datei extrahieren
quiz_data = []
if isinstance(quizzes, dict):
    for key, value in quizzes.items():
        if isinstance(value, list):
            quiz_data.extend(value)
        elif isinstance(value, dict):
            quiz_data.append(value)
elif isinstance(quizzes, list):
    quiz_data = quizzes

if not quiz_data:
    st.warning("⚠️ Diese JSON-Datei enthält keine Fragen.")
    st.stop()

st.success(f"✅ Paket **{selected_json_file}** erfolgreich geladen ({len(quiz_data)} Fragen).")
st.divider()

# Quiz-Schleife durchlaufen
for idx, frage in enumerate(quiz_data):
    st.markdown(f"### Frage {idx + 1} von {len(quiz_data)}")
    st.write(f"**{frage.get('frage', '')}**")

    # Zustand für diese spezifische Frage im Session State speichern
    show_key = f"revealed_{selected_json_file}_{idx}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    typ = frage.get("typ", "offen")
    user_selected = []

    # Antwortmöglichkeiten darstellen
    if typ == "multiple_choice":
        options = frage.get("optionen", [])
        st.markdown("*Hinweis: Es können eine oder mehrere Antworten richtig sein.*")
        for opt_idx, option in enumerate(options):
            if st.checkbox(option, key=f"chk_{selected_json_file}_{idx}_{opt_idx}"):
                user_selected.append(option)
    else:
        user_selected = st.text_input("Deine Antwort eingeben:", key=f"choice_{selected_json_file}_{idx}")

    # Button zum Prüfen
    if not st.session_state[show_key]:
        if st.button("Antwort prüfen", key=f"btn_check_{selected_json_file}_{idx}"):
            st.session_state[show_key] = True
            st.rerun()
    else:
        loesung = frage.get("loesung", "")
        erklaerung = frage.get("erklaerung", "")
        
        is_correct = False
        if typ == "multiple_choice":
            correct_options = [opt for opt in options if opt.strip().lower() in loesung.lower()]
            
            # Strenger Mengenabgleich
            if correct_options and set(user_selected) == set(correct_options):
                is_correct = True
            elif not correct_options:
                if user_selected and all(opt.strip().lower() in loesung.lower() for opt in user_selected):
                    is_correct = True
        else:
            if isinstance(user_selected, str) and (user_selected.strip().lower() in loesung.lower() or loesung.lower() in user_selected.strip().lower()):
                is_correct = True

        # Visuelles Feedback & Bedingung für die Lösungsanzeige
        if is_correct:
            st.success("✅ **Richtig! Sehr gut gemacht.**")
            # Lösung und Erklärung werden NUR bei richtiger Antwort angezeigt!
            st.markdown(f"**🎯 Tatsächliche Lösung:** {loesung}")
            if erklaerung:
                st.info(f"💡 **Erklärung:** {erklaerung}")
        else:
            st.error("❌ **Leider falsch oder unvollständig!** Schade, versuche es noch einmal.")
            # Hier wird absichtlich KEINE Lösung angezeigt, damit man weiternageln / neu versuchen kann!

        # Button zum Zurücksetzen / Erneut versuchen
        if st.button("Frage zurücksetzen / Nochmal versuchen", key=f"reset_{selected_json_file}_{idx}"):
            st.session_state[show_key] = False
            st.rerun()

    st.markdown("---")
