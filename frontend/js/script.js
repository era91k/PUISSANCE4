document.addEventListener('DOMContentLoaded', function() {
    const rows = 6;
    const cols = 7;
    const board = Array.from(Array(rows), () => Array(cols).fill(null));
    let currentPlayer = 1;
    let player1Name = localStorage.getItem('username') || 'NomUtilisateurStocke'; // Récupérer le nom stocké dans le stockage local
    let player2Name = 'Adversaire';
    const BASE_URL = "http://127.0.0.1:8000"

    const boardElement = document.getElementById('board');
    const messageElement = document.getElementById('message');
    const confettiElement = document.getElementById('confetti');
    const startButton = document.getElementById('startButton');
    const restartButton = document.getElementById('restartButton');

    // Pré-remplir le champ de saisie du nom avec le nom stocké dans le stockage local
    document.getElementById('player1Name').value = player1Name;

    startButton.addEventListener('click', async () => {
        player1Name = document.getElementById('player1Name').value;

        if (player1Name) {
            document.getElementById('nameForm').style.display = 'none';
            boardElement.style.display = 'grid';
            messageElement.style.display = 'block';
            restartButton.style.display = 'none';
            const gameData = await createGame(player1Name, player2Name);
            if (gameData) {
                console.log("Game data:", gameData);
                createBoard(gameData);
                messageElement.textContent = `${player1Name} à vous de jouer !`;
            } else {
                console.error("Failed to create game");
            }
        }
    });

    restartButton.addEventListener('click', resetGame);

    async function resetGame() {
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
        boardElement.style.pointerEvents = 'auto'; // Réactiver les clics
        restartButton.style.display = 'none'; // Cacher le bouton rejouer

        // Créer une nouvelle partie
        const gameData = await createGame(player1Name, player2Name);
        if (gameData) {
            createBoard(gameData);
        } else {
            console.error("Failed to create game");
        }
    }

    async function createBoard(gameData) {
        console.log("Creating board...");
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.col = c;
                cell.addEventListener('click', () => handleClick(c, gameData));
                boardElement.appendChild(cell);
            }
        }
        console.log("Board created");
    }

    async function handleClick(col, gameData) {
        const game_state = await playMove(gameData.id, col, currentPlayer);
        if (game_state) {
            const { row } = game_state; // On suppose que l'API renvoie la ligne jouée
            board[row][col] = currentPlayer; // Mise à jour du tableau logique
            dropPiece(row, col);
            gameData = game_state;
    
            if (checkWin(row, col)) { // Vérifiez la victoire
                celebrateWin(gameData);
            } else {
                currentPlayer = gameData.current_turn;
                messageElement.textContent = `${currentPlayer === 1 ? player1Name : player2Name} à vous de jouer !`;
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

    function celebrateWin(gameData) {
        const winnerName = currentPlayer === 1 ? player1Name : player2Name;
        console.log(`${winnerName} a gagné !`);
        messageElement.textContent = `${winnerName} a gagné !`;
        boardElement.style.pointerEvents = 'none';
        restartButton.style.display = 'block'; // Afficher le bouton rejouer
        createConfetti();
    
        // Mettre à jour le score du gagnant
        if (winnerName !== 'Adversaire') {
            updateScore(winnerName, 1);
        }
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

    async function createGame(player1, player2) {
        const gameData = {
            id: Date.now(),  // Utiliser un ID unique basé sur l'heure actuelle
            players: [
                { id: 1, name: player1 },
                { id: 2, name: player2 }
            ],
            current_turn: 1,
            board: Array.from({ length: 6 }, () => Array(7).fill(0)),  // Plateau vide
            status: "active"
        };

        try {
            const response = await fetch(`${BASE_URL}/game/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gameData)
            });

            if (response.ok) {
                const game = await response.json();  // Attendre le JSON
                console.log("Game created successfully:", game);
                return game;  // Retourner l'objet game créé
            } else {
                const errorData = await response.json();  // Attendre le JSON des erreurs
                console.error("Failed to create game:", errorData.detail);  // Accéder au message d'erreur
                return null;  // Retourner null si la création échoue
            }
        } catch (error) {
            console.error("Error creating game:", error);
            return null;  // Retourner null en cas d'erreur
        }
    }

    async function playMove(gameId, column, playerId) {
        try {
            const response = await fetch(`${BASE_URL}/game/${gameId}/play?column=${column}&player_id=${playerId}`, {
                method: 'PUT'
            });

            if (response.ok) {
                console.log("Move played successfully!");
                return await response.json();  // Renvoie l'état mis à jour du jeu
            } else {
                const errorData = await response.json();
                console.error("Failed to play move:", errorData);
                return null;
            }
        } catch (error) {
            console.error("Error:", error);
            return null;
        }
    }

    function updateScore(name, score) {
        fetch(`${BASE_URL}/game/update_score`, {
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
});