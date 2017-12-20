import requests

from dragons import get_game_url
from dragons import get_solution
from dragons import run


def test_run_with_wrong_input():
    """Test main method."""
    run("s")


def test_run_normal_weather(monkeypatch):
    """Test main method."""
    monkeypatch.setattr(requests, 'get', mock_get_response)
    monkeypatch.setattr(requests, 'put', mock_put_solution)
    run(1)


def test_weather_handling(monkeypatch):
    """Test weather handling."""
    knight = {}
    weather = {'code': 'SRO'}
    solution = get_solution(knight, weather)
    assert solution == {}

    weather = {'code': 'HVA'}
    solution = get_solution(knight, weather)
    assert solution == {
        'dragon': {
            'clawSharpness': 10,
            'fireBreath': 0,
            'scaleThickness': 10,
            'wingStrength': 0
        }
    }

    weather = {'code': 'T E'}
    solution = get_solution(knight, weather)
    assert solution == {
        'dragon': {
            'clawSharpness': 5,
            'fireBreath': 5,
            'scaleThickness': 5,
            'wingStrength': 5
        }
    }


def mock_get_response(url):
    """Mock requests.get response based on url."""
    if url == get_game_url:
        return mock_get_game()
    else:
        return mock_get_weather()


def mock_get_game():
    """Mock get game API."""
    json = {
        'gameId': 1,
        'knight': {
            'name': 'Knight Rider',
            'attack': 4,
            'armor': 7,
            'agility': 5,
            'endurance': 5
        }
    }
    return MockResponse(json_data=json)


def mock_get_weather():
    """Mock get weather API."""
    text = """<?xml version="1.0" encoding="UTF-8"?><report><code>NMR</code></report>"""
    return MockResponse(text=text)


def mock_put_solution(url, json):
    """Mock put soluton API."""
    json = {
        'status': 'Victory'
    }
    return MockResponse(json_data=json)


class MockResponse:
    """Mock responses with this class."""

    def __init__(self, json_data=None, text=None):
        """Construct method."""
        self.json_data = json_data
        self.text = text

    def json(self):
        """Return json."""
        return self.json_data
