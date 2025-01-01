document.addEventListener('DOMContentLoaded', function() {
  const rows = 6;
  const cols = 7;
  const board = Array.from(Array(rows), () => Array(cols).fill(null));
  let previousBoardState = Array.from({ length: rows }, () => Array(cols).fill(0));

  let currentPlayer = 1;
  let player1Name = localStorage.getItem('username') || 'Joueur1';
  let player2Name = 'Joueur2';
  const BASE_URL = "http://127.0.0.1:8000";

  const boardElement = document.getElementById('board');
  const messageElement = document.getElementById('message');
  const confettiElement = document.getElementById('confetti');
  const startButton = document.getElementById('startButton');
  const restartButton = document.getElementById('restartButton');
  const createOnlineGameButton = document.getElementById('createOnlineGameButton');
  const joinOnlineGameButton = document.getElementById('joinOnlineGameButton');
  const onlinePlayerNameInput = document.getElementById('onlinePlayerName');
  const onlineGameCodeInput = document.getElementById('onlineGameCode');

  document.getElementById('player1Name').value = player1Name;

  let isOnlineGame = false;
  let onlineGameCode = null;
  let localPlayerId = 1;
  let pollIntervalId = null;
  let gameOver = false; // Will be true when game is won/draw, reset to false after reset or new game

  startButton.addEventListener('click', async () => {
      player1Name = document.getElementById('player1Name').value.trim() || 'Joueur1';
      document.getElementById('nameForm').style.display = 'none';
      boardElement.style.display = 'grid';
      messageElement.style.display = 'block';
      restartButton.style.display = 'none';
      isOnlineGame = false;

      const gameData = await createGame(player1Name, player2Name);
      if (gameData) {
          createBoard(gameData);
          messageElement.textContent = `${player1Name}, c'est votre tour !`;
      }
  });

  restartButton.addEventListener('click', resetGame);

  createOnlineGameButton.addEventListener('click', async () => {
      const playerName = onlinePlayerNameInput.value.trim();
      const gameCode = onlineGameCodeInput.value.trim();

      if (!playerName || !gameCode) {
          alert("Veuillez remplir le nom et le code de la partie.");
          return;
      }

      try {
          const response = await fetch(`${BASE_URL}/game/online`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ playerName, gameCode })
          });

          if (response.ok) {
              alert("Partie en ligne créée ! Attente de l'autre joueur...");
              isOnlineGame = true;
              localPlayerId = 1;
              onlineGameCode = gameCode;
              player1Name = playerName;
              player2Name = '';

              document.getElementById('nameForm').style.display = 'none';
              boardElement.style.display = 'grid';
              messageElement.style.display = 'block';
              messageElement.textContent = "Vous êtes l'hôte. En attente d'un autre joueur...";
              createBoard({});
              previousBoardState = blankBoard(rows, cols);
              pollForOpponent(gameCode);
          } else {
              const err = await response.json();
              alert(err.detail || "Erreur création.");
          }
      } catch (err) {
          console.error("Erreur création online:", err);
      }
  });

  joinOnlineGameButton.addEventListener('click', async () => {
      const playerName = onlinePlayerNameInput.value.trim();
      const gameCode = onlineGameCodeInput.value.trim();

      if (!playerName || !gameCode) {
          alert("Veuillez remplir le nom et le code.");
          return;
      }

      try {
          const response = await fetch(`${BASE_URL}/game/online/join`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ playerName, gameCode })
          });

          if (response.ok) {
              const data = await response.json();
              alert("Partie rejointe : " + data.message);
              isOnlineGame = true;
              localPlayerId = 2;
              onlineGameCode = gameCode;
              player2Name = playerName;

              document.getElementById('nameForm').style.display = 'none';
              boardElement.style.display = 'grid';
              messageElement.style.display = 'block';
              createBoard({});
              previousBoardState = blankBoard(rows, cols);
              loadGameGrid(gameCode);
          } else {
              const err = await response.json();
              alert(err.detail || "Erreur join.");
          }
      } catch (err) {
          console.error("Erreur joinOnlineGame:", err);
      }
  });

  function pollForOpponent(gameCode) {
      const intervalId = setInterval(async () => {
          try {
              const resp = await fetch(`${BASE_URL}/game/online/${gameCode}`);
              if (!resp.ok) return;
              const data = await resp.json();

              if (data.player1) player1Name = data.player1;
              if (data.player2) player2Name = data.player2;

              if (data.status === 'ready') {
                  clearInterval(intervalId);
                  messageElement.textContent = `Le joueur ${player2Name} a rejoint !`;
                  pollForMoves(gameCode);
              }
          } catch (err) {
              console.error("pollForOpponent:", err);
          }
      }, 2000);
  }

  /**
   * Main polling for an online game
   * - We do NOT stop polling on 'won' or 'draw', so that if a reset happens,
   *   we see 'active' again and resume.
   */
  function pollForMoves(gameCode) {
    // Clear old polling if any
    if (pollIntervalId) {
      clearInterval(pollIntervalId);
    }

    pollIntervalId = setInterval(async () => {
        try {
            const resp = await fetch(`${BASE_URL}/game/online/${gameCode}`);
            if (!resp.ok) return;
            const data = await resp.json();

            // Sync names
            if (data.player1) player1Name = data.player1;
            if (data.player2) player2Name = data.player2;

            // Check game status
            if (data.status === "won") {
                // Mark gameOver only once
                if (!gameOver) {
                    gameOver = true;
                    renderOnlineBoard(data);
                    celebrateWinOnline(data.winner_id, data);
                }
            } else if (data.status === "draw") {
                if (!gameOver) {
                    gameOver = true;
                    renderOnlineBoard(data);
                    messageElement.textContent = "Match nul !";
                    boardElement.style.pointerEvents = "none";
                    restartButton.style.display = "block";
                }
            } else if (data.status === "active") {
                // If previously gameOver, but now active => a reset happened
                if (gameOver) {
                    gameOver = false;
                    boardElement.style.pointerEvents = "auto";
                    restartButton.style.display = "none";
                    messageElement.textContent = "La partie est réinitialisée !";
                }
                // Render the new board & set turns
                renderOnlineBoard(data);
                updateOnlineTurn(data);
            }
        } catch (err) {
            console.error("pollForMoves error:", err);
        }
    }, 2000);
  }

  /**
   * Decide whose turn it is & enable/disable board accordingly.
   */
  function updateOnlineTurn(data) {
    if (gameOver) {
      // If the game ended, no one can play
      boardElement.style.pointerEvents = "none";
      return;
    }

    if (data.current_turn === localPlayerId) {
        boardElement.style.pointerEvents = "auto";
        messageElement.textContent = "C'est votre tour !";
    } else {
        boardElement.style.pointerEvents = "none";
        const other = (localPlayerId === 1) ? (data.player2 || 'Joueur2') : (data.player1 || 'Joueur1');
        messageElement.textContent = `C'est au tour de ${other} !`;
    }
  }

  function renderOnlineBoard(data) {
      boardElement.innerHTML = '';
      createCellsForClick();

      for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
              const val = data.board[r][c];
              if (val !== 0) {
                  const piece = document.createElement('div');
                  piece.classList.add('piece', val === 1 ? 'player1' : 'player2');
                  piece.style.left = `calc(${c * 55}px + 5px)`;
                  piece.style.top = '5px';
                  piece.style.zIndex = 1;

                  if (previousBoardState[r][c] === 0) {
                      requestAnimationFrame(() => {
                          piece.style.transition = 'transform 0.2s ease';
                          piece.style.transform = `translateY(${r * 55}px)`;
                      });
                  } else {
                      piece.style.transform = `translateY(${r * 55}px)`;
                  }
                  boardElement.appendChild(piece);
              }
          }
      }
      previousBoardState = data.board.map(row => [...row]);
  }

  /**
   * Single resetOnlineGame function
   */
  async function resetOnlineGame(gameCode) {
    try {
        const resp = await fetch(`${BASE_URL}/game/online/${gameCode}/reset`, { method: 'PUT' });
        if (!resp.ok) {
            const e = await resp.json();
            alert(e.detail || "Erreur lors de la réinitialisation de la partie en ligne");
            return;
        }
        const data = await resp.json();

        // Clear local gameOver so we can continue
        gameOver = false;

        // Clear poll interval
        if (pollIntervalId) {
            clearInterval(pollIntervalId);
        }

        // Immediately reset visuals
        boardElement.innerHTML = '';
        previousBoardState = blankBoard(rows, cols);
        createBoard({});
        messageElement.textContent = "La partie est réinitialisée ! À vous de jouer.";

        // Restart polling to see the new empty board & status
        pollForMoves(gameCode);

    } catch (error) {
        console.error("resetOnlineGame error:", error);
    }
  }

  /**
   * Universal reset button
   * - If online => resetOnlineGame
   * - Else => normal offline reset
   */
  async function resetGame() {
      if (isOnlineGame && onlineGameCode) {
        await resetOnlineGame(onlineGameCode);
        return;
      }
      // Offline reset
      for (let r = 0; r < rows; r++) {
          for (let c = 0; c < cols; c++) {
              board[r][c] = null;
          }
      }
      currentPlayer = 1;
      messageElement.textContent = `${player1Name}, c'est votre tour !`;
      boardElement.innerHTML = '';
      confettiElement.innerHTML = '';
      confettiElement.style.display = 'none';
      boardElement.style.pointerEvents = 'auto';
      restartButton.style.display = 'none';

      previousBoardState = blankBoard(rows, cols);

      const gd = await createGame(player1Name, player2Name);
      if (gd) createBoard(gd);
  }

  async function createBoard(gameData) {
      boardElement.innerHTML = '';
      createCellsForClick(gameData);
  }

  function createCellsForClick(gameData) {
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

  /**
   * Clicking on a column -> either do offline or online move
   */
  async function handleClick(col, gameData) {
      if (isOnlineGame && onlineGameCode) {
          try {
              // Double-check it's actually our turn
              const st = await fetch(`${BASE_URL}/game/online/${onlineGameCode}`);
              if (!st.ok) return;
              const currentData = await st.json();

              if (currentData.current_turn !== localPlayerId) {
                  alert("Pas votre tour!");
                  return;
              }
              // Make the move
              const moveResult = await playMoveOnline(onlineGameCode, col, localPlayerId);
              if (moveResult) {

                  // ADD: Immediately render the updated board so the last disc is visible
                  const updatedData = {
                      ...currentData,
                      board: moveResult.board
                  };
                  renderOnlineBoard(updatedData);
                  previousBoardState = updatedData.board.map(row => [...row]);

                  if (moveResult.status === 'won') {
                      // Use moveResult.winner_id to ensure correct winner
                      setTimeout(() => celebrateWinOnline(moveResult.winner_id, updatedData), 100);
                  } else if (moveResult.status === 'draw') {
                      messageElement.textContent = "Match nul !";
                      boardElement.style.pointerEvents = 'none';
                      restartButton.style.display = 'block';
                  }
              }
          } catch (err) {
              console.error("handleClick(online) err:", err);
          }
      } else {
          // Offline move
          const st = await playMove(gameData.id, col, currentPlayer);
          if (st) {
              const { row } = st;
              board[row][col] = st.player_id;
              dropPiece(row, col);

              if (st.status === 'won') {
                  setTimeout(() => celebrateWinOffline(st.player_id), 100);
              } else if (st.status === 'draw') {
                  messageElement.textContent = "Match nul !";
                  boardElement.style.pointerEvents = 'none';
                  restartButton.style.display = 'block';
              } else {
                  currentPlayer = st.current_turn;
                  if (currentPlayer === 1) {
                      messageElement.textContent = "C'est votre tour !";
                  } else {
                      messageElement.textContent = "C'est au tour de l'adversaire !";
                  }
              }
          }
      }
  }

  async function playMoveOnline(gc, col, pid) {
      try {
          const resp = await fetch(`${BASE_URL}/game/online/${gc}/play?column=${col}&player_id=${pid}`, {
              method: 'PUT'
          });
          if (!resp.ok) {
              const e = await resp.json();
              console.error("playMoveOnline error:", e);
              return null;
          }
          return await resp.json();
      } catch (err) {
          console.error("playMoveOnline catch:", err);
          return null;
      }
  }

  async function loadGameGrid(gc) {
      try {
          const r = await fetch(`${BASE_URL}/game/online/${gc}`);
          if (!r.ok) {
              const e = await r.json();
              alert(e.detail || "Erreur loadGameGrid");
              return;
          }
          const data = await r.json();
          if (data.player1) player1Name = data.player1;
          if (data.player2) player2Name = data.player2;

          document.getElementById('nameForm').style.display = 'none';
          boardElement.style.display = 'grid';
          messageElement.style.display = 'block';
          createBoard({});
          previousBoardState = blankBoard(rows, cols);

          if (data.status === 'ready') {
              pollForMoves(gc);
          } else if (data.status === 'waiting') {
              alert("En attente d'un autre joueur...");
              messageElement.textContent = "En attente...";
              pollForMoves(gc);
          } else {
              pollForMoves(gc);
          }
      } catch (er) {
          console.error("loadGameGrid err:", er);
      }
  }

  function dropPiece(row, col) {
      const piece = document.createElement('div');
      piece.classList.add('piece', currentPlayer === 1 ? 'player1' : 'player2');
      boardElement.appendChild(piece);

      piece.style.left = `calc(${col * 55}px + 5px)`;
      piece.style.top = '5px';
      piece.style.zIndex = 1;

      requestAnimationFrame(() => {
          piece.style.transition = 'transform 0.2s ease';
          piece.style.transform = `translateY(${row * 55}px)`;
      });
  }

  function celebrateWinOffline(wpid) {
      const winnerName = (wpid === 1) ? player1Name : player2Name;
      messageElement.textContent = `${winnerName} a gagné !`;
      boardElement.style.pointerEvents = 'none';
      restartButton.style.display = 'block';

      setTimeout(() => {
          createConfetti();
          if (winnerName !== 'Joueur2' && winnerName !== 'Adversaire') {
              updateScore(winnerName, 1);
          }
      }, 100);
  }

  /**
   * Online winning scenario – we rely on the server's "winner_id".
   */
  function celebrateWinOnline(winnerId, data) {
      gameOver = true;
      // The actual winner:
      const winnerName = (winnerId === 1) ? player1Name : player2Name;
      messageElement.textContent = `${winnerName} a gagné !`;
      boardElement.style.pointerEvents = "none";
      restartButton.style.display = "block";

      // If *we* are the winner, update our score
      if (winnerId === localPlayerId) {
          setTimeout(() => {
              createConfetti();
              updateScore(winnerName, 1);
          }, 100);
      }
  }

  async function createGame(p1, p2) {
      const payload = {
          id: Date.now(),
          players: [
              { id: 1, name: p1 },
              { id: 2, name: p2 }
          ],
          current_turn: 1,
          board: Array.from({ length: 6 }, () => Array(7).fill(0)),
          status: "active"
      };
      try {
          const resp = await fetch(`${BASE_URL}/game/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          });
          if (!resp.ok) {
              const e = await resp.json();
              console.error("createGame error:", e);
              return null;
          }
          return await resp.json();
      } catch (err) {
          console.error("createGame catch:", err);
          return null;
      }
  }

  async function playMove(gameId, column, playerId) {
      try {
          const resp = await fetch(`${BASE_URL}/game/${gameId}/play?column=${column}&player_id=${playerId}`, {
              method: 'PUT'
          });
          if (!resp.ok) {
              const e = await resp.json();
              console.error("Failed to play move offline:", e);
              return null;
          }
          return await resp.json();
      } catch (err) {
          console.error("Error offline playMove:", err);
          return null;
      }
  }

  function updateScore(name, sc) {
      fetch(`${BASE_URL}/game/update_score`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, score: sc })
      })
      .then(r => {
          if (!r.ok) {
              return r.json().then(d => {
                  throw new Error(d.detail || "Erreur updateScore");
              });
          }
          return r.json();
      })
      .then(d => {
          console.log("Score mis à jour:", d);
      })
      .catch(er => {
          console.error("Erreur:", er);
      });
  }

  function blankBoard(r, c) {
      return Array.from({ length: r }, () => Array(c).fill(0));
  }

  function guessLast(data) {
      if (data.current_turn === 1) return 2;
      return 1;
  }

  function checkWin(row, col) {
      return checkDirection(row, col, 1, 0) ||
             checkDirection(row, col, 0, 1) ||
             checkDirection(row, col, 1, 1) ||
             checkDirection(row, col, 1, -1);
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

          setTimeout(() => {
              confettiPiece.remove();
          }, 3000);
      }
  }
});
