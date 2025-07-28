# game_logic.py
import random
from game_data import FACTIONS, EVENTS, ENDINGS, DAILY_EVENTS

class GameState:
    """用于存储所有游戏状态的类"""
    def __init__(self):
        self.year = 1
        self.player_stats = {"prestige": 70, "health": 100, "mentality": 100}
        self.nation_stats = {"treasury": 1000, "stability": 70, "military": 60, "agriculture": 50}
        self.faction_stats = {k: v.copy() for k, v in FACTIONS.items()}
        self.event_history = set()
        self.lifespan = random.randint(40, 60) 
        self.hidden_flags = set()

    def apply_stat_changes(self, changes):
        """应用数值变化"""
        for key, value in changes.items():
            if key in self.player_stats:
                self.player_stats[key] = max(0, self.player_stats[key] + value)
            elif key in self.nation_stats:
                self.nation_stats[key] = max(0, self.nation_stats[key] + value)
            else:
                try:
                    faction_id, prop = key.split('-')
                    if faction_id in self.faction_stats and prop in self.faction_stats[faction_id]:
                        self.faction_stats[faction_id][prop] = max(0, min(100, self.faction_stats[faction_id][prop] + value))
                except (ValueError, KeyError):
                    print(f"警告：未知的属性键 '{key}'")
        
        for k in self.player_stats: self.player_stats[k] = min(100, self.player_stats[k])
        for k in self.nation_stats:
            if k != 'treasury': self.nation_stats[k] = min(100, self.nation_stats[k])

    def to_dict(self):
        """将当前状态序列化为字典，方便存储。"""
        # Set不能直接转为JSON，需要先转为list
        return {
            "year": self.year,
            "player_stats": self.player_stats,
            "nation_stats": self.nation_stats,
            "faction_stats": self.faction_stats,
            "event_history": list(self.event_history),
            "lifespan": self.lifespan,
            "hidden_flags": list(self.hidden_flags)
        }

    @classmethod
    def from_dict(cls, data):
        """从字典中恢复游戏状态。"""
        state = cls()
        state.year = data.get("year", 1)
        state.player_stats = data.get("player_stats", state.player_stats)
        state.nation_stats = data.get("nation_stats", state.nation_stats)
        state.faction_stats = data.get("faction_stats", state.faction_stats)
        # 从list恢复为set
        state.event_history = set(data.get("event_history", []))
        state.lifespan = data.get("lifespan", random.randint(40, 60))
        state.hidden_flags = set(data.get("hidden_flags", []))
        return state

    def to_frontend_dict(self):
        """将状态序列化为发送给前端的字典（隐藏敏感数据）。"""
        return {
            "year": self.year,
            "playerStats": self.player_stats,
            "nationStats": self.nation_stats,
            "factionStats": self.faction_stats
        }

def get_next_event(game_state):
    """
    获取下一个事件。
    核心修改：重写事件筛选逻辑以修复重复触发的Bug。
    """
    triggered_story_events = [
        e for e in EVENTS 
        if e['id'] not in game_state.event_history and ('trigger' not in e or e['trigger'](game_state))
    ]

    if triggered_story_events:
        event = random.choice(triggered_story_events)
        game_state.event_history.add(event['id'])
        return event

    triggered_daily_events = [
        e for e in DAILY_EVENTS
        if ('trigger' not in e or e['trigger'](game_state))
    ]
    if triggered_daily_events:
        return random.choice(triggered_daily_events)

    return {
        "id": "E_NO_EVENTS",
        "title": "内容枯竭",
        "report": {"base_text": "（开发者提示：当前没有可触发的事件。请在 game_data.py 中添加更多主线或日常事件。）"},
        "choices": [
            {"id": "E_NO_EVENTS_C1", "text": "继续", "executing_faction": "bureaucrats", "outcomes": [
                {"description": "时间继续流逝。", "condition": "default", "stat_changes": {}}
            ]}
        ]
    }


def process_choice(game_state, event_id, choice_id):
    """
    将决策逻辑恢复为简单的、确定性的版本
    """
    all_events = EVENTS + DAILY_EVENTS
    if event_id == "E_NO_EVENTS":
        all_events.append(get_next_event(GameState()))

    event = next((e for e in all_events if e['id'] == event_id), None)
    if not event:
        return {"error": f"Event with id {event_id} not found."}

    choice = next((c for c in event['choices'] if c['id'] == choice_id), None)
    if not choice:
        return {"error": f"Choice with id {choice_id} not found in event {event_id}."}

    executing_faction = game_state.faction_stats[choice['executing_faction']]
    
    final_outcome = None
    for outcome in choice['outcomes']:
        if outcome['condition'] == 'default' or outcome['condition'](game_state, executing_faction):
            final_outcome = outcome
            break
    
    if final_outcome:
        game_state.apply_stat_changes(final_outcome['stat_changes'])
        
        if "flags_to_add" in final_outcome:
            for flag in final_outcome["flags_to_add"]:
                game_state.hidden_flags.add(flag)
        if "flags_to_remove" in final_outcome:
            for flag in final_outcome["flags_to_remove"]:
                game_state.hidden_flags.discard(flag)

        return {"description": final_outcome['description']}
    
    return {"error": "Could not determine outcome"}


def advance_year(game_state):
    """推进年份并应用新的年度变化逻辑"""
    game_state.year += 1
    health_penalty = (100 - game_state.player_stats['health']) / 50
    game_state.lifespan -= (1 + health_penalty)
    game_state.apply_stat_changes({})

def check_endings(game_state):
    """检查结局"""
    for ending in ENDINGS:
        if ending['condition'](game_state):
            return ending
    return None
