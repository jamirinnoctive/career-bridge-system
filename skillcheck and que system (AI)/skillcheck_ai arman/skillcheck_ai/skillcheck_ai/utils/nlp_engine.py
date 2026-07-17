
import spacy
from sentence_transformers import SentenceTransformer

nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")


def clean_text(text):
    doc = nlp(text.lower())
    return " ".join([t.lemma_ for t in doc if not t.is_stop])


def key_terms(text):
    """Single-token lemmas of the important words (nouns, proper nouns, verbs,
    adjectives) in a text, lowercased. Used for consistent set-based comparison
    between two texts — always normalized the same way on both sides."""
    doc = nlp(text.lower())
    return {
        t.lemma_ for t in doc
        if t.pos_ in ("NOUN", "PROPN", "VERB", "ADJ")
        and not t.is_stop and t.is_alpha and len(t) > 2
    }


def key_phrases(text):
    """Human-readable noun-chunk phrases (for display), longest/most specific first."""
    doc = nlp(text)
    terms = set()
    for chunk in doc.noun_chunks:
        words = [t.lemma_.lower() for t in chunk if not t.is_stop and t.is_alpha and len(t) > 2]
        if words:
            terms.add(" ".join(words))
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and token.is_alpha and len(token) > 2:
            terms.add(token.lemma_.lower())
    return sorted({t for t in terms if t}, key=len, reverse=True)
