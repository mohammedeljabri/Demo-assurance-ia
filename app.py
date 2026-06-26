"""
Bank Insurance AI Agent — Démo publique
=======================================
Analyse automatique de contrats d'assurance.

IMPORTANT — Démo vs Produit
  - DÉMO (ce fichier) : s'appuie sur l'API Mistral (société française, serveurs en
    Europe), parce qu'un hébergement public gratuit ne peut pas faire tourner un
    modèle téléchargé en local.
  - PRODUIT : le même agent tourne avec Mistral exécuté 100% EN LOCAL, sans qu'aucune
    donnée ne quitte l'infrastructure du client.

La logique d'analyse (prompt, structure) est IDENTIQUE à celle du produit.
"""

import os
import streamlit as st
import pdfplumber
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Bank Insurance AI Agent — Démo",
    page_icon="🏦",
    layout="centered",
)

MODELE = "mistral-small-latest"  # modèle Mistral (français), rapide et économique

# Prompt système — identique au produit
SYSTEM_PROMPT = """Tu es un assistant bancaire expert.
Tu analyses les contrats d'assurance et extrais les informations clés.
Tu réponds toujours en français de manière professionnelle et structurée."""

# Contrat d'exemple 100% FICTIF (données générées, aucune personne ni société réelle)
CONTRAT_EXEMPLE = """ASSURANCES EXEMPLE SA — Document de démonstration (société fictive)
CONTRAT D'ASSURANCE MULTIRISQUE HABITATION
Référence : MRH-DEMO-0001

1. INFORMATIONS SUR L'ASSURÉ (fictif)
Nom et prénom : DUPONT Marie
Adresse : 10 Rue de l'Exemple, 00000 Villedémo
Email : demo@exemple.fr
Numéro client : CLI-DEMO-0001
Statut : Locataire

2. BIEN ASSURÉ
Appartement — résidence principale, 68 m², 3 pièces (T3)
Valeur déclarée du mobilier : 25 000 €

3. GARANTIES SOUSCRITES
Incendie & Explosion : plafond 150 000 €, franchise 300 €
Dégât des eaux : plafond 80 000 €, franchise 150 €
Vol & Vandalisme : plafond 25 000 €, franchise 200 €
Responsabilité Civile : plafond 1 000 000 €, franchise 0 €
Bris de glace : plafond 5 000 €, franchise 50 €
Catastrophes naturelles : plafond 150 000 €, franchise 380 €
Protection juridique : plafond 15 000 € (option)
Assistance 24h/24 : frais réels

4. EXCLUSIONS PRINCIPALES
- Dommages intentionnels causés par l'assuré ou sa famille
- Dommages de guerre, émeutes ou actes terroristes (sauf garantie spécifique)
- Usure normale, défaut d'entretien, vétusté
- Vol sans effraction constatée
- Dommages survenus lors d'une location saisonnière non déclarée
- Pertes financières indirectes consécutives à un sinistre matériel

5. COTISATION
Prime annuelle TTC : 450,00 € (paiement mensuel de 37,50 €)

6. OBLIGATIONS DE L'ASSURÉ
- Déclarer tout sinistre sous 5 jours ouvrés (2 jours en cas de vol)
- Informer la compagnie de tout changement de situation
- Ne pas réparer avant l'intervention d'un expert mandaté
- Dépôt de plainte obligatoire en cas de vol
"""


# --------------------------------------------------------------------------
# Fonctions
# --------------------------------------------------------------------------
def get_api_key() -> str:
    """Récupère la clé API depuis l'environnement ou les secrets Streamlit."""
    key = os.environ.get("MISTRAL_API_KEY", "")
    if not key:
        try:
            key = st.secrets["MISTRAL_API_KEY"]
        except Exception:
            key = ""
    return key


def lire_pdf(fichier) -> str:
    """Extrait le texte d'un PDF avec pdfplumber."""
    texte = ""
    with pdfplumber.open(fichier) as pdf:
        for page in pdf.pages:
            texte += (page.extract_text() or "") + "\n"
    return texte


def construire_messages(texte_contrat: str):
    """Construit les messages envoyés au modèle (identique au produit)."""
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
Analyse ce contrat d'assurance et extrais :
1. Type de contrat
2. Garanties principales
3. Exclusions importantes
4. Montant de la prime
5. Points de vigilance

Contrat :
{texte_contrat}
"""
        ),
    ]


def analyser_en_streaming(texte_contrat: str, api_key: str):
    """Appelle Mistral et renvoie un générateur de tokens (pour st.write_stream)."""
    llm = ChatMistralAI(model=MODELE, api_key=api_key, temperature=0)
    for chunk in llm.stream(construire_messages(texte_contrat)):
        yield chunk.content


# --------------------------------------------------------------------------
# Interface
# --------------------------------------------------------------------------
st.title("🏦 Bank Insurance AI Agent")
st.caption(
    "Analyse automatique de contrats d'assurance — secteur banque & assurance français"
)

st.info(
    "🔒 **Démo** sur un contrat d'exemple **généré** (aucune donnée réelle). "
    "En déploiement réel, le même moteur tourne **100% en local**, sans qu'aucune "
    "donnée ne quitte votre infrastructure."
)

api_key = get_api_key()
if not api_key:
    st.error(
        "Clé API Mistral manquante. Ajoutez `MISTRAL_API_KEY` dans les secrets "
        "de l'application (voir le guide de déploiement)."
    )
    st.stop()

onglet1, onglet2 = st.tabs(["📄 Contrat d'exemple", "⬆️ Uploader un PDF"])

texte_a_analyser = None

with onglet1:
    st.write("Analysez le contrat d'exemple fourni (multirisque habitation, données fictives).")
    with st.expander("Voir le contrat d'exemple"):
        st.text(CONTRAT_EXEMPLE)
    if st.button("Analyser le contrat d'exemple", type="primary", key="btn_exemple"):
        texte_a_analyser = CONTRAT_EXEMPLE

with onglet2:
    st.warning("⚠️ Démo : n'uploadez **pas** de contrat réel ni de données personnelles.")
    fichier = st.file_uploader("Contrat au format PDF", type="pdf")
    if fichier is not None and st.button("Analyser le PDF", type="primary", key="btn_pdf"):
        with st.spinner("Lecture du PDF..."):
            texte_a_analyser = lire_pdf(fichier)

if texte_a_analyser:
    st.divider()
    st.subheader("📋 Analyse du contrat")
    st.write_stream(analyser_en_streaming(texte_a_analyser, api_key))
    st.caption(
        "⚙️ Démo via l'API Mistral (France / UE). En production : Mistral exécuté 100% en local."
    )
