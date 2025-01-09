from fastapi import HTTPException
import pytest
from unittest.mock import patch, MagicMock
from app.model_player import Player
from app.routers.game import create_game, drop_piece, get_score, play_move, update_score
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


@patch("app.routers.game.db")
def test_update_score_ok(mock_db):
    mock_user_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_user_collection
    mock_user_collection.find_one.return_value = {"name": "Alice", "score": 10}
    mock_user_collection.update_one.return_value = None

    result = update_score(name="Alice", score=5)

    assert result == {"name": "Alice", "new_score": 15}


@patch("app.routers.game.db")
def test_update_score_user_not_found(mock_db):
    mock_user_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_user_collection
    mock_user_collection.find_one.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        update_score(name="Bob", score=5)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


@patch("app.routers.game.db")
def test_get_score_ok(mock_db):
    mock_user_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_user_collection
    mock_user_collection.find_one.return_value = {"name": "Alice", "score": 15}

    result = get_score(name="Alice")

    assert result == {"name": "Alice", "score": 15}
    mock_user_collection.find_one.assert_called_with({"name": "Alice"})


@patch("app.routers.game.db")
def test_get_score_user_not_found(mock_db):
    mock_user_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_user_collection

    mock_user_collection.find_one.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_score(name="Bob")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"