from services.db import get_db
from datetime import datetime

W_KEYWORD = 0.6
W_SENTIMENT = 0.4
HIGH_RISK_TH = 0.75
MED_RISK_TH = 0.4

def compute_score(kw_flag, sentiment):
    s = 0.0
    if kw_flag:
        s += W_KEYWORD
    mag = sentiment.get('score', 0)
    if sentiment.get('label') == 'NEGATIVE':
        s += W_SENTIMENT * mag
    else:
        s += W_SENTIMENT * (1 - mag)
    return min(1.0, s)

def _to_json_serializable(doc: dict):
    if not doc:
        return None
    if "_id" in out:
        try:
            out["_id"] = str(out["_id"])
        except Exception:
            out["_id"] = out["_id"] 
    return out

def update_user_and_score(user_id, platform, payload, nlp_res):
    db = get_db()
    score = compute_score(nlp_res['keyword_flag'], nlp_res['sentiment'])
    level = 'LOW'
    if score >= HIGH_RISK_TH:
        level = 'HIGH'
    elif score >= MED_RISK_TH:
        level = 'MEDIUM'
    doc = {
        'user_id': user_id,
        'platform': platform,
        'timestamp': payload.get('timestamp', datetime.utcnow().isoformat()),
        'score': score,
        'level': level,
        'keyword_flag': nlp_res['keyword_flag'],
        'sentiment': nlp_res['sentiment']
    }
    try:
        act_res = db.activities.insert_one(doc)
    except Exception:
        act_res = None

    alert = None
    if level in ['HIGH', 'MEDIUM']:
        alert_doc = {
            'user_id': user_id,
            'score': score,
            'level': level,
            'timestamp': doc['timestamp']
        }
        try:
            res = db.alerts.insert_one(alert_doc)
            alert_doc['_id'] = str(res.inserted_id)
        except Exception:
            alert_doc['_id'] = None
        alert = alert_doc

    return score, _to_json_serializable(alert)
