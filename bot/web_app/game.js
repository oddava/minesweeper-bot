const Telegram = window.Telegram.WebApp;

Telegram.ready();
Telegram.expand();

// Mode configurations
const MODES = {
    beginner: { rows: 9, cols: 9, mines: 10 },
    intermediate: { rows: 16, cols: 16, mines: 40 },
    expert: { rows: 16, cols: 30, mines: 99 }
};

// Current game state
let currentMode = 'beginner';
let ROWS = 9;
let COLS = 9;
let MINES = 10;

// DOM Elements
const modeSelectScreen = document.getElementById('mode-select');
const gameScreen = document.getElementById('game-screen');
const boardElement = document.getElementById('board');
const minesCountElement = document.querySelector('.mines-count span');
const timerElement = document.querySelector('.timer-count span');
const resetBtn = document.getElementById('reset-btn');
const toggleInput = document.getElementById('flag-mode-toggle');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const modalText = document.getElementById('modal-text');
const modalClose = document.getElementById('modal-close');
const backBtn = document.getElementById('back-btn');
const bestTimeDisplay = document.getElementById('best-time-display');

let grid = [];
let minesLeft = MINES;
let gameOver = false;
let timer = 0;
let timerInterval;
let firstClick = true;
let isFlagMode = false;
let userStats = null;
let resultSent = false;

// Fetch user stats on load
async function fetchStats() {
    const user = Telegram.initDataUnsafe?.user;
    if (!user) return;

    try {
        const res = await fetch(`/api/stats/${user.id}`);
        userStats = await res.json();
        updateBestTimeDisplay();
    } catch (e) {
        console.error('Failed to fetch stats', e);
    }
}

function updateBestTimeDisplay() {
    if (!userStats || !userStats.modes) return;
    const modeStats = userStats.modes[currentMode];
    if (modeStats && modeStats.best_time) {
        bestTimeDisplay.innerText = `🏆 Best: ${modeStats.best_time}s | Wins: ${modeStats.wins}`;
    } else {
        bestTimeDisplay.innerText = '';
    }
}

// Mode selection handlers
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        startGameWithMode(mode);
    });
});

function startGameWithMode(mode) {
    currentMode = mode;
    const config = MODES[mode];
    ROWS = config.rows;
    COLS = config.cols;
    MINES = config.mines;

    document.documentElement.style.setProperty('--cols', COLS);
    document.documentElement.style.setProperty('--rows', ROWS);

    modeSelectScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');

    initGame();
}

backBtn.addEventListener('click', () => {
    clearInterval(timerInterval);
    gameScreen.classList.add('hidden');
    modeSelectScreen.classList.remove('hidden');
    updateBestTimeDisplay();
});

function initGame() {
    clearInterval(timerInterval);
    boardElement.innerHTML = '';
    grid = [];
    minesLeft = MINES;
    timer = 0;
    gameOver = false;
    firstClick = true;
    resultSent = false;

    updateMinesCounter();
    timerElement.innerText = "000";
    resetBtn.innerText = "🙂";
    modal.classList.add('hidden');

    // Create Grid
    for (let r = 0; r < ROWS; r++) {
        const row = [];
        for (let c = 0; c < COLS; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.r = r;
            cell.dataset.c = c;

            cell.addEventListener('click', () => handleCellClick(r, c));
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                toggleFlag(r, c);
            });

            boardElement.appendChild(cell);
            row.push({
                element: cell,
                isMine: false,
                isRevealed: false,
                isFlagged: false,
                neighbors: 0
            });
        }
        grid.push(row);
    }
}

function placeMines(excludeR, excludeC) {
    let placed = 0;
    while (placed < MINES) {
        const r = Math.floor(Math.random() * ROWS);
        const c = Math.floor(Math.random() * COLS);

        if (!grid[r][c].isMine && (r !== excludeR || c !== excludeC)) {
            grid[r][c].isMine = true;
            placed++;
        }
    }
    calculateNeighbors();
}

function calculateNeighbors() {
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (grid[r][c].isMine) continue;

            let count = 0;
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const nr = r + i;
                    const nc = c + j;
                    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && grid[nr][nc].isMine) {
                        count++;
                    }
                }
            }
            grid[r][c].neighbors = count;
        }
    }
}

function handleCellClick(r, c) {
    if (gameOver) return;

    if (isFlagMode) {
        toggleFlag(r, c);
        return;
    }

    if (firstClick) {
        placeMines(r, c);
        startTimer();
        firstClick = false;
    }

    const cell = grid[r][c];
    if (cell.isFlagged || cell.isRevealed) return;

    if (cell.isMine) {
        revealMines();
        endGame(false);
    } else {
        revealCell(r, c);
        checkWin();
    }
}

function revealCell(startR, startC) {
    const queue = [[startR, startC]];

    while (queue.length > 0) {
        const [r, c] = queue.shift();
        const cell = grid[r][c];

        if (cell.isRevealed || cell.isFlagged) continue;

        cell.isRevealed = true;
        cell.element.classList.add('revealed');

        if (cell.neighbors > 0) {
            cell.element.innerText = cell.neighbors;
            cell.element.dataset.num = cell.neighbors;
        } else {
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    const nr = r + i;
                    const nc = c + j;
                    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !grid[nr][nc].isRevealed) {
                        queue.push([nr, nc]);
                    }
                }
            }
        }
    }
}

function toggleFlag(r, c) {
    if (gameOver) return;
    const cell = grid[r][c];
    if (cell.isRevealed) return;

    cell.isFlagged = !cell.isFlagged;
    cell.element.classList.toggle('flagged');

    minesLeft += cell.isFlagged ? -1 : 1;
    updateMinesCounter();
}

function updateMinesCounter() {
    minesCountElement.innerText = minesLeft;
}

function startTimer() {
    timerInterval = setInterval(() => {
        timer++;
        timerElement.innerText = timer.toString().padStart(3, '0');
    }, 1000);
}

function revealMines() {
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            const cell = grid[r][c];
            if (cell.isMine) {
                cell.element.classList.add('revealed', 'mine');
                cell.element.innerText = '💣';
            }
        }
    }
}

function endGame(win) {
    gameOver = true;
    clearInterval(timerInterval);
    resetBtn.innerText = win ? "😎" : "😵";

    if (win) {
        Telegram.HapticFeedback.notificationOccurred('success');
        showModal('Victory!', `You cleared the field in ${timer} seconds!`);
    } else {
        Telegram.HapticFeedback.notificationOccurred('error');
        showModal('Game Over', 'Better luck next time!');
    }

    sendGameResult(win, timer);
}

function sendGameResult(isWin, score) {
    if (resultSent) return;
    resultSent = true;

    const user = Telegram.initDataUnsafe?.user;
    if (!user) return;

    fetch('/api/game/result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            initData: Telegram.initData,
            user_id: user.id,
            first_name: user.first_name,
            username: user.username,
            score: score,
            is_win: isWin,
            game_mode: currentMode,
            rows: ROWS,
            cols: COLS,
            mines: MINES
        })
    }).then(() => fetchStats()).catch(console.error);
}

function checkWin() {
    let revealedCount = 0;
    for (let r = 0; r < ROWS; r++) {
        for (let c = 0; c < COLS; c++) {
            if (grid[r][c].isRevealed) revealedCount++;
        }
    }

    if (revealedCount === (ROWS * COLS - MINES)) {
        endGame(true);
    }
}

function showModal(title, text) {
    modalTitle.innerText = title;
    modalText.innerText = text;
    modal.classList.remove('hidden');
}

// Controls
resetBtn.addEventListener('click', initGame);
modalClose.addEventListener('click', initGame);

toggleInput.addEventListener('change', (e) => {
    isFlagMode = e.target.checked;
});

// Init
fetchStats();
