import re

def split_into_sections(snippet: str, max_sections: int = 4):
    sentences = re.split(r'(?<=[.!?]) +', snippet.strip())
    if not sentences:
        return [snippet]
    avg = max(1, len(sentences) // max_sections)
    return [" ".join(sentences[i:i+avg]) for i in range(0, len(sentences), avg)][:max_sections]