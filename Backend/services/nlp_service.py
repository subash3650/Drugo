import os
import logging
import re
from difflib import get_close_matches

from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv("DEBUG_NLP", "0") == "1"
from transformers import pipeline, Pipeline, AutoTokenizer, AutoModelForSequenceClassification

def _safe_pipeline(task, model_name_list):
    for m in model_name_list:
        try:
            pipe = pipeline(task, model=m)
            logging.info(f"NLP: loaded {task} model '{m}'")
            return pipe
        except Exception as e:
            logging.warning(f"NLP: failed to load {task} model '{m}': {e}")
    raise RuntimeError(f"NLP: could not load any model for task '{task}' from list: {model_name_list}")

SENTIMENT_MODELS = [
    "siebert/sentiment-roberta-large-english",   
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  
    "distilbert-base-uncased-finetuned-sst-2-english", 
]

ZERO_SHOT_MODELS = [
    "facebook/bart-large-mnli",
    "valhalla/distilbart-mnli-12-1"
]

_sentiment_pipe = None
_zero_shot_pipe = None

def get_sentiment_pipe():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        _sentiment_pipe = _safe_pipeline("sentiment-analysis", SENTIMENT_MODELS)
    return _sentiment_pipe

def get_zero_shot_pipe():
    global _zero_shot_pipe
    if _zero_shot_pipe is None:
        try:
            _zero_shot_pipe = _safe_pipeline("zero-shot-classification", ZERO_SHOT_MODELS)
        except Exception:
            _zero_shot_pipe = None
    return _zero_shot_pipe

DRUG_KEYWORDS = {
    "pill","pills","tablet","xanax","percocet","oxy","oxycontin","mdma","molly","ecstasy",
    "cocaine","coke","heroin","weed","marijuana","maryjane","hash","meth","amphetamine",
    "ketamine","lsd","lsdtabs","tabs","opioid","opioids","dope","opiate",
    "g","gram","gms","pkg","package","bundle","bag","bags","q","dub","8ball",
    "xan","xannie","perc","percocet","oxy","oxy/p"
}

EMOJI_MAP = {
    "💊": "pill",
    "💉": "inject",
    "🌿": "weed",
    "🍁": "weed",
    "🎱": "cocaine", 
    "❄️": "cocaine",
    "🚚": "delivery",
    "📦": "package",
}

NORMALIZE_RULES = [
    (re.compile(r'(?i)\bx ?a ?n ?a ?x\b'), "xanax"),
    (re.compile(r'(?i)\bperc\b'), "perc"),
    (re.compile(r'(?i)\bmdma\b'), "mdma"),
    (re.compile(r'(?i)[^0-9a-z\s\U0001F300-\U0001F6FF]+'), " "), 
]

FUZZY_CUTOFF = 0.78

def normalize_text(text: str) -> str:
    txt = text
    for emo, token in EMOJI_MAP.items():
        if emo in txt:
            txt = txt.replace(emo, f" {token} ")
    for pattern, repl in NORMALIZE_RULES:
        txt = pattern.sub(repl, txt)
    txt = txt.lower()
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt

def _tokenize(text: str):
    return [t for t in re.split(r'[\s,;:.!?()\[\]"]+', text) if t]

def keyword_match(text: str):
    normalized = normalize_text(text)
    tokens = _tokenize(normalized)
    matched = set()

    for kw in DRUG_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', normalized):
            matched.add(kw)

    for t in tokens:
        if t in DRUG_KEYWORDS:
            matched.add(t)
    if not matched:
        for t in tokens:
            if len(t) < 3:
                continue
            close = get_close_matches(t, DRUG_KEYWORDS, n=1, cutoff=FUZZY_CUTOFF)
            if close:
                matched.add(close[0])

    return (len(matched) > 0, list(matched))

def zero_shot_check(text: str):
    pipe = get_zero_shot_pipe()
    if pipe is None:
        return None
    candidate_labels = ["drug-related", "not drug-related"]
    try:
        out = pipe(text, candidate_labels, multi_label=False)
        for lbl, score in zip(out["labels"], out["scores"]):
            if lbl == "drug-related":
                return float(score)
        return float(out["scores"][0]) if out and "scores" in out else None
    except Exception as e:
        logging.warning(f"Zero-shot classification failed: {e}")
        return None

def analyze_text(text: str):
    if not text:
        return {'sentiment': {'label': 'NEUTRAL', 'score': 0.0}, 'keyword_flag': False}
    try:
        sentiment_pipe = get_sentiment_pipe()
        sent_res = sentiment_pipe(text[:512])[0]
        label = sent_res.get("label")
        score = float(sent_res.get("score", 0.0))
    except Exception as e:
        logging.exception(f"Sentiment pipeline failed: {e}")
        label, score = ("POSITIVE", 0.5)
    kw_flag, kw_matches = keyword_match(text)
    zscore = None
    if not kw_flag:
        try:
            z = zero_shot_check(text)
            if z is not None:
                zscore = z
                if zscore >= 0.60:
                    kw_flag = True
        except Exception as e:
            logging.warning(f"Zero-shot fallback failed: {e}")

    result = {'sentiment': {'label': label, 'score': score}, 'keyword_flag': bool(kw_flag)}
    if DEBUG:
        meta = {
            'normalized_text': normalize_text(text),
            'keyword_matches': kw_matches,
            'zero_shot_score': zscore,
            'sentiment_raw': sent_res if 'sent_res' in locals() else None
        }
        result['meta'] = meta

    return result