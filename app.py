import streamlit as st
import random
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Générateur de grille EuroMillions", page_icon="🎯")

st.title("🎯 Générateur de grille EuroMillions")
st.caption("⚠️ Jeu de hasard : chaque tirage est indépendant. Aucune grille n’a plus de chance de gagner. Jouez avec modération.")

# ------------------------------
# Scraping robuste des 200 à 500 derniers tirages (source publique)
# ------------------------------
def _to_int(text):
    m = re.search(r"\d+", text or "")
    return int(m.group()) if m else None

def get_last_draws(nb=500):
    url = f"https://www.reducmiz.com/resultat_fdj.php?jeu=euromillions&nb={nb}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    draws = []
    rows = soup.find_all("tr")
    if rows:
        rows = rows[1:]  # sauter l'entête
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 8:
            continue
        try:
            # Les colonnes 1..5 = numéros, 6..7 = étoiles (0 = date)
            nums = []
            for i in range(1, 6):
                v = _to_int(tds[i].get_text(strip=True))
                if v is None:
                    raise ValueError("num manquant")
                nums.append(v)

            stars = []
            for i in range(6, 8):
                v = _to_int(tds[i].get_text(strip=True))
                if v is None:
                    raise ValueError("étoile manquante")
                stars.append(v)

            # validations simples
            if all(1 <= n <= 50 for n in nums) and all(1 <= s <= 12 for s in stars):
                draws.append((nums, stars))
        except Exception:
            # On ignore proprement les lignes non conformes
            continue

    return draws

# ------------------------------
# Stats basiques : fréquences & retards
# ------------------------------
def compute_stats(draws):
    num_freq = {i: 0 for i in range(1, 51)}
    star_freq = {i: 0 for i in range(1, 13)}
    last_seen_num = {i: None for i in range(1, 51)}
    last_seen_star = {i: None for i in range(1, 13)}

    # index 0 = tirage le plus ancien
    for idx, (nums, stars) in enumerate(draws):
        for n in nums:
            num_freq[n] += 1
            last_seen_num[n] = idx
        for s in stars:
            star_freq[s] += 1
            last_seen_star[s] = idx

    # retard = nombre de tirages depuis la dernière apparition
    total = len(draws)
    num_delay = {n: (total - 1 - last_seen_num[n]) if last_seen_num[n] is not None else total for n in num_freq}
    star_delay = {s: (total - 1 - last_seen_star[s]) if last_seen_star[s] is not None else total for s in star_freq}

    return num_freq, star_freq, num_delay, star_delay

# ------------------------------
# Anti-popularité : filtrer patterns ultra courants
# ------------------------------
def looks_popular(nums):
    # évite suites, tous multiples de 5, ou plage trop resserrée
    nums = sorted(nums)
    if nums == list(range(nums[0], nums[0]+5)):  # suite parfaite
        return True
    if all(n % 5 == 0 for n in nums):
        return True
    if nums[-1] - nums[0] <= 8:  # trop groupé
        return True
    return False

# ------------------------------
# Génération de grilles
# ------------------------------
def make_grids(num_freq, star_freq, num_delay, star_delay, seed=None):
    rng = random.Random(seed)

    # rangs par fréquence et par retard
    top_nums = [n for n, _ in sorted(num_freq.items(), key=lambda x: (-x[1], x[0]))[:15]]
    top_stars = [s for s, _ in sorted(star_freq.items(), key=lambda x: (-x[1], x[0]))[:6]]

    delayed_nums = [n for n, _ in sorted(num_delay.items(), key=lambda x: (-x[1], x[0]))[:15]]
    delayed_stars = [s for s, _ in sorted(star_delay.items(), key=lambda x: (-x[1], x[0]))[:6]]

    # équilibres
    eq_pool_nums = sorted(set(top_nums[:8] + delayed_nums[:8]))
    eq_pool_stars = sorted(set(top_stars[:3] + delayed_stars[:3]))

    def sample_from(pool, k):
        sel = set()
        tries = 0
        while len(sel) < k and tries < 100:
            sel.add(rng.choice(pool))
            tries += 1
        return sorted(sel)

    G = {}
    G["Top"] = (sample_from(top_nums, 5), sample_from(top_stars, 2))
    G["Retard"] = (sample_from(delayed_nums, 5), sample_from(delayed_stars, 2))
    G["Équilibre"] = (sample_from(eq_pool_nums, 5), sample_from(eq_pool_stars, 2))

    # Aléatoire pondéré par (fréquence + retard)
    def weights(d1, d2, alpha=0.6, beta=0.4):
        max1 = max(d1.values()) or 1
        max2 = max(d2.values()) or 1
        return {k: alpha*(d1[k]/max1) + beta*(d2[k]/max2) for k in d1}

    w_num = weights(num_freq, num_delay)
    w_star = weights(star_freq, star_delay)

    def weighted_sample(wmap, k):
        keys = list(wmap.keys())
        vals = [wmap[k] for k in keys]
        # normalisation
        s = sum(vals) or 1.0
        vals = [v/s for v in vals]
        chosen = set()
        while len(chosen) < k:
            r = rng.random()
            acc = 0.0
            for key, p in zip(keys, vals):
                acc += p
                if r <= acc:
                    chosen.add(key)
                    break
        return sorted(chosen)

    G["Aléatoire"] = (weighted_sample(w_num, 5), weighted_sample(w_star, 2))

    # Grille spéciale du soir = meilleure anti-popularité parmi Top/Équilibre/Retard
    candidates = [G["Top"], G["Équilibre"], G["Retard"], G["Aléatoire"]]
    special = None
    for (nums, stars) in candidates:
        if not looks_popular(nums):
            special = (nums, stars)
            break
    if special is None:
        special = candidates[0]
    G["SPECIAL"] = special

    return G

# ------------------------------
# UI
# ------------------------------
seed = st.slider("🔁 Variabilité (graine aléatoire)", 0, 9999, 42, help="Change la graine pour obtenir d'autres propositions.")
if st.button("Générer mes grilles du soir"):
    try:
        draws = get_last_draws(500)
    except Exception as e:
        st.error("Impossible de récupérer les tirages (source indisponible). On passe en mode purement aléatoire.")
        draws = []

    if not draws:
        # fallback minimal : aucun historique → on propose du pur aléatoire (responsable)
        num_freq = {i: 1 for i in range(1, 51)}
        star_freq = {i: 1 for i in range(1, 13)}
        num_delay = {i: 1 for i in range(1, 51)}
        star_delay = {i: 1 for i in range(1, 13)}
    else:
        num_freq, star_freq, num_delay, star_delay = compute_stats(draws)

    grids = make_grids(num_freq, star_freq, num_delay, star_delay, seed=seed)

    st.subheader("🧮 Résumé analytique (ultra synthèse)")
    st.write("• Fréquences + retards combinés. • Filtre anti-popularité. • Aucune promesse de gain.")

    st.subheader("📋 GRILLES SUGGÉRÉES")
    for key in ["Top", "Retard", "Équilibre", "Aléatoire"]:
        nums, stars = grids[key]
        st.write(f"{key} : {nums} ★ {stars}")

    s_nums, s_stars = grids["SPECIAL"]
    st.success(f"🎯 **GRILLE SPÉCIALE CE SOIR** : {s_nums} ★ {s_stars}")    
