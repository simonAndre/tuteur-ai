import re
from textwrap import shorten

CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)

# Heuristique simple: si trop de code / réponse trop procédurale, on reformule en indices.
def sanitize_and_demote_solutions(text: str, level: int) -> str:
    # 1) Limiter les gros blocs de code
    def shrink_block(m):
        block = m.group(0)
        lines = block.splitlines()
        if len(lines) > 8:
            # Remplacer par un pseudo-code d'indice
            return (
                "```pseudo\n" 
                "Étapes (esquisse) :\n"
                "1) Identifier les entrées/sorties\n"
                "2) Décomposer en sous-fonctions\n"
                "3) Écrire des tests simples\n"
                "4) Implémenter itérativement\n" 
                "```"
            )
        return block

    text = CODE_BLOCK_RE.sub(shrink_block, text)

    # 2) Si la réponse paraît être une solution clé-en-main (mots clés)
    strong_solution_markers = [
        "voici la solution", "la solution complète", "code final", "copie-colle",
    ]
    if any(k in text.lower() for k in strong_solution_markers):
        text = (
            "Plutôt que la solution complète, suis ces indices :\n"
            "- Reformule l'objectif avec tes mots.\n"
            "- Identifie la donnée minimale à manipuler.\n"
            "- Écris un test rapide (entrée → sortie attendue).\n"
            "- Implémente une première étape et vérifie.\n"
        )

    # 3) Adapter le degré d'aide
    if level == 1:
        text = limit_sentences(text, max_sentences=3)
    elif level == 2:
        text = limit_sentences(text, max_sentences=5)
    else:  # level 3
        text = limit_sentences(text, max_sentences=6)

    # 4) Toujours finir par une question de relance légère
    if not text.strip().endswith("?"):
        text = text.rstrip() + "\n\nQuelle serait ta prochaine petite étape de vérification ?"

    return text


def limit_sentences(text: str, max_sentences: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= max_sentences:
        return text
    keep = " ".join(sentences[:max_sentences])
    return keep