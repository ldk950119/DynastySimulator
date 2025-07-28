document.addEventListener('DOMContentLoaded', () => {
    const UIElements = {
        gameContainer: document.getElementById('game-container'),
        year: document.getElementById('year'),
        prestige: document.getElementById('prestige'),
        health: document.getElementById('health'),
        mentality: document.getElementById('mentality'),
        treasury: document.getElementById('treasury'),
        stabilityBar: document.getElementById('stability-bar'),
        militaryBar: document.getElementById('military-bar'),
        agricultureBar: document.getElementById('agriculture-bar'),
        eventTitle: document.getElementById('event-title'),
        eventReport: document.getElementById('event-report'),
        eventChoices: document.getElementById('event-choices'),
        factionsDisplay: document.getElementById('factions-display'),
        modal: document.getElementById('modal'),
        modalTitle: document.getElementById('modal-title'),
        modalText: document.getElementById('modal-text'),
        modalChoices: document.getElementById('modal-choices'),
        resultBox: document.getElementById('result-box'),
        resultText: document.getElementById('result-text'),
    };

    let currentEventId = null;

    function updateUI(gameState) {
        if (!gameState) return;
        const { year, playerStats, nationStats, factionStats } = gameState;
        UIElements.year.textContent = `第 ${year} 年`;
        
        for(const key in playerStats) {
            if (UIElements[key]) UIElements[key].textContent = playerStats[key];
        }
        UIElements.treasury.textContent = nationStats.treasury;

        UIElements.stabilityBar.style.width = `${nationStats.stability}%`;
        UIElements.militaryBar.style.width = `${nationStats.military}%`;
        UIElements.agricultureBar.style.width = `${nationStats.agriculture}%`;

        UIElements.factionsDisplay.innerHTML = '';
        for (const id in factionStats) {
            const faction = factionStats[id];
            const factionEl = document.createElement('div');
            factionEl.className = 'flex justify-between items-center';
            factionEl.innerHTML = `
                <span>${faction.name}</span>
                <div class="flex items-center">
                    <span class="text-xs mr-1 text-gray-400">忠</span>
                    <span class="font-bold ${faction.loyalty > 60 ? 'text-green-400' : faction.loyalty < 40 ? 'text-red-400' : 'text-white'}">${faction.loyalty}</span>
                </div>
            `;
            UIElements.factionsDisplay.appendChild(factionEl);
        }
    }

    function displayEvent(event) {
        currentEventId = event.id;
        UIElements.eventTitle.textContent = event.title;
        UIElements.eventReport.textContent = event.report;
        UIElements.eventChoices.innerHTML = '';
        
        event.choices.forEach(choice => {
            const button = document.createElement('button');
            button.className = 'w-full bg-amber-500/80 text-white font-bold py-3 px-4 rounded-lg shadow-md choice-btn border border-amber-400';
            button.textContent = choice.text;
            button.dataset.choiceId = choice.id;
            button.addEventListener('click', handleChoice);
            UIElements.eventChoices.appendChild(button);
        });
    }

    // --- 核心修改：重构网络请求逻辑，增加错误处理 ---
    async function apiFetch(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "服务器返回了一个非JSON格式的错误。" }));
                throw new Error(`网络请求失败! 状态码: ${response.status}, 信息: ${errorData.error || response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Fetch Error:', error);
            showErrorModal("与服务器通信失败", `无法处理你的请求。这通常是后端代码出错了。\n\n请检查运行 'python app.py' 的终端窗口，寻找红色的错误日志。\n\n前端捕获到的错误: ${error.message}`);
            // 返回一个Promise.reject来中断后续的.then()链
            return Promise.reject(error);
        }
    }

    async function handleChoice(e) {
        const choiceId = e.target.dataset.choiceId;

        UIElements.eventChoices.querySelectorAll('button').forEach(button => {
            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');
        });

        const data = await apiFetch('/api/choice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ eventId: currentEventId, choiceId: choiceId }),
        });
        
        // 如果apiFetch成功，则继续执行
        if (!data) return;

        if (data.result && data.result.description) {
            UIElements.resultText.textContent = data.result.description;
            UIElements.resultBox.classList.remove('hidden');
        }
        
        if (data.new_state) {
            updateUI(data.new_state);
        }
        
        if (data.game_over) {
            setTimeout(() => showEndScreen(data.ending), 1000);
            return; 
        }
        
        setTimeout(fetchNextTurn, 500); 
    }

    async function fetchNextTurn() {
        const data = await apiFetch('/api/next_turn');
        if (!data) return;

        if (data.game_over) {
            if(data.new_state) updateUI(data.new_state);
            setTimeout(() => showEndScreen(data.ending), 1000);
        } else {
            updateUI(data.game_state);
            displayEvent(data.event);
        }
    }
    
    function showEndScreen(ending) {
        if (!ending) {
             showErrorModal("结局错误", "游戏结束，但无法加载结局数据。");
             return;
        }
        UIElements.gameContainer.classList.add('hidden');
        UIElements.modal.classList.remove('hidden');
        UIElements.modalTitle.textContent = ending.title || "游戏结束";
        UIElements.modalText.textContent = ending.text || "发生了一个未知错误。";
        UIElements.modalChoices.innerHTML = '';
        
        const button = document.createElement('button');
        button.className = 'w-full bg-amber-600 text-white font-bold py-3 px-4 rounded-lg shadow-md choice-btn';
        button.textContent = '再开一局';
        button.addEventListener('click', () => window.location.reload());
        UIElements.modalChoices.appendChild(button);
    }

    // 新增：一个专门用来显示错误的模态框
    function showErrorModal(title, text) {
        UIElements.gameContainer.classList.add('hidden');
        UIElements.modal.classList.remove('hidden');
        UIElements.modalTitle.textContent = title;
        UIElements.modalText.textContent = text;
        UIElements.modalChoices.innerHTML = '';
        
        const button = document.createElement('button');
        button.className = 'w-full bg-gray-600 text-white font-bold py-3 px-4 rounded-lg shadow-md choice-btn';
        button.textContent = '刷新重试';
        button.addEventListener('click', () => window.location.reload());
        UIElements.modalChoices.appendChild(button);
    }

    async function startGame(talentId) {
        const data = await apiFetch('/api/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ talentId: talentId }),
        });
        if (!data) return;
        
        UIElements.modal.classList.add('hidden');
        UIElements.gameContainer.classList.remove('hidden');
        
        updateUI(data);
        UIElements.resultBox.classList.add('hidden');
        fetchNextTurn();
    }

    async function showStartScreen() {
        UIElements.gameContainer.classList.add('hidden');
        UIElements.modal.classList.remove('hidden');
        
        const talents = await apiFetch('/api/talents');
        if (!talents) return;

        UIElements.modalTitle.textContent = '选择你的出身';
        UIElements.modalText.textContent = '新的时代已经开始，但王朝的命运悬而未决。你的过去，将决定你的未来。';
        UIElements.modalChoices.innerHTML = '';
        talents.forEach(talent => {
            const button = document.createElement('button');
            button.className = 'w-full bg-amber-600 text-white font-bold py-3 px-4 rounded-lg shadow-md choice-btn';
            button.innerHTML = `${talent.name}<p class="text-sm font-normal text-amber-200 mt-1">${talent.description}</p>`;
            button.dataset.talentId = talent.id;
            button.addEventListener('click', () => startGame(talent.id));
            UIElements.modalChoices.appendChild(button);
        });
    }

    // Initial load
    showStartScreen();
});
