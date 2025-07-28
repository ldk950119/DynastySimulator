# game_data.py
import random # <--- CORE FIX: Import the 'random' module here.

DBNAME = "大乾"

TALENTS = [
    {'id': 't01', 'name': '天命之子', 'description': '你生有异象，被视为天命所归。初始皇威+20，民心+10。', 'effects': {'prestige': 20, 'stability': 10}},
    {'id': 't02', 'name': '权臣之后', 'description': '你的外戚或恩师是朝中重臣。初始国库+200，文官忠诚+10。', 'effects': {'treasury': 200, 'bureaucrats-loyalty': 10}},
    {'id': 't03', 'name': '少年将军', 'description': '你曾久经沙场，在军中颇有威望。初始军力+20，武将忠诚+10。', 'effects': {'military': 20, 'generals-loyalty': 10}},
]

FACTIONS = {
    "bureaucrats": {"name": "文官集团", "loyalty": 50, "influence": 60},
    "generals": {"name": "武将集团", "loyalty": 50, "influence": 50},
    "eunuchs": {"name": "宦官势力", "loyalty": 70, "influence": 40},
    "clan": {"name": "宗室外戚", "loyalty": 60, "influence": 30},
}

# 主线/剧情事件
EVENTS = [
    {
        "id": "E001",
        "title": "黄河决堤",
        "trigger": lambda s: s.year > 2 and s.nation_stats['agriculture'] < 60,
        "report": { "base_text": "陛下，黄河下游决堤，数万百姓流离失所，急需开仓放粮，拨款修堤！", "distortions": [ {"condition": lambda s: s.faction_stats['bureaucrats']['loyalty'] < 40, "append_text": " 据臣所知，负责河工的官员乃是宦官一党，恐有贪腐之嫌，请陛下明察！"}, {"condition": lambda s: s.faction_stats['generals']['loyalty'] < 50, "append_text": " 此事恐会影响北方军粮运输，请陛下速速拨款修堤，勿误军国大事！"} ] },
        "choices": [
            { "id": "E001_C1", "text": "拨款200万两修堤，并开仓放粮。", "executing_faction": "bureaucrats", "outcomes": [ {"description": "在忠臣的主持下，大堤得固，百姓感恩戴德。", "condition": lambda s, f: f['loyalty'] > 60, "stat_changes": {"treasury": -200, "stability": 20, "bureaucrats-loyalty": 5, "health": -5}}, {"description": "款项被层层盘剥，百姓未见其利，反增其乱。", "condition": lambda s, f: f['loyalty'] < 40, "stat_changes": {"treasury": -200, "stability": -10, "bureaucrats-influence": 5, "mentality": -10}}, {"description": "大堤勉强修好，但效果平平，耗费巨大。", "condition": "default", "stat_changes": {"treasury": -200, "stability": 5, "mentality": -5, "health": -5}} ] },
            { "id": "E001_C2", "text": "派遣宦官严查，再行赈灾。", "executing_faction": "eunuchs", "outcomes": [ {"description": "查出巨贪，追回了部分款项，民怨稍解，但文官集团对您更加忌惮。", "condition": lambda s, f: f['loyalty'] > 70, "stat_changes": {"treasury": -50, "stability": 5, "eunuchs-loyalty": 5, "bureaucrats-loyalty": -10, "mentality": 5}}, {"description": "调查受阻，错过了最佳救灾时机，灾情扩大。", "condition": "default", "stat_changes": {"treasury": -10, "stability": -15, "eunuchs-loyalty": -5, "health": -10, "mentality": -10}} ] }
        ]
    },
]

# --- 日常事件库 ---
DAILY_EVENTS = [
    {
        "id": "D001", "title": "翰林院呈书",
        "report": {"base_text": "翰林院的大学士呈上新编撰的史书，请您御览。"},
        "choices": [
            {"id": "D001_C1", "text": "仔细阅读，嘉奖学士。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的好学之名在文官中传开，皇威略有提升。", "condition": "default", "stat_changes": {"prestige": 2, "bureaucrats-loyalty": 1}}]},
            {"id": "D001_C2", "text": "无心政务，放置一旁。", "executing_faction": "bureaucrats", "outcomes": [{"description": "大学士们感到有些失望。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": -1}}]}
        ]
    },
    {
        "id": "D002", "title": "御膳房的新菜",
        "report": {"base_text": "御膳房总管呈上新研制的菜肴，请您品尝。"},
        "choices": [
            {"id": "D002_C1", "text": "品尝并大加赞赏。", "executing_faction": "eunuchs", "outcomes": [{"description": "一顿美食让你心情愉悦，健康和心态都略有恢复。", "condition": "default", "stat_changes": {"health": 2, "mentality": 2}}]},
            # 核心修改：这个选项现在会添加一个“隐藏标记”
            {"id": "D002_C2", "text": "斥其奢靡，下令节俭。", "executing_faction": "eunuchs", "outcomes": [{"description": "你节俭的名声传开了，但御厨对你的斥责怀恨在心。", "condition": "default", "stat_changes": {"prestige": 1, "eunuchs-loyalty": -1}, "flags_to_add": ["chef_angry"]}]}
        ]
    },
    {
        "id": "D003", "title": "京城治安",
        "report": {"base_text": "京城守备来报，近日城中治安良好，未有大的案件发生。"},
        "choices": [
            {"id": "D003_C1", "text": "嘉奖守备，勉励将士。", "executing_faction": "generals", "outcomes": [{"description": "守备部队士气高昂，对你更加忠诚。", "condition": "default", "stat_changes": {"generals-loyalty": 2, "stability": 1}}]},
            {"id": "D003_C2", "text": "这是他们分内之事。", "executing_faction": "generals", "outcomes": [{"description": "一切如常。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D004", "title": "宗室请安",
        "report": {"base_text": "一位远亲王爷前来请安，言语间暗示封地贫瘠，希望得到些赏赐。"},
        "choices": [
            {"id": "D004_C1", "text": "赏赐金银，以示皇恩。", "executing_faction": "clan", "outcomes": [{"description": "王爷感恩戴德地走了，但国库又少了一笔钱。", "condition": "default", "stat_changes": {"treasury": -20, "clan-loyalty": 2}}]},
            {"id": "D004_C2", "text": "好言安抚，不予赏赐。", "executing_faction": "clan", "outcomes": [{"description": "王爷看起来有些失望。", "condition": "default", "stat_changes": {"clan-loyalty": -1}}]}
        ]
    },
    {
        "id": "D005", "title": "太医请脉",
        "report": {"base_text": "太医前来为您请平安脉。"},
        "choices": [
            {"id": "D005_C1", "text": "让其诊治，并赏赐药材。", "executing_faction": "eunuchs", "outcomes": [{"description": "太医的悉心调理让你的身体感觉好多了。", "condition": "default", "stat_changes": {"health": 3, "treasury": -5}}]},
            {"id": "D005_C2", "text": "朕躬安好，无需多此一举。", "executing_faction": "eunuchs", "outcomes": [{"description": "你打发走了太医。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D006", "title": "密探来报",
        "report": {"base_text": "你安插在某位大臣身边的密探送来一份报告，称该大臣并无异动。"},
        "choices": [
            {"id": "D006_C1", "text": "很好，继续监视。", "executing_faction": "eunuchs", "outcomes": [{"description": "你对朝局的掌控感让你心态平稳。", "condition": "default", "stat_changes": {"mentality": 1}}]},
            {"id": "D006_C2", "text": "撤回密探，以示信任。", "executing_faction": "eunuchs", "outcomes": [{"description": "你节省了一笔开销，但对大臣的掌控力下降了。", "condition": "default", "stat_changes": {"treasury": 5, "eunuchs-influence": -1}}]}
        ]
    },
    {
        "id": "D007", "title": "将军求见",
        "report": {"base_text": "一位战功赫赫的老将军求见，抱怨军中粮饷有些紧张。"},
        "choices": [
            {"id": "D007_C1", "text": "从国库拨发特别军饷。", "executing_faction": "generals", "outcomes": [{"description": "军队士气大振，将军对你忠心耿耿。", "condition": "default", "stat_changes": {"treasury": -50, "military": 2, "generals-loyalty": 3}}]},
            {"id": "D007_C2", "text": "安抚将军，表示国库紧张。", "executing_faction": "generals", "outcomes": [{"description": "将军忧心忡忡地离开了。", "condition": "default", "stat_changes": {"generals-loyalty": -2, "military": -1}}]}
        ]
    },
    {
        "id": "D008", "title": "地方呈上祥瑞",
        "report": {"base_text": "某地官员上奏，称当地发现“麒麟”踪迹，此乃天降祥瑞，彰显陛下德政。"},
        "choices": [
            {"id": "D008_C1", "text": "昭告天下，与民同庆。", "executing_faction": "bureaucrats", "outcomes": [{"description": "百姓们听闻祥瑞之事，民心有所提升。", "condition": "default", "stat_changes": {"stability": 3, "prestige": 2}}]},
            {"id": "D008_C2", "text": "斥其荒谬，令其务实。", "executing_faction": "bureaucrats", "outcomes": [{"description": "官员们知道了你不喜虚名的态度，但你的威望也因此没能提升。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 1}}]}
        ]
    },
    {
        "id": "D009", "title": "后宫请安",
        "report": {"base_text": "后宫的妃嫔们前来向你请安。"},
        "choices": [
            {"id": "D009_C1", "text": "与她们闲聊家常。", "executing_faction": "clan", "outcomes": [{"description": "后宫和睦，让你感到一丝家庭的温暖。", "condition": "default", "stat_changes": {"mentality": 2, "clan-loyalty": 1}}]},
            {"id": "D009_C2", "text": "心系国事，让她们退下。", "executing_faction": "clan", "outcomes": [{"description": "你勤于政务，但后宫的气氛有些冷清。", "condition": "default", "stat_changes": {"prestige": 1}}]}
        ]
    },
    {
        "id": "D010", "title": "皇子课业",
        "report": {"base_text": "太傅报告，皇子们最近在学业上颇有进步。"},
        "choices": [
            {"id": "D010_C1", "text": "亲自考校，予以嘉奖。", "executing_faction": "bureaucrats", "outcomes": [{"description": "看到子嗣成才，你对王朝的未来充满了希望。", "condition": "default", "stat_changes": {"mentality": 3, "clan-loyalty": 2}}]},
            {"id": "D010_C2", "text": "勉励太傅，继续用心教导。", "executing_faction": "bureaucrats", "outcomes": [{"description": "太傅对你更加尽心尽力。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 1}}]}
        ]
    },
    # 新增：由隐藏标记触发的后果事件
    {
        "id": "D011",
        "title": "御厨的复仇",
        # 触发条件：拥有“chef_angry”标记，并且有15%的概率发生
        "trigger": lambda s: "chef_angry" in s.hidden_flags and random.random() < 0.15,
        "report": {"base_text": "今日的午膳似乎格外丰盛，你正欲动筷，身边的试毒太监突然面色发紫，口吐白沫倒地不起！"},
        "choices": [
            {"id": "D011_C1", "text": "（大惊失色）", "executing_faction": "eunuchs", "outcomes": [
                # 核心修改：这个后果事件在触发后，必须移除标记，防止重复发生
                {"description": "你好不容易逃过一劫，但惊吓和后怕让你心力交瘁，健康也大受影响。御厨已被当场拿下，怨恨的种子总算被铲除。", "condition": "default", "stat_changes": {"health": -20, "mentality": -20}, "flags_to_remove": ["chef_angry"]}
            ]}
        ]
    },
    {
        "id": "D012", "title": "宫殿修缮",
        "report": {"base_text": "工部上奏，几处宫殿年久失修，墙皮剥落，建议拨专款进行修缮。"},
        "choices": [
            {"id": "D012_C1", "text": "批准，务必修得壮丽。", "executing_faction": "bureaucrats", "outcomes": [{"description": "宫殿焕然一新，皇室的体面得以维持，但国库又支出了一大笔。", "condition": "default", "stat_changes": {"treasury": -100, "prestige": 3}}]},
            {"id": "D012_C2", "text": "小修小补即可，节省开支。", "executing_faction": "bureaucrats", "outcomes": [{"description": "宫殿得到了基本的维护，节省了开支，但看起来依旧有些陈旧。", "condition": "default", "stat_changes": {"treasury": -30, "prestige": 1}}]}
        ]
    },
    {
        "id": "D013", "title": "民间艺人",
        "report": {"base_text": "听闻民间有一杂耍班子技艺高超，深得百姓喜爱。是否宣其入宫表演？"},
        "choices": [
            {"id": "D013_C1", "text": "宣！与众同乐。", "executing_faction": "eunuchs", "outcomes": [{"description": "精彩的表演让你和宫人们大开眼界，心情舒畅。", "condition": "default", "stat_changes": {"mentality": 3, "stability": 1}}]},
            {"id": "D013_C2", "text": "不务正业，不予理会。", "executing_faction": "eunuchs", "outcomes": [{"description": "你专注于朝政，未将此事放在心上。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D014", "title": "言官上奏",
        "report": {"base_text": "一位御史上奏，洋洋洒洒数千言，弹劾某位将军克扣军饷，言辞激烈。"},
        "choices": [
            {"id": "D014_C1", "text": "派人调查，若属实严惩不贷。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的公正严明让文官集团感到振奋，但被调查的将军对此十分不满。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 3, "generals-loyalty": -3, "prestige": 2}}]},
            {"id": "D014_C2", "text": "斥其捕风捉影，安抚将军。", "executing_faction": "generals", "outcomes": [{"description": "将军对你的信任感激涕零，但言官们认为你偏袒武将，有损圣明。", "condition": "default", "stat_changes": {"generals-loyalty": 3, "bureaucrats-loyalty": -3, "prestige": -2}}]}
        ]
    },
    {
        "id": "D015", "title": "驿站扩建",
        "report": {"base_text": "兵部提议，为加强中央与地方的联系，应扩建驿站，增加驿卒和马匹。"},
        "choices": [
            {"id": "D015_C1", "text": "准奏，此乃国之大事。", "executing_faction": "generals", "outcomes": [{"description": "政令的传达和军情的传递速度大大加快，但维持驿站需要持续的投入。", "condition": "default", "stat_changes": {"treasury": -40, "military": 2, "stability": 2}}]},
            {"id": "D015_C2", "text": "国库紧张，暂缓此议。", "executing_faction": "generals", "outcomes": [{"description": "扩建计划被搁置，一切照旧。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D016", "title": "微服私访？",
        "report": {"base_text": "你感到有些烦闷，一位贴身太监提议，不如换上便装，去宫外体察一番民情。"},
        "choices": [
            {"id": "D016_C1", "text": "好主意，立刻安排。", "executing_faction": "eunuchs", "outcomes": [{"description": "你在街市上听到了许多真实的声音，对民间的疾苦有了更深的了解，但也有些劳累。", "condition": "default", "stat_changes": {"stability": 3, "mentality": 2, "health": -3}}]},
            {"id": "D016_C2", "text": "风险太大，朕不亲涉险地。", "executing_faction": "eunuchs", "outcomes": [{"description": "你选择留在安全的宫中，处理堆积的奏折。", "condition": "default", "stat_changes": {"health": 1}}]}
        ]
    },
    {
        "id": "D017", "title": "外戚求官",
        "report": {"base_text": "一位得宠的贵妃为你吹起了枕边风，希望你能为她的草包弟弟在朝中安排一个职位。"},
        "choices": [
            {"id": "D017_C1", "text": "允了她，安排个闲职。", "executing_faction": "clan", "outcomes": [{"description": "贵妃心满意足，外戚对你更加忠心。但朝中多了一个吃闲饭的，文官们对此颇有微词。", "condition": "default", "stat_changes": {"clan-loyalty": 3, "bureaucrats-loyalty": -2, "treasury": -10}}]},
            {"id": "D017_C2", "text": "严词拒绝，告诫后宫不得干政。", "executing_faction": "clan", "outcomes": [{"description": "你维护了朝廷的规矩，皇威有所提升，但贵妃好几天没给你好脸色看。", "condition": "default", "stat_changes": {"prestige": 3, "clan-loyalty": -3, "mentality": -2}}]}
        ]
    },
    {
        "id": "D018", "title": "番邦进贡",
        "report": {"base_text": "西域小国派遣使者前来，进贡了一批珍奇的珠宝和香料。"},
        "choices": [
            {"id": "D018_C1", "text": "厚往薄来，加倍赏赐。", "executing_faction": "bureaucrats", "outcomes": [{"description": "使者对天朝的慷慨感激不尽，你的威名远播四方。", "condition": "default", "stat_changes": {"prestige": 3, "treasury": -60}}]},
            {"id": "D018_C2", "text": "收入国库，常规赏赐。", "executing_faction": "bureaucrats", "outcomes": [{"description": "国库得到了一笔意外的补充。", "condition": "default", "stat_changes": {"treasury": 40}}]}
        ]
    },
    {
        "id": "D019", "title": "皇家围猎",
        "report": {"base_text": "秋高气爽，正是围猎的好时节。武将们提议举办一场皇家围猎，以彰显国威，操演兵马。"},
        "choices": [
            {"id": "D019_C1", "text": "准奏，朕要亲自参与。", "executing_faction": "generals", "outcomes": [{"description": "你在围猎中大显身手，与将士们同乐，军心大振。但此行花费不菲。", "condition": "default", "stat_changes": {"military": 3, "generals-loyalty": 4, "health": -2, "treasury": -80}}]},
            {"id": "D019_C2", "text": "国事为重，取消围猎。", "executing_faction": "generals", "outcomes": [{"description": "将士们有些失望，但国库避免了一次不必要的开销。", "condition": "default", "stat_changes": {"generals-loyalty": -2}}]}
        ]
    },
    {
        "id": "D020", "title": "清查土地",
        "report": {"base_text": "户部尚书上奏，称国内土地兼并严重，大量田产被地方豪强隐匿，导致税收流失，建议在全国清查田亩。"},
        "choices": [
            {"id": "D020_C1", "text": "雷厉风行，彻查到底。", "executing_faction": "bureaucrats", "outcomes": [{"description": "清查行动查出了大量隐田，国库收入大增，但此举触动了几乎所有权贵的利益，各派系对你的忠诚都有所下降。", "condition": "default", "stat_changes": {"treasury": 200, "bureaucrats-loyalty": -5, "generals-loyalty": -5, "clan-loyalty": -10, "stability": -5}}]},
            {"id": "D020_C2", "text": "兹事体大，从长计议。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你将此事暂时搁置，避免了朝局的剧烈动荡。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D021", "title": "大赦天下",
        "report": {"base_text": "为庆贺皇子满月，有大臣提议大赦天下，以彰显您的仁德。"},
        "choices": [
            {"id": "D021_C1", "text": "准奏，与天下同庆。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的仁德之名传遍天下，民心大幅提升，但一些罪犯被释放也给地方治安带来些许隐患。", "condition": "default", "stat_changes": {"stability": 10, "prestige": 5, "military": -1}}]},
            {"id": "D021_C2", "text": "不可，国法岂能儿戏。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你维护了法律的威严，但错失了一次收拢民心的好机会。", "condition": "default", "stat_changes": {"prestige": 2}}]}
        ]
    },
    {
        "id": "D022", "title": "开凿运河",
        "report": {"base_text": "有大臣提议，开凿一条新的运河连接南北，以利漕运和商业。"},
        "choices": [
            {"id": "D022_C1", "text": "功在千秋，即刻动工。", "executing_faction": "bureaucrats", "outcomes": [{"description": "一项浩大的工程开始了。它将极大地消耗国库和民力，但若能成功，将对农业和民生大有裨益。", "condition": "default", "stat_changes": {"treasury": -150, "stability": -5, "agriculture": 5, "prestige": 2}}]},
            {"id": "D022_C2", "text": "劳民伤财，不予采纳。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你驳回了这项提议，避免了巨大的开销。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D023", "title": "将领的请求",
        "report": {"base_text": "一位边关将领上书，请求将他的儿子安排到京城禁军中历练。"},
        "choices": [
            {"id": "D023_C1", "text": "同意，将门虎子理应重用。", "executing_faction": "generals", "outcomes": [{"description": "将领对你感激不尽，你在军中的影响力更大了。", "condition": "default", "stat_changes": {"generals-loyalty": 4, "generals-influence": 2}}]},
            {"id": "D023_C2", "text": "拒绝，禁军选拔需按规矩来。", "executing_faction": "generals", "outcomes": [{"description": "你维护了制度，但那位将领显然有些失望。", "condition": "default", "stat_changes": {"generals-loyalty": -3, "prestige": 1}}]}
        ]
    },
    {
        "id": "D024", "title": "神秘的道士",
        "report": {"base_text": "一位道士自称能炼制长生不老丹药，请求面圣。"},
        "choices": [
            {"id": "D024_C1", "text": "宣他入宫，令其开炉炼丹。", "executing_faction": "eunuchs", "outcomes": [{"description": "你开始服用道士炼制的“仙丹”，感觉精神焕发，但太医们对此忧心忡忡。", "condition": "default", "stat_changes": {"mentality": 5, "health": -2, "treasury": -50}}]},
            {"id": "D024_C2", "text": "斥为妖言惑众，逐出京城。", "executing_faction": "eunuchs", "outcomes": [{"description": "你对这些虚无缥缈的东西不感兴趣。", "condition": "default", "stat_changes": {"mentality": -1}}]}
        ]
    },
    {
        "id": "D025", "title": "国子监辩论",
        "report": {"base_text": "国子监的学子们就“义利之辨”展开激烈辩论，请求您亲临裁断。"},
        "choices": [
            {"id": "D025_C1", "text": "欣然前往，参与讨论。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的学识和见解折服了在场的学子，你在士林中的威望大大提高。", "condition": "default", "stat_changes": {"prestige": 4, "bureaucrats-loyalty": 2}}]},
            {"id": "D025_C2", "text": "此等空谈，于国何益？", "executing_faction": "bureaucrats", "outcomes": [{"description": "学子们对你的态度感到失望。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": -2}}]}
        ]
    },
    {
        "id": "D026", "title": "盐铁专卖",
        "report": {"base_text": "户部提议，将盐和铁的生产销售收归国有，以增加国库收入。"},
        "choices": [
            {"id": "D026_C1", "text": "准奏，此乃富国强兵之策。", "executing_faction": "bureaucrats", "outcomes": [{"description": "盐铁官营为国库带来了稳定的巨额收入，但官府的垄断也导致价格上涨，引起了部分民众的不满。", "condition": "default", "stat_changes": {"treasury": 150, "stability": -3}}]},
            {"id": "D026_C2", "text": "与民争利，不可行。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你没有采纳这个建议，维持了现有的自由贸易政策。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D027", "title": "修建皇家陵寝",
        "report": {"base_text": "宗室成员提议，是时候为您百年之后修建一座配得上您身份的陵寝了。"},
        "choices": [
            {"id": "D027_C1", "text": "同意，提前规划身后事。", "executing_faction": "clan", "outcomes": [{"description": "一项巨大的工程开始了，它将耗费无数钱财和民力。", "condition": "default", "stat_changes": {"treasury": -200, "stability": -5, "clan-loyalty": 3}}]},
            {"id": "D027_C2", "text": "朕还年轻，此事不急。", "executing_faction": "clan", "outcomes": [{"description": "你将此事搁置了下来。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D028", "title": "邻国公主",
        "report": {"base_text": "邻国派遣使者，希望送一位公主前来和亲，以结两国之好。"},
        "choices": [
            {"id": "D028_C1", "text": "接受和亲，纳入后宫。", "executing_faction": "clan", "outcomes": [{"description": "两国关系更加稳固，但你的后宫也因此增添了新的变数。", "condition": "default", "stat_changes": {"stability": 3, "clan-influence": 2}}]},
            {"id": "D028_C2", "text": "婉言谢绝。", "executing_faction": "clan", "outcomes": [{"description": "你拒绝了这次联姻，邻国对此似乎有些失望。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D029", "title": "新式火器",
        "report": {"base_text": "军器监的工匠研制出一种新式火器，射程和威力都远胜从前，但造价不菲。"},
        "choices": [
            {"id": "D029_C1", "text": "不计成本，全军换装。", "executing_faction": "generals", "outcomes": [{"description": "你的军队装备了划时代的武器，军力大增，这让所有潜在的敌人都感到了畏惧。", "condition": "default", "stat_changes": {"military": 15, "treasury": -250, "prestige": 5}}]},
            {"id": "D029_C2", "text": "很好，但先小规模试制。", "executing_faction": "generals", "outcomes": [{"description": "一小部分精锐部队装备了新火器，战斗力有所提升。", "condition": "default", "stat_changes": {"military": 5, "treasury": -80}}]}
        ]
    },
    {
        "id": "D030", "title": "老臣告老",
        "report": {"base_text": "一位在朝中德高望重的老臣上书，请求告老还乡。"},
        "choices": [
            {"id": "D030_C1", "text": "准奏，并赐予丰厚赏赐。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你尊重大臣的决定，此举赢得了百官的赞誉。", "condition": "default", "stat_changes": {"prestige": 3, "bureaucrats-loyalty": 2}}]},
            {"id": "D030_C2", "text": "挽留，称国家需要他。", "executing_faction": "bureaucrats", "outcomes": [{"description": "老臣被你的诚意打动，决定继续为你效力。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 4, "mentality": 2}}]}
        ]
    },
    {
        "id": "D031", "title": "天狗食日",
        "report": {"base_text": "天空中出现了日食现象，百姓中流言四起，认为是上天对你的警示。"},
        "choices": [
            {"id": "D031_C1", "text": "下罪己诏，安抚民心。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的谦卑姿态平息了民众的恐慌，民心得以稳定，但皇威也因此受损。", "condition": "default", "stat_changes": {"stability": 5, "prestige": -5}}]},
            {"id": "D031_C2", "text": "颁布告示，解释此乃自然现象。", "executing_faction": "bureaucrats", "outcomes": [{"description": "虽然官方进行了解释，但仍有许多人将信将疑，民心不稳。", "condition": "default", "stat_changes": {"stability": -3}}]}
        ]
    },
    {
        "id": "D032", "title": "祥瑞还是异象?",
        "report": {"base_text": "钦天监来报，昨夜观察到有奇特的云霞出现在紫禁城上空，不知是何预兆。"},
        "choices": [
            {"id": "D032_C1", "text": "此乃祥瑞，大力宣传。", "executing_faction": "bureaucrats", "outcomes": [{"description": "“天降祥云”的消息传开，百姓们认为你是天命所归，民心和皇威都得到提升。", "condition": "default", "stat_changes": {"stability": 2, "prestige": 2}}]},
            {"id": "D032_C2", "text": "此乃异象，朕当自省。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你表现出的谦逊和谨慎让大臣们颇为赞赏。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 2, "mentality": 1}}]}
        ]
    },
    {
        "id": "D033", "title": "皇庄收成",
        "report": {"base_text": "内务府总管来报，今年的皇家田庄大丰收，多出了不少粮食。"},
        "choices": [
            {"id": "D033_C1", "text": "全部变卖，充入国库。", "executing_faction": "eunuchs", "outcomes": [{"description": "国库得到了一笔可观的补充。", "condition": "default", "stat_changes": {"treasury": 70}}]},
            {"id": "D033_C2", "text": "分发给宫中侍卫和宫女。", "executing_faction": "eunuchs", "outcomes": [{"description": "宫人们对你的慷慨感恩戴德，宦官和禁军的忠诚度都有所提升。", "condition": "default", "stat_changes": {"eunuchs-loyalty": 2, "generals-loyalty": 1}}]}
        ]
    },
    {
        "id": "D034", "title": "修复古籍",
        "report": {"base_text": "翰林院的学者们发现一批前朝的珍贵古籍因保存不当而严重受损，请求拨款修复。"},
        "choices": [
            {"id": "D034_C1", "text": "文化传承为重，批准。", "executing_faction": "bureaucrats", "outcomes": [{"description": "你的决定保住了一批文化瑰宝，在文人中的声望大大提高。", "condition": "default", "stat_changes": {"treasury": -30, "prestige": 2, "bureaucrats-loyalty": 2}}]},
            {"id": "D034_C2", "text": "国库空虚，暂无余力。", "executing_faction": "bureaucrats", "outcomes": [{"description": "学者们对此感到非常遗憾。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": -2}}]}
        ]
    },
    {
        "id": "D035", "title": "禁军比武",
        "report": {"base_text": "禁军举行了一年一度的比武大会，将士们士气高昂，邀请您亲临观摩。"},
        "choices": [
            {"id": "D035_C1", "text": "亲临校场，并赏赐魁首。", "executing_faction": "generals", "outcomes": [{"description": "你的到来让将士们备受鼓舞，军心可用。", "condition": "default", "stat_changes": {"military": 2, "generals-loyalty": 3, "treasury": -15}}]},
            {"id": "D035_C2", "text": "朕乏了，派人代为观礼。", "executing_faction": "generals", "outcomes": [{"description": "将士们未能亲见圣颜，感到有些失落。", "condition": "default", "stat_changes": {"generals-loyalty": -1}}]}
        ]
    },
    {
        "id": "D036", "title": "宦官的小报告",
        "report": {"base_text": "一个贴身小太监向你秘密报告，称他看到两位大臣在深夜秘密会面，形迹可疑。"},
        "choices": [
            {"id": "D036_C1", "text": "哦？派人去查查。", "executing_faction": "eunuchs", "outcomes": [{"description": "调查结果表明，两位大臣只是在讨论棋艺。你的多疑让大臣们有些不安。", "condition": "default", "stat_changes": {"mentality": -2, "bureaucrats-loyalty": -2}}]},
            {"id": "D036_C2", "text": "不必理会，恐是小人挑拨。", "executing_faction": "eunuchs", "outcomes": [{"description": "你没有理会这个小报告，朝局一如既往。", "condition": "default", "stat_changes": {"mentality": 1}}]}
        ]
    },
    {
        "id": "D037", "title": "地方水利",
        "report": {"base_text": "一位地方官员上书，请求拨款修建一座水坝，以保一方平安。"},
        "choices": [
            {"id": "D037_C1", "text": "利国利民，准了。", "executing_faction": "bureaucrats", "outcomes": [{"description": "水坝建成后，当地的农业收成得到了保障。", "condition": "default", "stat_changes": {"treasury": -60, "agriculture": 3, "stability": 2}}]},
            {"id": "D037_C2", "text": "让地方自行筹款。", "executing_faction": "bureaucrats", "outcomes": [{"description": "由于资金不足，修建水坝的计划被搁置了。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D038", "title": "宗室丑闻",
        "report": {"base_text": "有传言称，一位皇叔沉迷赌博，欠下巨额债务，闹得满城风雨。"},
        "choices": [
            {"id": "D038_C1", "text": "替他还债，压下此事。", "executing_faction": "clan", "outcomes": [{"description": "丑闻被平息，皇室的颜面得以保全，宗室对你心存感激。", "condition": "default", "stat_changes": {"treasury": -100, "clan-loyalty": 4, "prestige": -2}}]},
            {"id": "D038_C2", "text": "严厉申斥，令其自行解决。", "executing_faction": "clan", "outcomes": [{"description": "你公正无私，但也因此与宗室的关系变得紧张。", "condition": "default", "stat_changes": {"prestige": 2, "clan-loyalty": -4}}]}
        ]
    },
    {
        "id": "D039", "title": "异国商人",
        "report": {"base_text": "一位来自遥远国度的商人，向你献上了一只活蹦乱跳的袋鼠，声称是“祥瑞”。"},
        "choices": [
            {"id": "D039_C1", "text": "有趣，养在宫中。", "executing_faction": "eunuchs", "outcomes": [{"description": "这只奇特的动物给你带来了许多乐趣。", "condition": "default", "stat_changes": {"mentality": 3}}]},
            {"id": "D039_C2", "text": "非我族类，放归自然。", "executing_faction": "eunuchs", "outcomes": [{"description": "你对此并无兴趣。", "condition": "default", "stat_changes": {}}]}
        ]
    },
    {
        "id": "D040", "title": "扩充后宫",
        "report": {"base_text": "礼部大臣上奏，称后宫空虚，子嗣单薄，建议在全国范围内选拔秀女，充实后宫。"},
        "choices": [
            {"id": "D040_C1", "text": "准奏，此事交由宗室办理。", "executing_faction": "clan", "outcomes": [{"description": "一场盛大的选秀开始了，后宫增添了许多新鲜血液，宗室和外戚的势力也因此得到了扩张。", "condition": "default", "stat_changes": {"treasury": -120, "clan-influence": 4, "stability": -2}}]},
            {"id": "D040_C2", "text": "国事为重，暂不考虑。", "executing_faction": "clan", "outcomes": [{"description": "你将精力放在了朝政上。", "condition": "default", "stat_changes": {"prestige": 1}}]}
        ]
    },
    {
        "id": "D041", "title": "将军的家事",
        "report": {"base_text": "一位你所倚重的将军的儿子当街纵马伤人，被京兆尹抓了起来，将军前来向你求情。"},
        "choices": [
            {"id": "D041_C1", "text": "法理不外乎人情，从轻发落。", "executing_faction": "generals", "outcomes": [{"description": "将军对你的宽容感激涕零，但京城的法治因此受到了挑战。", "condition": "default", "stat_changes": {"generals-loyalty": 5, "stability": -3}}]},
            {"id": "D041_C2", "text": "王子犯法与庶民同罪，依法严办。", "executing_faction": "generals", "outcomes": [{"description": "你维护了法律的公正，赢得了民心，但与这位将军之间产生了隔阂。", "condition": "default", "stat_changes": {"stability": 4, "prestige": 2, "generals-loyalty": -5}}]}
        ]
    }

]

ENDINGS = [
    # ... 结局列表保持不变 ...
    {'id': 'end01', 'condition': lambda s: s.nation_stats['treasury'] <= 0, 'title': '国库空虚', 'text': f"国库已空，俸禄无法发放，军队哗变，{DBNAME}王朝在内乱中覆灭。"},
    {'id': 'end02', 'condition': lambda s: s.nation_stats['stability'] <= 0, 'title': '民变蜂起', 'text': "民心尽失，天下揭竿而起。起义军攻破京城，你成为了亡国之君。"},
    {'id': 'end03', 'condition': lambda s: s.nation_stats['military'] <= 0, 'title': '国破家亡', 'text': '军备废弛，外敌入侵。在敌人的铁蹄下，京城化为焦土，你国破家亡。'},
    {'id': 'end04', 'condition': lambda s: s.player_stats['health'] <= 0, 'title': '积劳成疾', 'text': '日夜操劳，你的身体终于被拖垮。你英年早逝，而王朝的未来也随之变得扑朔迷离。'},
    {'id': 'end05', 'condition': lambda s: s.player_stats['mentality'] <= 0, 'title': '心力交瘁', 'text': '长期的压力和欺骗让你精神崩溃，你被软禁在深宫之中，成为了一个傀儡皇帝。'},
    {'id': 'end06', 'condition': lambda s: s.faction_stats['bureaucrats']['influence'] > 85 and s.faction_stats['bureaucrats']['loyalty'] < 20, 'title': '权臣篡位', 'text': '文官集团首鼠两端，终成气候。你被逼退位，禅让于权臣，史书上只留下一笔“恭顺”的记载。'},
    {'id': 'end07', 'condition': lambda s: s.faction_stats['generals']['influence'] > 80 and s.faction_stats['generals']['loyalty'] < 25 and s.player_stats['prestige'] < 30, 'title': '藩镇割据', 'text': '地方将领拥兵自重，朝廷号令不出京城。你的皇权名存实亡，天下陷入四分五裂的战乱之中。'},
    {'id': 'end08', 'condition': lambda s: s.faction_stats['eunuchs']['influence'] > 90 and s.player_stats['prestige'] < 20, 'title': '宦官乱政', 'text': '你过度依赖身边的宦官，导致其势力急剧膨胀，蒙蔽圣听，残害忠良。最终，你在宫廷政变中被他们架空，成为一个可悲的提线木偶。'},
    {'id': 'end09', 'condition': lambda s: s.lifespan <= 0, 'title': '寿终正寝', 'text': f'岁月不居，时节如流。你耗尽了天命所归的岁月，在宫中安然离世。你留下的{DBNAME}王朝，将由你的子嗣继续书写它的命运。'},
    {'id': 'end10', 'condition': lambda s: s.year > 30, 'title': '中兴之主', 'text': f"三十年励精图治，你成功带领{DBNAME}王朝走出了末年的泥潭。国家安定，百姓富足，你被后世誉为“中兴之主”。"},
    {'id': 'end11', 'condition': lambda s: s.year > 35 and all(stat > 85 for key, stat in s.nation_stats.items() if key != 'treasury') and all(f['loyalty'] > 70 for f in s.faction_stats.values()), 'title': '千古一帝', 'text': '在你的统治下，国富民强，四海咸服，派系同心。你不仅挽救了王朝，更开创了一个前所未有的盛世，你的功绩将与日月同辉，永载史册。'},
]


