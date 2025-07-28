# app.py
from flask import Flask, render_template, jsonify, request
import traceback

from game_logic import GameState, get_next_event, process_choice, advance_year, check_endings
from game_data import TALENTS, DBNAME

app = Flask(__name__)

game_sessions = {}

def get_current_session_id():
    if 'session_id' not in request.cookies:
        import uuid
        session_id = str(uuid.uuid4())
    else:
        session_id = request.cookies.get('session_id')
    return session_id

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print("An error occurred while rendering the template:")
        print(traceback.format_exc())
        return "<h1>Error loading template</h1><p>Please check the server logs.</p>", 500


@app.route('/api/start', methods=['POST'])
def start_game():
    try:
        data = request.json
        talent_id = data.get('talentId')
        
        session_id = get_current_session_id()
        game_state = GameState()
        
        talent = next((t for t in TALENTS if t['id'] == talent_id), None)
        if talent:
            game_state.apply_stat_changes(talent['effects'])
        
        game_sessions[session_id] = game_state
        
        response = jsonify(game_state.to_dict())
        response.set_cookie('session_id', session_id)
        return response
    except Exception as e:
        print("An error occurred in /api/start:")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to start game due to a server error."}), 500


@app.route('/api/next_turn', methods=['GET'])
def next_turn():
    try:
        session_id = get_current_session_id()
        game_state = game_sessions.get(session_id)
        if not game_state:
            return jsonify({"error": "Game not started"}), 400

        advance_year(game_state)
        
        ending = check_endings(game_state)
        if ending:
            if session_id in game_sessions:
                del game_sessions[session_id]
            # --- CORE FIX ---
            # Create a "clean" dictionary for the ending, excluding the lambda function.
            ending_for_frontend = {"id": ending["id"], "title": ending["title"], "text": ending["text"]}
            return jsonify({"game_over": True, "ending": ending_for_frontend, "new_state": game_state.to_dict()})

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

        return jsonify({
            "game_state": game_state.to_dict(),
            "event": event_for_frontend
        })
    except Exception as e:
        print("An error occurred in /api/next_turn:")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to get next turn due to a server error."}), 500


@app.route('/api/choice', methods=['POST'])
def make_choice():
    try:
        session_id = get_current_session_id()
        game_state = game_sessions.get(session_id)
        if not game_state:
            return jsonify({"error": "Game not started"}), 400
            
        data = request.json
        event_id = data.get('eventId')
        choice_id = data.get('choiceId')

        result = process_choice(game_state, event_id, choice_id)
        
        ending = check_endings(game_state)
        if ending:
            if session_id in game_sessions:
                del game_sessions[session_id]
            # --- CORE FIX ---
            # Also apply the fix here.
            ending_for_frontend = {"id": ending["id"], "title": ending["title"], "text": ending["text"]}
            return jsonify({
                "game_over": True,
                "ending": ending_for_frontend,
                "result": result,
                "new_state": game_state.to_dict() 
            })

        return jsonify({
            "result": result,
            "new_state": game_state.to_dict()
        })
    except Exception as e:
        print("An error occurred in /api/choice:")
        print(traceback.format_exc())
        return jsonify({"error": "An internal server error occurred. Check the server logs for details."}), 500


@app.route('/api/talents', methods=['GET'])
def get_talents():
    try:
        return jsonify(TALENTS)
    except Exception as e:
        print("An error occurred in /api/talents:")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to load talents due to a server error."}), 500


if __name__ == '__main__':
    app.run(debug=True)
