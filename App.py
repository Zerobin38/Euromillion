import streamlit as st
from euromax_advanced import generate_pool, evaluate_combo, run_ga
import json, os

st.set_page_config(page_title="EuroMax Analyzer", layout="wide")

st.title("🎰 EuroMillions Optimizer")

mode = st.radio("Mode :", ["Basique", "Avancé"])

if mode == "Basique":
    st.write("Analyse simple des tirages récents.")
    if st.button("Rafraîchir et calculer"):
        pool = generate_pool(20)
        st.json(pool)

elif mode == "Avancé":
    st.sidebar.header("Paramètres avancés")
    pool_size = st.sidebar.slider("Taille du pool", 20, 200, 50)
    gens = st.sidebar.slider("Nombre de générations (GA)", 10, 200, 50)
    n_other = st.sidebar.number_input("Nombre de joueurs simulés", 100_000, 10_000_000, 1_000_000, step=100_000)
    jackpot = st.sidebar.number_input("Jackpot (€)", 10_000_000, 250_000_000, 100_000_000, step=1_000_000)

    if st.button("⚡ Générer le pool"):
        pool = generate_pool(pool_size)
        st.session_state.pool = pool
        st.success("Pool généré")

    if st.button("🚀 Lancer l’optimisation GA"):
        if "pool" not in st.session_state:
            st.error("Génère un pool d’abord")
        else:
            best = run_ga(st.session_state.pool, gens=gens, N_other=n_other, J=jackpot)
            st.json(best)
            with open("best_combo.json", "w") as f:
                json.dump(best, f)
            st.success("Résultat sauvegardé dans best_combo.json")
