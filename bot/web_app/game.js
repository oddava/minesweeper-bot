const Telegram = window.Telegram.WebApp;
Telegram.ready();
Telegram.expand();

// Settings
const SETTINGS_KEY = 'minesweeper_settings';
let settings = { theme: 'classic', vibration: true };

function loadSettings() {
    try {
        const saved = localStorage.getItem(SETTINGS_KEY);
        if (saved) settings = { ...settings, ...JSON.parse(saved) };
    } catch (e) { }
    applyTheme(settings.theme);
    document.getElementById('vibration-toggle').checked = settings.vibration;
}

function saveSettings() {
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch (e) { }
}

function applyTheme(name) {
    document.body.className = name === 'classic' ? '' : `theme-${name}`;
    settings.theme = name;
    saveSettings();
    document.querySelectorAll('.theme-option').forEach(b =>
        b.classList.toggle('active', b.dataset.theme === name));
}

function haptic(type) {
    if (settings.vibration && Telegram.HapticFeedback) {
        Telegram.HapticFeedback.notificationOccurred(type);
    }
}

// Game config
const MODES = {
    beginner: { rows: 9, cols: 9, mines: 10 },
    intermediate: { rows: 16, cols: 16, mines: 40 },
    expert: { rows: 16, cols: 30, mines: 99 }
};

let mode = 'beginner', ROWS = 9, COLS = 9, MINES = 10;
let grid = [], minesLeft = 10, timer = 0, timerInterval;
let gameOver = false, firstClick = true, flagMode = false;
let clicks = 0, flags = 0, resultSent = false, userStats = null;

// DOM
const $ = id => document.getElementById(id);
const modeSelect = $('mode-select'), gameScreen = $('game-screen'), board = $('board');
const minesEl = document.querySelector('.mines-count span');
const timerEl = document.querySelector('.timer-count span');
const resetBtn = $('reset-btn'), flagToggle = $('flag-mode-toggle');
const backBtn = $('back-btn'), bestTimeDisplay = $('best-time-display');
const settingsBtn = $('settings-btn'), settingsModal = $('settings-modal');
const settingsClose = $('settings-close'), vibrationToggle = $('vibration-toggle');
const statsContainer = $('game-stats'), statsTitle = $('stats-title');
const statTime = $('stat-time'), statBest = $('stat-best');
const statClicks = $('stat-clicks'), statFlags = $('stat-flags');
const bestTimeStat = $('best-time-stat');

// Stats API
async function fetchStats() {
    const user = Telegram.initDataUnsafe?.user;
    if (!user) return;
    try {
        const res = await fetch(`/api/stats/${user.id}`);
        userStats = await res.json();
        updateBestTime();
    } catch (e) { }
}

function updateBestTime() {
    if (!userStats?.modes) return;
    const s = userStats.modes[mode];
    bestTimeDisplay.textContent = s?.best_time ? `🏆 Best: ${s.best_time}s | Wins: ${s.wins}` : '';
}

function getBest() {
    return userStats?.modes?.[mode]?.best_time || null;
}

// Game logic
function cellSize(cols, rows) {
    const w = window.innerWidth - 40, h = window.innerHeight - 200;
    return Math.max(26, Math.min(Math.floor(Math.min(w / cols, h / rows)), 36));
}

function startGame(m) {
    mode = m;
    const cfg = MODES[m];
    ROWS = cfg.rows; COLS = cfg.cols; MINES = cfg.mines;
    const size = cellSize(COLS, ROWS);
    document.documentElement.style.setProperty('--cell-size', `${size}px`);
    document.documentElement.style.setProperty('--cols', COLS);
    document.documentElement.style.setProperty('--rows', ROWS);
    modeSelect.classList.add('hidden');
    gameScreen.classList.remove('hidden');
    initGame();
}

function initGame() {
    clearInterval(timerInterval);
    board.innerHTML = '';
    grid = []; minesLeft = MINES; timer = 0;
    gameOver = false; firstClick = true; resultSent = false;
    clicks = 0; flags = 0;
    minesEl.textContent = minesLeft;
    timerEl.textContent = '000';
    resetBtn.textContent = '🙂';
    statsContainer.classList.remove('visible');

    for (let r = 0; r < ROWS; r++) {
        const row = [];
        for (let c = 0; c < COLS; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.onclick = () => onClick(r, c);
            cell.oncontextmenu = e => { e.preventDefault(); toggleFlag(r, c); };
            board.appendChild(cell);
            row.push({ el: cell, mine: false, revealed: false, flagged: false, n: 0 });
        }
        grid.push(row);
    }
}

function placeMines(er, ec) {
    let placed = 0;
    while (placed < MINES) {
        const r = Math.floor(Math.random() * ROWS);
        const c = Math.floor(Math.random() * COLS);
        if (!grid[r][c].mine && (r !== er || c !== ec)) {
            grid[r][c].mine = true;
            placed++;
        }
    }
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (grid[r][c].mine) continue;
            let n = 0;
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const nr = r + i, nc = c + j;
                    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && grid[nr][nc].mine) n++;
                }
            }
            grid[r][c].n = n;
        }
    }
}

function onClick(r, c) {
    if (gameOver) return;
    clicks++;
    if (flagMode) { toggleFlag(r, c); return; }
    if (firstClick) { placeMines(r, c); startTimer(); firstClick = false; }
    const cell = grid[r][c];
    if (cell.flagged || cell.revealed) return;
    if (cell.mine) { revealMines(); endGame(false); }
    else { reveal(r, c); checkWin(); }
}

function reveal(sr, sc) {
    const q = [[sr, sc]];
    while (q.length) {
        const [r, c] = q.shift();
        const cell = grid[r][c];
        if (cell.revealed || cell.flagged) continue;
        cell.revealed = true;
        cell.el.classList.add('revealed');
        if (cell.n > 0) {
            cell.el.textContent = cell.n;
            cell.el.dataset.num = cell.n;
        } else {
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const nr = r + i, nc = c + j;
                    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !grid[nr][nc].revealed) {
                        q.push([nr, nc]);
                    }
                }
            }
        }
    }
}

function toggleFlag(r, c) {
    if (gameOver) return;
    const cell = grid[r][c];
    if (cell.revealed) return;
    cell.flagged = !cell.flagged;
    cell.el.classList.toggle('flagged');
    flags += cell.flagged ? 1 : -1;
    minesLeft += cell.flagged ? -1 : 1;
    minesEl.textContent = minesLeft;
}

function startTimer() {
    timerInterval = setInterval(() => {
        timer++;
        timerEl.textContent = timer.toString().padStart(3, '0');
    }, 1000);
}

function revealMines() {
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const cell = grid[r][c];
            if (cell.mine) {
                cell.el.classList.add('revealed', 'mine');
                cell.el.textContent = '💣';
            }
        }
    }
}

function endGame(win) {
    gameOver = true;
    clearInterval(timerInterval);
    resetBtn.textContent = win ? '😎' : '😵';
    haptic(win ? 'success' : 'error');
    showStats(win);
    sendResult(win);
}

function showStats(win) {
    statsTitle.textContent = win ? '🎉 Victory!' : '💥 Game Over';
    statTime.textContent = timer;
    statClicks.textContent = clicks;
    statFlags.textContent = flags;
    const best = getBest();
    if (best) {
        statBest.textContent = (win && timer < best) ? `${timer}s 🆕` : `${best}s`;
        bestTimeStat.classList.toggle('highlight', win && timer < best);
    } else {
        statBest.textContent = win ? `${timer}s 🆕` : '-';
        bestTimeStat.classList.toggle('highlight', win);
    }
    statsContainer.classList.add('visible');
}

function sendResult(win) {
    if (resultSent) return;
    resultSent = true;
    const user = Telegram.initDataUnsafe?.user;
    if (!user) return;
    fetch('/api/game/result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            initData: Telegram.initData,
            user_id: user.id, first_name: user.first_name, username: user.username,
            score: timer, is_win: win, game_mode: mode, rows: ROWS, cols: COLS, mines: MINES
        })
    }).then(() => fetchStats()).catch(() => { });
}

function checkWin() {
    let count = 0;
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (grid[r][c].revealed) count++;
        }
    }
    if (count === ROWS * COLS - MINES) endGame(true);
}

// Events
document.querySelectorAll('.mode-btn').forEach(b =>
    b.addEventListener('click', () => startGame(b.dataset.mode)));

resetBtn.addEventListener('click', initGame);
backBtn.addEventListener('click', () => {
    clearInterval(timerInterval);
    gameScreen.classList.add('hidden');
    modeSelect.classList.remove('hidden');
    updateBestTime();
});

flagToggle.addEventListener('change', e => flagMode = e.target.checked);

settingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
settingsClose.addEventListener('click', () => settingsModal.classList.add('hidden'));
settingsModal.addEventListener('click', e => {
    if (e.target === settingsModal) settingsModal.classList.add('hidden');
});

document.querySelectorAll('.theme-option').forEach(b =>
    b.addEventListener('click', () => applyTheme(b.dataset.theme)));

vibrationToggle.addEventListener('change', e => {
    settings.vibration = e.target.checked;
    saveSettings();
    if (settings.vibration) haptic('success');
});

// Init
loadSettings();
fetchStats();
