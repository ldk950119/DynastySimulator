# app.py
from flask import Flask, render_template, jsonify, request, session
import os
import traceback

from game_logic import GameState, get_next_event, process_choice, advance_year, check_endings
from game_data import TALENTS, DBNAME

app = Flask(__name__)
# 核心修改：为session设置一个密钥。在生产环境中，这应该是一个更复杂的、不公开的字符串。
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.json
    talent_id = data.get('talentId')
    
    game_state = GameState()
    
    talent = next((t for t in TALENTS if t['id'] == talent_id), None)
    if talent:
        game_state.apply_stat_changes(talent['effects'])
    
    # 核心修改：将游戏状态存入session，而不是全局变量
    session['game_state'] = game_state.to_dict()
    
    return jsonify(game_state.to_frontend_dict())

@app.route('/api/next_turn', methods=['GET'])
def next_turn():
    # 核心修改：从session中恢复游戏状态
    if 'game_state' not in session:
        return jsonify({"error": "Game not started or session expired"}), 400
    game_state = GameState.from_dict(session['game_state'])

    advance_year(game_state)
    
    ending = check_endings(game_state)
    if ending:
        session.pop('game_state', None) # 游戏结束，清除session
        ending_for_frontend = {"id": ending["id"], "title": ending["title"], "text": ending["text"]}
        return jsonify({"game_over": True, "ending": ending_for_frontend, "new_state": game_state.to_frontend_dict()})

    event = get_next_event(game_state)
    
    report_text = event['report']['base_text']
    if "distortions" in event['report']:
        for d in event['report']['distortions']:
            if d['condition'](game_state):
                report_text += d['append_text']
                break
    
    event_for_frontend = {
        "id": event['id'],
        "title": event['title'],
        "report": report_text,
        "choices": [{"id": c['id'], "text": c['text']} for c in event['choices']]
    }
    
    # 核心修改：更新session中的游戏状态
    session['game_state'] = game_state.to_dict()

    return jsonify({
        "game_state": game_state.to_frontend_dict(),
        "event": event_for_frontend
    })

@app.route('/api/choice', methods=['POST'])
def make_choice():
    if 'game_state' not in session:
        return jsonify({"error": "Game not started or session expired"}), 400
    game_state = GameState.from_dict(session['game_state'])
        
    data = request.json
    event_id = data.get('eventId')
    choice_id = data.get('choiceId')

    result = process_choice(game_state, event_id, choice_id)
    
    ending = check_endings(game_state)
    if ending:
        session.pop('game_state', None)
        ending_for_frontend = {"id": ending["id"], "title": ending["title"], "text": ending["text"]}
        return jsonify({
            "game_over": True,
            "ending": ending_for_frontend,
            "result": result,
            "new_state": game_state.to_frontend_dict() 
        })
    
    session['game_state'] = game_state.to_dict()

    return jsonify({
        "result": result,
        "new_state": game_state.to_frontend_dict()
    })

@app.route('/api/talents', methods=['GET'])
def get_talents():
    return jsonify(TALENTS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
