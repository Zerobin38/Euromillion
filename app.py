import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random

# -----------------------------
# Fonction pour récupérer les derniers tirages
# -----------------------------
def get_last_draws(n=200):
    url = f"https://www.reducmiz.com/resultat_fdj.php?jeu=euromillions&nb={n}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    
    draws = []
    for row in soup.select("tr")[1:]:  # on saute l'entête
        cols = row.text.strip().split()
        if len(cols) >= 7:
            nums = list(map(int, cols[1:6]))
            stars = list(map(int, cols[6:8]))
            draws.append((nums, stars))
    return draws

# -----------------------------
# Génération de grilles
# -----------------------------
def generate_grids(draws):
    # Compter fréquences
    all_nums = [n for d in draws for n in d[0]]
    all_stars = [s for d in draws for s in d[1]]
    num_freq = pd.Series(all_nums).value_counts().sort_values(ascending=False)
    star_freq = pd.Series(all_stars).value_counts().sort_values(ascending=False)

    # Grille Top (les plus fréquents)
    top_nums = list(num_freq.index[:5])
    top_stars = list(star_freq.index[:2])

    # Grille Retard (les moins sortis)
    low_nums = list(num_freq.index[-5:])
    low_stars = list(star_freq.index[-2:])

    # Grille Equilibre (mix haut/bas)
    eq_nums = list(num_freq.index[:3]) + list(num_freq.index[-2:])
    eq_stars = [star_freq.index[0], star_freq.index[-1]]

    # Grille Aléatoire (mais unique)
    rand_nums = sorted(random.sample(range(1, 51), 5))
    rand_stars = sorted(random.sample(range(1, 13), 2))

    return {
        "Top": (sorted(top_nums), sorted(top_stars)),
        "Retard": (sorted(low_nums), sorted(low_stars)),
        "Equilibre": (sorted(eq_nums), sorted(eq_stars)),
        "Aléatoire": (rand_nums, rand_stars),
    }

# -----------------------------
# Interface Streamlit
# -----------------------------
st.title("🎯 Générateur de grilles EuroMillions")
st.write("⚠️ Jeu de hasard : aucune grille n’a plus de chance de gagner. Jeu responsable !")

if st.button("Générer mes grilles du soir"):
    draws = get_last_draws()
    grilles = generate_grids(draws)

    for name, (nums, stars) in grilles.items():
        st.write(f"**{name}** : {nums} ★ {stars}")

    st.success(f"🎯 Grille spéciale du soir : {grilles['Equilibre'][0]} ★ {grilles['Equilibre'][1]}")
