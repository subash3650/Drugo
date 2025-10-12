from flask import Blueprint, request, jsonify
from services.nlp_service import analyze_text
from services.risk_engine import update_user_and_score
from services.db import get_db_client  # abstracted db helper

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    payload = request.json
    # expected: {platform, user_id, timestamp, text, metadata}
    user_id = payload.get('user_id')
    text = payload.get('text', '')
    platform = payload.get('platform', 'unknown')
    # NLP analysis
    nlp_res = analyze_text(text)
    # update risk & store activity
    score, alert = update_user_and_score(user_id, platform, payload, nlp_res)
    return jsonify({'user_id':user_id, 'score': score, 'alert': alert})
