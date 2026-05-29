from config import OLLAMA_BASE_URL, OPENAI_API_KEY, OLLAMA_MODEL
import ollama
from openai import OpenAI

openai_client = OpenAI(api_key=OPENAI_API_KEY)
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)


def build_rag_prompt(place: str, interests: list, real_places: list[dict], already_suggested: list[str]) -> str:
    if real_places:
        context_lines = "\n".join(
            f"- {p['name']} ({p['type']}) | {p['city']} {p['address']} "
            f"{'| ' + p['opening_hours'] if p['opening_hours'] else ''}"
            for p in real_places
        )
        context_block = f"""
        Voici une liste de lieux RÉELS et VÉRIFIÉS situés à {place} ou ses environs :
    {context_lines}
    Tu dois OBLIGATOIREMENT baser tes suggestions sur ces lieux réels.
    Ne génère PAS de lieux fictifs. Si tu proposes une activité, elle doit correspondre à un lieu de la liste.
    """

    else:
        context_block = f"Lieu : {place}. Génère des activités plausibles pour cette région."

    return f"""
    Tu es une API. Réponds UNIQUEMENT par un JSON valide. Aucun texte, aucun markdown.
    Format EXACT :
    {{
    "activities": [
        {{
          "title": "string",
          "description": "string (décris l'activité de façon engageante, 2-3 phrases)",
          "location": "string (nom exact du lieu + adresse si disponible)",
          "duration": "string"
        }}
      ]
    }}
    
    {context_block}
    Centres d'intérêt de l'utilisateur : {', '.join(interests) if isinstance(interests, list) else interests}
    Activités déjà proposées à exclure : {already_suggested}

    Propose 5 activités variées, adaptées aux centres d'intérêt, basées sur les lieux réels ci-dessus.
    """


def call_llm(source, prompt):
    if source == "openai":
        response = openai_client.chat.completions.create(model="gpt-4o-mini",
                                                         messages=[
                                                             {"role": "system",
                                                              "content":
                                                                  "Tu es un assistant expert"
                                                                  "en suggestions d'activités."},
                                                             {"role": "user", "content": prompt}
                                                         ],
                                                         temperature=0,
                                                         max_tokens=800)
        result_text = response.choices[0].message.content

    elif source == "ollama":
        response = ollama_client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            format="json",
            options={
                "temperature": 0
            }
        )
        result_text = response["response"]

    return result_text
