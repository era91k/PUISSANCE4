from fastapi import HTTPException
import pytest
from unittest.mock import patch, MagicMock
from app.model_player import Player
from app.routers.game import *
from app.model_game import Game

def test_drop_piece_ok():
    board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0]
    ]
    column = 3
    player_id = 1
    row_index = drop_piece(board, column, player_id)

    assert row_index == 2

def test_drop_piece_full_column():
    board = [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0]
    ]
    column = 3
    player_id = 1
    row_index = drop_piece(board, column, player_id)

    assert row_index == -1


def test_create_game_ok():
    mock_game = MagicMock(spec=Game)
    mock_game.id = 1
    mock_game.status = None
    game = create_game(mock_game)

    assert game.status == "active"

def test_play_move_invalid_column():
    mock_game = MagicMock(spec=Game)
    mock_game.id = 1
    column = -1
    player_id = 456

    with pytest.raises(HTTPException) as exc_info:
        play_move(mock_game.id, column, player_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid column"


@patch("app.routers.game.drop_piece")
def test_play_move_column_full(mock_drop_piece):
    mock_drop_piece.return_value = -1
    game = Game(
        id=2,
        players=[Player(id=1, name="Alice"), Player(id=2, name="Bob")],
        current_turn=1,
        board=[
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ],
    )
    game = create_game(game)

    with pytest.raises(HTTPException) as exc_info:
        play_move(game.id, 3, 1)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Column is full"


@patch("app.routers.game.drop_piece")
@patch("app.routers.game.check_winner")
def test_play_move_win(mock_check_winner, mock_drop_piece):
    mock_check_winner.return_value = True
    mock_drop_piece.return_value = 2
    game = Game(
        id=3,
        players=[Player(id=1, name="Alice"), Player(id=2, name="Bob")],
        current_turn=1,
        board=[
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ],
    )
    game = create_game(game)
    result = play_move(game.id, 3, 1)

    assert result["status"] == "won"


@patch("app.routers.game.drop_piece")
@patch("app.routers.game.check_winner")
def test_play_move_draw(mock_check_winner, mock_drop_piece):
    mock_drop_piece.return_value = 0
    mock_check_winner.return_value = False
    game = Game(
        id=4,
        players=[Player(id=1, name="Alice"), Player(id=2, name="Bob")],
        current_turn=1,
        board = [
            [1, 2, 1, 1, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
        ],
    )
    game = create_game(game)
    result = play_move(game.id, 3, 1)

    assert result["status"] == "draw"


@patch("app.routers.game.drop_piece")
@patch("app.routers.game.check_winner")
def test_play_move_draw(mock_check_winner, mock_drop_piece):
    mock_drop_piece.return_value = 0
    mock_check_winner.return_value = False
    game = Game(
        id=4,
        players=[Player(id=1, name="Alice"), Player(id=2, name="Bob")],
        current_turn=1,
        board = [
            [1, 2, 1, 0, 1, 2, 1],
            [2, 1, 0, 1, 2, 1, 2],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
            [1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2],
        ],
    )
    game = create_game(game)
    result = play_move(game.id, 3, 1)

    assert result["status"] == "active"


def test_play_move_game_not_found():
    with pytest.raises(HTTPException) as exc_info:
        play_move(123, 3, 1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"


@patch("app.routers.game.online_games", new_callable=dict)
def test_create_online_game(mock_online_games):
    result = create_online_game(playerName="Alice", gameCode="GAME123")

    assert result == {"message": "Online game created successfully."}
    assert "GAME123" in mock_online_games
    assert mock_online_games["GAME123"]["player1"] == "Alice"
    assert mock_online_games["GAME123"]["status"] == "waiting"



@patch("app.routers.game.online_games", {"GAME123": {"player1": "Alice", "player2": None}})
def test_join_online_game():
    result = join_online_game(playerName="Bob", gameCode="GAME123")

    assert result["message"] == "Joined game successfully."
    assert result["game"]["player2"] == "Bob"
    assert result["game"]["status"] == "ready"

#game have already 2 players
@patch("app.routers.game.online_games", {"GAME123": {"player1": "Alice", "player2": "Bob", "status": "ready"}})
def test_join_online_game_full():
    with pytest.raises(HTTPException) as exc_info:
        join_online_game(playerName="Charlie", gameCode="GAME123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Game already has two players."


@patch("app.routers.game.online_games", {"GAME123": {"player1": "Alice", "player2": "Bob", "board": [[0]*7 for _ in range(6)], "current_turn": 1, "status": "active"}})
@patch("app.routers.game.drop_piece")
@patch("app.routers.game.check_winner")
def test_play_online_move(mock_check_winner, mock_drop_piece):
    mock_drop_piece.return_value = 5
    mock_check_winner.return_value = False

    result = play_online_move(gameCode="GAME123", column=3, player_id=1)

    assert result["message"] == "Player 1 played in column 3"
    assert result["status"] == "active"
    assert result["current_turn"] == 2


@patch("app.routers.game.online_games", {"GAME123": {"player1": "Alice", "player2": "Bob", "status": "won", "current_turn": 1}})
def test_reset_online_game():
    result = reset_online_game(gameCode="GAME123")

    assert result["message"] == "Game reset. Player 2 starts now."
    assert result["status"] == "active"
    assert result["current_turn"] == 2
    assert result["board"] == [[0]*7 for _ in range(6)]


@patch("app.routers.game.db")
@patch("app.routers.game.online_games", {"GAME123": {}})
def test_update_online_score(mock_db):
    mock_user_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_user_collection
    mock_user_collection.find_one.return_value = {"name": "Alice", "score": 10}

    result = update_online_score(gameCode="GAME123", name="Alice", score=5)

    assert result == {"name": "Alice", "new_score": 15}
    mock_user_collection.update_one.assert_called_with({"name": "Alice"}, {"$set": {"score": 15}})





