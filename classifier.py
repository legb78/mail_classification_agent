import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# load_dotenv()


MODEL_NAME = "qwen/qwen3-32b"


def classify_ticket(subject, body):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
Tu es un agent expert en gestion de tickets.
Analyse le ticket suivant et classe-le dans l'une des catégories exactes :

- Technique
- Administratif
- Accès
- Support
- Service

Puis attribue un niveau d'urgence parmi :

- Critique
- Élevée
- Modérée
- Faible
- Anodine

Ensuite génère une synthèse très courte (3–4 lignes max).

Répond STRICTEMENT au format JSON suivant :
{{
    "categorie": "...",
    "urgence": "...",
    "synthese": "..."
}}

TICKET :
SUJET : {subject}
CONTENU : {body}
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    text = response.choices[0].message["content"]

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Fallback en cas de sortie imprécise
        result = {
            "categorie": "Support",
            "urgence": "Modérée",
            "synthese": "Impossible de traiter correctement la réponse LLM."
        }

    return (
        result.get("categorie", "Support"),
        result.get("urgence", "Modérée"),
        result.get("synthese", "")
    )
