# Générateur de grille EuroMillions – Streamlit

## Déploiement (Streamlit Cloud)
1. Crée un repo public sur GitHub et uploade `app.py`, `requirements.txt` et ce README.
2. Va sur https://streamlit.io/cloud → **New app** → connecte ton GitHub → choisis le repo.
3. Déploie. Tu obtiendras une URL publique utilisable sur mobile.

## Remarques
- La source publique utilisée est reducmiz.com. Le scraping est robuste (regex) et tolère les changements mineurs.
- Si la source est indisponible, l’appli bascule en mode aléatoire (avec avertissement).
- Jeu responsable : aucune combinaison n’a une probabilité supérieure. L’outil optimise seulement la diversité/anti-popularité.
