from transformers import pipeline
# load sentiment pipeline once
sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

DRUG_KEYWORDS = {"pill","💊","molly","weed","coke","pkg","bundle","g"}  # extend for prototype

def analyze_text(text: str):
    res = sentiment_pipe(text[:512])[0]
    lower = text.lower()
    kw_flag = any(k in lower for k in DRUG_KEYWORDS)
    return {'sentiment': res, 'keyword_flag': kw_flag}
