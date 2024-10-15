const rows = 6;
const cols = 7;
const board = Array.from(Array(rows), () => Array(cols).fill(null));
let currentPlayer = 1;
let player1Name = '';
let player2Name = '';

const boardElement = document.getElementById('board');
const messageElement = document.getElementById('message');
const startButton = document.getElementById('startButton');
const restartButton = document.getElementById('restartButton');

startButton.addEventListener('click', () => {
    player1Name = document.getElementById('player1Name').value;
    player2Name = document.getElementById('player2Name').value;

    if (player1Name && player2Name) {
        document.getElementById('nameForm').style.display = 'none';
        boardElement.style.display = 'grid';
        messageElement.style.display = 'block';
        restartButton.style.display = 'none';
        createBoard();
        messageElement.textContent = `${player1Name} (Rouge) à vous de jouer !`;
    }
});

restartButton.addEventListener('click', resetGame);

function resetGame() {
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            board[r][c] = null;
        }
    }
    currentPlayer = 1;
    messageElement.textContent = `${player1Name} (Rouge) à vous de jouer !`;
    boardElement.innerHTML = '';
    confettiElement.innerHTML = '';
    confettiElement.style.display = 'none';
    createBoard();
    boardElement.style.pointerEvents = 'auto';
    restartButton.style.display = 'none';
}

function createBoard() {
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.col = c;
            cell.addEventListener('click', () => handleClick(c));
            boardElement.appendChild(cell);
        }
    }
}

function handleClick(col) {
    for (let r = rows - 1; r >= 0; r--) {
        if (!board[r][col]) {
            board[r][col] = currentPlayer;
            dropPiece(r, col);
            if (checkWin(r, col)) {
                celebrateWin(r, col);
            } else {
                currentPlayer = currentPlayer === 1 ? 2 : 1;
                messageElement.textContent = `${currentPlayer === 1 ? player1Name : player2Name} à vous de jouer !`;
            }
            return;
        }
    }
}

function dropPiece(row, col) {
    const piece = document.createElement('div');
    piece.classList.add('piece', currentPlayer === 1 ? 'player1' : 'player2');
    boardElement.appendChild(piece);

    piece.style.left = `calc(${col * 55}px + 5px)`;
    piece.style.top = `5px`;
    piece.style.zIndex = `1`;

    requestAnimationFrame(() => {
        piece.style.transition = 'transform 0.5s ease';
        piece.style.transform = `translateY(${(row * 55)}px)`;
    });
}

function celebrateWin(row, col) {
    messageElement.textContent = `${currentPlayer === 1 ? player1Name : player2Name} a gagné !`;
    boardElement.style.pointerEvents = 'none';
    restartButton.style.display = 'block';

    const winPieces = getWinningPieces(row, col);
    winPieces.forEach(([r, c]) => {
        const cell = boardElement.children[r * cols + c];
        cell.classList.add('blink');
    });

    createConfetti();
}

function getWinningPieces(row, col) {
    const directions = [
        [1, 0], // horizontal
        [0, 1], // vertical
        [1, 1], // diagonal \
        [1, -1] // diagonal /
    ];
    let winPieces = [];
    for (const [rowInc, colInc] of directions) {
        let count = 0;
        let pieces = [];
        for (let i = -3; i <= 3; i++) {
            const r = row + i * rowInc;
            const c = col + i * colInc;
            if (r >= 0 && r < rows && c >= 0 && c < cols && board[r][c] === currentPlayer) {
                count++;
                pieces.push([r, c]);
                if (count === 4) {
                    winPieces = pieces;
                    break;
                }
            } else {
                count = 0;
                pieces = [];
            }
        }
    }
    return winPieces;
}

function checkWin(row, col) {
    return checkDirection(row, col, 1, 0) || // Horizontal
           checkDirection(row, col, 0, 1) || // Vertical
           checkDirection(row, col, 1, 1) || // Diagonal \
           checkDirection(row, col, 1, -1);  // Diagonal /
}

function checkDirection(row, col, rowInc, colInc) {
    let count = 0;
    for (let i = -3; i <= 3; i++) {
        const r = row + i * rowInc;
        const c = col + i * colInc;
        if (r >= 0 && r < rows && c >= 0 && c < cols && board[r][c] === currentPlayer) {
            count++;
            if (count === 4) return true;
        } else {
            count = 0;
        }
    }
    return false;
}