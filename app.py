"""
app.py
FiSi Lern-Generator – Interaktiver Quiz-Player mit Dropdown & JSON-Dateinamen
"""

import json
import os
import streamlit as st

st.set_page_config(page_title="FiSi Quiz-Player", page_icon="🎯", layout="centered")

st.title("🎯 FiSi Prüfungs-Trainer")
st.caption("Teste dein Wissen – interaktiv und prüfungsrelevant.")

# Fester Name der JSON-Datei
json_filename = "fisi_uebungsaufgaben.json"

if not os.path.exists(json_filename):
    st.error(f"❌ Die Datei `{json_filename}` wurde im Projektordner nicht gefunden!")
    st.info(
        "**So geht's:** Stelle sicher, dass die `fisi_uebungsaufgaben.json` "
        "im selben Ordner liegt (oder auf GitHub hochgeladen wurde)."
    )
    st.stop()

# JSON-Daten laden
with open(json_filename, "r", encoding="utf-8") as f:
    quizzes = json.load(f)

# Dropdown-Menü beibehalten, aber anstelle des PDF-Namens den JSON-Namen anzeigen!
quiz_keys = list(quizzes.keys())

selected_key = st.selectbox(
    "Wähle ein Lernpaket aus:", 
    quiz_keys, 
    format_func=lambda x: f"{json_filename}" if len(quiz_keys) == 1 else f"{json_filename} (Bereich {quiz_keys.index(x) + 1})"
)

quiz_data = quizzes[selected_key]
st.divider()

# Quiz-Schleife durchlaufen
for idx, frage in enumerate(quiz_data):
    st.markdown(f"### Frage {idx + 1} von {len(quiz_data)}")
    st.write(f"**{frage.get('frage', '')}**")

    # Zustand für diese spezifische Frage im Session State speichern
    show_key = f"revealed_{selected_key}_{idx}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    typ = frage.get("typ", "offen")
    user_selected = []

    # Antwortmöglichkeiten darstellen
    if typ == "multiple_choice":
        options = frage.get("optionen", [])
        st.markdown("*Hinweis: Es können eine oder mehrere Antworten richtig sein.*")
        for opt_idx, option in enumerate(options):
            if st.checkbox(option, key=f"chk_{selected_key}_{idx}_{opt_idx}"):
                user_selected.append(option)
    else:
        user_selected = st.text_input("Deine Antwort eingeben:", key=f"choice_{selected_key}_{idx}")

    # Button zum Prüfen
    if not st.session_state[show_key]:
        if st.button("Antwort prüfen", key=f"btn_check_{selected_key}_{idx}"):
            st.session_state[show_key] = True
            st.rerun()
    else:
        loesung = frage.get("loesung", "")
        erklaerung = frage.get("erklaerung", "")
        
        is_correct = False
        if typ == "multiple_choice":
            # Ermittle alle Optionen, die laut dem Lösungstext korrekt sind
            correct_options = [opt for opt in options if opt.strip().lower() in loesung.lower()]
            
            # Strenger Mengenabgleich (kein Schummeln bei Multiple-Choice)
            if correct_options and set(user_selected) == set(correct_options):
                is_correct = True
            elif not correct_options:
                if user_selected and all(opt.strip().lower() in loesung.lower() for opt in user_selected):
                    is_correct = True
        else:
            if isinstance(user_selected, str) and (user_selected.strip().lower() in loesung.lower() or loesung.lower() in user_selected.strip().lower()):
                is_correct = True

        # Visuelles Feedback (Richtig vs. Falsch)
        if is_correct:
            st.success("✅ **Richtig! Sehr gut gemacht.**")
        else:
            st.error("❌ **Leider falsch oder unvollständig!**")

        # Offizielle Lösung und Erklärung anzeigen
        st.markdown(f"**🎯 Tatsächliche Lösung:** {loesung}")
        if erklaerung:
            st.info(f"💡 **Erklärung:** {erklaerung}")
            
        # Button zum Zurücksetzen
        if st.button("Frage zurücksetzen", key=f"reset_{selected_key}_{idx}"):
            st.session_state[show_key] = False
            st.rerun()

    st.markdown("---")
