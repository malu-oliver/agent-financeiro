import unicodedata
import re
STOPWORDS = {"de", "para", "com", "em", "o", "a", "os", "as", "um", "uma"}

def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo acentos, stopwords e caracteres especiais"""
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    palavras = [p for p in texto.split() if p not in STOPWORDS]
    return " ".join(palavras)

def clean_text(text: str) -> str:
    """Remove acentos e caracteres especiais, convertendo para minúsculas."""
    text = str(text).lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^a-z0-9\s]", "", text) # Remove caracteres não alfanuméricos
    return text.strip()

def validate_input_regex(text: str, pattern: str) -> bool:
    """Valida um texto contra um padrão regex."""
    return bool(re.match(pattern, text))

