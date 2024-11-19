const rows = 6;
const cols = 7;
const board = Array.from(Array(rows), () => Array(cols).fill(null));
let currentPlayer = 1;
let player1Name = '';
let player2Name = '';
const BASE_URL = "http://127.0.0.1:8000"

const boardElement = document.getElementById('board');
const messageElement = document.getElementById('message');
const confettiElement = document.getElementById('confetti');
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

async function createBoard(gameData) {
    gameData = await createGame(player1Name, player2Name);
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.col = c;
            cell.addEventListener('click', () => handleClick(c, gameData));
            boardElement.appendChild(cell);
        }
    }
}

async function handleClick(col, gameData) {
    game_state = await playMove(gameData['id'], col, currentPlayer)
    console.log(game_state)
    if (game_state){
        dropPiece(game_state['row'], col);
        gameData = game_state
        if (gameData['status'] == 'won'){
            celebrateWin()
        } else {
            currentPlayer = gameData['current_turn']
            messageElement.textContent = `${currentPlayer} à vous de jouer !`;
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

function celebrateWin() {
    messageElement.textContent = `${currentPlayer === 1 ? player1Name : player2Name} a gagné !`;
    boardElement.style.pointerEvents = 'none';
    restartButton.style.display = 'block'; // Afficher le bouton rejouer
    createConfetti();
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
        id : 1,
        players: [
            { id: 1, name: player1 },
            { id: 2, name: player2 }
        ],
        current_turn: 1,
        board: Array.from({ length: 6 }, () => Array(7).fill(0))  // Plateau vide
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
