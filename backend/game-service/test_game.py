from unittest.mock import patch, MagicMock
from app.routers.game import create_game
from app.model_game import Game


def test_create_game_ok():
    mock_game = MagicMock(spec=Game)
    mock_game.id = 1
    mock_game.status = None
    game = create_game(mock_game)
    assert game.status == "active"