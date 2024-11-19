document.addEventListener('DOMContentLoaded', function() {
    const rows = 6;
    const cols = 7;
    const board = Array.from(Array(rows), () => Array(cols).fill(null));
    let currentPlayer = 1;
    let player1Name = '';
    let player2Name = 'Adversaire';

    const boardElement = document.getElementById('board');
    const messageElement = document.getElementById('message');
    const confettiElement = document.getElementById('confetti');
    const startButton = document.getElementById('startButton');
    const restartButton = document.getElementById('restartButton');

    startButton.addEventListener('click', () => {
        player1Name = document.getElementById('player1Name').value;

        if (player1Name) {
            document.getElementById('nameForm').style.display = 'none';
            boardElement.style.display = 'grid';
            messageElement.style.display = 'block';
            restartButton.style.display = 'none';
            createBoard();
            messageElement.textContent = `${player1Name} à vous de jouer !`;
        }
    });

    restartButton.addEventListener('click', resetGame);

    function resetGame() {
        // Réinitialiser le tableau et les éléments
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                board[r][c] = null;
            }
        }
        currentPlayer = 1;
        messageElement.textContent = `${player1Name} à vous de jouer !`;
        boardElement.innerHTML = ''; // Vider le plateau
        confettiElement.innerHTML = ''; // Vider les confettis
        confettiElement.style.display = 'none'; // Cacher les confettis
        createBoard(); // Recréer le plateau
        boardElement.style.pointerEvents = 'auto'; // Réactiver les clics
        restartButton.style.display = 'none'; // Cacher le bouton rejouer
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
                    if (currentPlayer === 2) {
                        setTimeout(() => {
                            handleClick(Math.floor(Math.random() * cols)); // Adversaire fictif joue un coup aléatoire
                        }, 1000);
                    }
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
        restartButton.style.display = 'block'; // Afficher le bouton rejouer

        // Récupérer la direction des pièces gagnantes
        const winPieces = getWinningPieces(row, col);
        winPieces.forEach(([r, c]) => {
            const cell = boardElement.children[r * cols + c];
            cell.classList.add('blink'); // Appliquer le clignotement
        });

        createConfetti();

        // Mettre à jour le score du gagnant
        const winnerName = currentPlayer === 1 ? player1Name : player2Name;
        updateScore(winnerName, 1);
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

    function createConfetti() {
        confettiElement.style.display = 'block';
        for (let i = 0; i < 100; i++) {
            const confettiPiece = document.createElement('div');
            confettiPiece.classList.add('confetti-piece');
            confettiPiece.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
            confettiPiece.style.left = `${Math.random() * 100}%`;
            confettiPiece.style.animationDelay = `${Math.random() * 2}s`;
            confettiPiece.style.transform = `translateY(-50px) rotate(${Math.random() * 360}deg)`;
            confettiElement.appendChild(confettiPiece);

            // Enlever le confetti après animation
            setTimeout(() => {
                confettiPiece.remove();
            }, 3000);
        }
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

    function updateScore(name, score) {
        fetch('http://localhost:8000/game/update_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                score: score
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || "Erreur lors de la mise à jour du score");
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Score mis à jour:', data);
        })
        .catch(error => {
            console.error('Erreur:', error.message);
        });
    }
});