# game_logic.py
import random
from game_data import FACTIONS, EVENTS, ENDINGS, DEFAULT_EVENT

class GameState:
    """用于存储所有游戏状态的类"""
    def __init__(self):
        self.year = 1
        self.player_stats = {"prestige": 70, "health": 100, "mentality": 100}
        self.nation_stats = {"treasury": 1000, "stability": 70, "military": 60, "agriculture": 50}
        self.faction_stats = {k: v.copy() for k, v in FACTIONS.items()}
        self.event_history = set()
        # 新增：在游戏开始时，为皇帝生成一个40到60年之间的隐藏寿命值
        self.lifespan = random.randint(40, 60) 

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
        """将当前状态序列化为字典，方便发送给前端。寿命值不包含在内，对玩家隐藏。"""
        return {
            "year": self.year,
            "playerStats": self.player_stats,
            "nationStats": self.nation_stats,
            "factionStats": self.faction_stats
        }

def get_next_event(game_state):
    """获取下一个可触发的事件"""
    available_events = [e for e in EVENTS if e['id'] not in game_state.event_history and e['trigger'](game_state)]
    if available_events:
        return random.choice(available_events)
    return DEFAULT_EVENT

def process_choice(game_state, event_id, choice_id):
    """处理玩家的选择并返回结果"""
    event = next((e for e in EVENTS if e['id'] == event_id), DEFAULT_EVENT)
    choice = next((c for c in event['choices'] if c['id'] == choice_id), None)

    if not choice:
        return {"error": "Invalid choice"}

    executing_faction = game_state.faction_stats[choice['executing_faction']]
    final_outcome = None

    for outcome in choice['outcomes']:
        if outcome['condition'] == 'default' or outcome['condition'](game_state, executing_faction):
            final_outcome = outcome
            break
    
    if final_outcome:
        game_state.apply_stat_changes(final_outcome['stat_changes'])
        return {"description": final_outcome['description']}
    
    return {"error": "Could not determine outcome"}

def advance_year(game_state):
    """推进年份并应用新的年度变化逻辑"""
    game_state.year += 1
    
    # 移除：不再有自动税收
    # game_state.nation_stats['treasury'] += int(...)
    
    # 移除：不再有自动健康下降
    # game_state.player_stats['health'] -= 1

    # 新增：根据健康值来消耗寿命
    # 健康为100时，每年寿命-1；健康越低，消耗越快。
    # 例如，健康为50时，每年寿命消耗 1 + (100-50)/50 = 2
    health_penalty = (100 - game_state.player_stats['health']) / 50
    game_state.lifespan -= (1 + health_penalty)

    game_state.apply_stat_changes({}) # 仅用于确保数值在0-100范围内

def check_endings(game_state):
    """检查结局"""
    for ending in ENDINGS:
        if ending['condition'](game_state):
            return ending
    return None
