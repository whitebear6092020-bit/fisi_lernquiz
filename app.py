"""
app.py
FiSi Lern-Generator – Interaktiver Quiz-Player (Datenschutzfreundlich & Ohne PDF-Namen)
"""

import json
import os
import streamlit as st

st.set_page_config(page_title="FiSi Quiz-Player", page_icon="🎯", layout="centered")

st.title("🎯 FiSi Prüfungs-Trainer")
st.caption("Teste dein Wissen – interaktiv und prüfungsrelevant.")

# Fester Name der JSON-Datei, damit keine PDF-Namen verraten werden
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

# Alle Fragen aus allen im Hintergrund liegenden Dokumenten zu einem sauberen Paket zusammenfassen,
# sodass KEINE PDF- oder Word-Namen für den Nutzer sichtbar sind!
quiz_data = []
for source_name, questions in quizzes.items():
    if isinstance(questions, list):
        quiz_data.extend(questions)

st.success(f"📁 **Aktives Lernpaket:** `{json_filename}` ({len(quiz_data)} Fragen geladen)")
st.divider()

# Quiz-Schleife durchlaufen
for idx, frage in enumerate(quiz_data):
    st.markdown(f"### Frage {idx + 1} von {len(quiz_data)}")
    st.write(f"**{frage.get('frage', '')}**")

    # Zustand für diese spezifische Frage im Session State speichern
    show_key = f"revealed_{idx}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    typ = frage.get("typ", "offen")
    user_selected = []

    # Antwortmöglichkeiten darstellen
    if typ == "multiple_choice":
        options = frage.get("optionen", [])
        st.markdown("*Hinweis: Es können eine oder mehrere Antworten richtig sein.*")
        for opt_idx, option in enumerate(options):
            if st.checkbox(option, key=f"chk_{idx}_{opt_idx}"):
                user_selected.append(option)
    else:
        user_selected = st.text_input("Deine Antwort eingeben:", key=f"choice_{idx}")

    # Button zum Prüfen
    if not st.session_state[show_key]:
        if st.button("Antwort prüfen", key=f"btn_check_{idx}"):
            st.session_state[show_key] = True
            st.rerun()
    else:
        loesung = frage.get("loesung", "")
        erklaerung = frage.get("erklaerung", "")
        
        is_correct = False
        if typ == "multiple_choice":
            # Ermittle alle Optionen, die laut dem Lösungstext korrekt sind
            correct_options = [opt for opt in options if opt.strip().lower() in loesung.lower()]
            
            # Strenger, fehlerfreier Mengenabgleich (kein Schummeln bei Multiple-Choice möglich)
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
        if st.button("Frage zurücksetzen", key=f"reset_{idx}"):
            st.session_state[show_key] = False
            st.rerun()

    st.markdown("---")
