# game_data.py

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

EVENTS = [
    {
        "id": "E001",
        "title": "黄河决堤",
        "trigger": lambda s: s.year > 2 and s.nation_stats['agriculture'] < 60,
        "report": {
            "base_text": "陛下，黄河下游决堤，数万百姓流离失所，急需开仓放粮，拨款修堤！",
            "distortions": [
                {"condition": lambda s: s.faction_stats['bureaucrats']['loyalty'] < 40, "append_text": " 据臣所知，负责河工的官员乃是宦官一党，恐有贪腐之嫌，请陛下明察！"},
                {"condition": lambda s: s.faction_stats['generals']['loyalty'] < 50, "append_text": " 此事恐会影响北方军粮运输，请陛下速速拨款修堤，勿误军国大事！"}
            ]
        },
        "choices": [
            {
                "id": "E001_C1",
                "text": "拨款200万两修堤，并开仓放粮。",
                "executing_faction": "bureaucrats",
                "outcomes": [
                    {"description": "在忠臣的主持下，大堤得固，百姓感恩戴德。", "condition": lambda s, f: f['loyalty'] > 60, "stat_changes": {"treasury": -200, "stability": 20, "bureaucrats-loyalty": 5, "health": -5}},
                    {"description": "款项被层层盘剥，百姓未见其利，反增其乱。", "condition": lambda s, f: f['loyalty'] < 40, "stat_changes": {"treasury": -200, "stability": -10, "bureaucrats-influence": 5, "mentality": -10}},
                    {"description": "大堤勉强修好，但效果平平，耗费巨大。", "condition": "default", "stat_changes": {"treasury": -200, "stability": 5, "mentality": -5, "health": -5}}
                ]
            },
            {
                "id": "E001_C2",
                "text": "派遣宦官严查，再行赈灾。",
                "executing_faction": "eunuchs",
                "outcomes": [
                    {"description": "查出巨贪，追回了部分款项，民怨稍解，但文官集团对您更加忌惮。", "condition": lambda s, f: f['loyalty'] > 70, "stat_changes": {"treasury": -50, "stability": 5, "eunuchs-loyalty": 5, "bureaucrats-loyalty": -10, "mentality": 5}},
                    {"description": "调查受阻，错过了最佳救灾时机，灾情扩大。", "condition": "default", "stat_changes": {"treasury": -10, "stability": -15, "eunuchs-loyalty": -5, "health": -10, "mentality": -10}}
                ]
            }
        ]
    },
    {
        "id": "E002",
        "title": "科举恩科",
        "trigger": lambda s: s.year % 3 == 0, # 每3年触发一次
        "report": {
            "base_text": "陛下，又是一年科举之期。为国选材，乃是头等大事。本次考试的主考官人选，至关重要。"
        },
        "choices": [
            {
                "id": "E002_C1",
                "text": "任命文官集团的宿儒为主考官。",
                "executing_faction": "bureaucrats",
                "outcomes": [
                    {"description": "考试公平公正，一批有才干的寒门学子入朝为官，文官集团的忠诚度有所提升。", "condition": "default", "stat_changes": {"bureaucrats-loyalty": 5, "prestige": 5, "stability": 5}}
                ]
            },
            {
                "id": "E002_C2",
                "text": "为平衡势力，任命宗室成员为主考官。",
                "executing_faction": "clan",
                "outcomes": [
                    {"description": "宗室子弟在科举中大占便宜，引起了学子们的普遍不满，但宗室对你更加拥护。", "condition": "default", "stat_changes": {"clan-loyalty": 10, "stability": -5, "bureaucrats-loyalty": -5}}
                ]
            }
        ]
    },
    # 新增事件模板：边境贸易争端
    {
        "id": "E003",
        "title": "边境贸易争端",
        "trigger": lambda s: s.year > 4 and s.nation_stats['treasury'] < 500,
        "report": {
            "base_text": "边关将军上奏，邻国商队在边境横行霸道，屡次引发冲突。是否要下令关闭边境，暂停贸易？"
        },
        "choices": [
            {
                "id": "E003_C1",
                "text": "强硬回应，关闭边境，驱逐商队。",
                "executing_faction": "generals",
                "outcomes": [
                    {"description": "边境恢复安宁，军方士气大振，但国库因失去贸易税收而更加紧张。", "condition": "default", "stat_changes": {"military": 5, "generals-loyalty": 5, "treasury": -50, "stability": 5}}
                ]
            },
            {
                "id": "E003_C2",
                "text": "安抚为上，派文官前去协商。",
                "executing_faction": "bureaucrats",
                "outcomes": [
                    {"description": "经过漫长的谈判，双方达成协议，贸易得以继续，但军方认为此举过于软弱。", "condition": lambda s, f: f['loyalty'] > 50, "stat_changes": {"treasury": 20, "stability": 5, "generals-loyalty": -5}},
                    {"description": "谈判失败，我方外交人员受辱，朝野哗然，你的威望大减。", "condition": "default", "stat_changes": {"prestige": -10, "stability": -10, "mentality": -5}}
                ]
            }
        ]
    },
]

ENDINGS = [
    # 基础失败结局
    {'id': 'end01', 'condition': lambda s: s.nation_stats['treasury'] <= 0, 'title': '国库空虚', 'text': f"国库已空，俸禄无法发放，军队哗变，{DBNAME}王朝在内乱中覆灭。"},
    {'id': 'end02', 'condition': lambda s: s.nation_stats['stability'] <= 0, 'title': '民变蜂起', 'text': "民心尽失，天下揭竿而起。起义军攻破京城，你成为了亡国之君。"},
    {'id': 'end03', 'condition': lambda s: s.nation_stats['military'] <= 0, 'title': '国破家亡', 'text': '军备废弛，外敌入侵。在敌人的铁蹄下，京城化为焦土，你国破家亡。'},
    {'id': 'end04', 'condition': lambda s: s.player_stats['health'] <= 0, 'title': '积劳成疾', 'text': '日夜操劳，你的身体终于被拖垮。你英年早逝，而王朝的未来也随之变得扑朔迷离。'},
    {'id': 'end05', 'condition': lambda s: s.player_stats['mentality'] <= 0, 'title': '心力交瘁', 'text': '长期的压力和欺骗让你精神崩溃，你被软禁在深宫之中，成为了一个傀儡皇帝。'},
    
    # 派系相关结局
    {'id': 'end06', 'condition': lambda s: s.faction_stats['bureaucrats']['influence'] > 85 and s.faction_stats['bureaucrats']['loyalty'] < 20, 'title': '权臣篡位', 'text': '文官集团首鼠两端，终成气候。你被逼退位，禅让于权臣，史书上只留下一笔“恭顺”的记载。'},
    {'id': 'end07', 'condition': lambda s: s.faction_stats['generals']['influence'] > 80 and s.faction_stats['generals']['loyalty'] < 25 and s.player_stats['prestige'] < 30, 'title': '藩镇割据', 'text': '地方将领拥兵自重，朝廷号令不出京城。你的皇权名存实亡，天下陷入四分五裂的战乱之中。'},
    {'id': 'end08', 'condition': lambda s: s.faction_stats['eunuchs']['influence'] > 90 and s.player_stats['prestige'] < 20, 'title': '宦官乱政', 'text': '你过度依赖身边的宦官，导致其势力急剧膨胀，蒙蔽圣听，残害忠良。最终，你在宫廷政变中被他们架空，成为一个可悲的提线木偶。'},

    # 新增：与寿命机制相关的结局
    {'id': 'end09', 'condition': lambda s: s.lifespan <= 0, 'title': '寿终正寝', 'text': f'岁月不居，时节如流。你耗尽了天命所归的岁月，在宫中安然离世。你留下的{DBNAME}王朝，将由你的子嗣继续书写它的命运。'},

    # 成功结局
    {'id': 'end10', 'condition': lambda s: s.year > 30, 'title': '中兴之主', 'text': f"三十年励精图治，你成功带领{DBNAME}王朝走出了末年的泥潭。国家安定，百姓富足，你被后世誉为“中兴之主”。"},
    {'id': 'end11', 'condition': lambda s: s.year > 35 and all(stat > 85 for key, stat in s.nation_stats.items() if key != 'treasury') and all(f['loyalty'] > 70 for f in s.faction_stats.values()), 'title': '千古一帝', 'text': '在你的统治下，国富民强，四海咸服，派系同心。你不仅挽救了王朝，更开创了一个前所未有的盛世，你的功绩将与日月同辉，永载史册。'},
]

DEFAULT_EVENT = {
    "id": "E_DEFAULT", "title": "平安无事",
    "report": {"base_text": "又是平静的一年，陛下可以稍作歇息，处理一些日常政务。"},
    "choices": [
        {"id": "ED_C1", "text": "减免部分赋税", "executing_faction": "bureaucrats", "outcomes": [{"description": "百姓感恩戴德，民心稍有提升。", "condition": "default", "stat_changes": {"treasury": -50, "stability": 5}}]},
        {"id": "ED_C2", "text": "兴修水利", "executing_faction": "bureaucrats", "outcomes": [{"description": "农业生产得到发展，但消耗了国库。", "condition": "default", "stat_changes": {"treasury": -80, "agriculture": 10}}]}
    ]
}
