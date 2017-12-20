import json
import logging
import math
import requests
import sys
import xmltodict

logging.basicConfig(filename='dragons.log', level=logging.INFO)

get_game_url = 'http://www.dragonsofmugloar.com/api/game'
get_weather_url = 'http://www.dragonsofmugloar.com/weather/api/report/%i'
put_solution_url = 'http://www.dragonsofmugloar.com/api/game/%i/solution'

stat_map = {
    'attack': 'scaleThickness',
    'armor': 'clawSharpness',
    'agility': 'wingStrength',
    'endurance': 'fireBreath'
}


def run(game_count):
    """Main method which holds the overall flow."""
    try:
        game_count = int(game_count)
    except (ValueError):
        print('Please provide valid game count as argument: python dragons.py 3')
        return
    wins = 0

    for i in range(1, game_count + 1):
        game = get_game()
        game_id = game['gameId']
        logging.info('%i/%i: %i' % (i, game_count, game_id))
        knight = game['knight']
        weather = get_weather(game_id)
        solution = get_solution(knight, weather)
        result = solve_game(game_id, solution)
        if result['status'] == 'Victory':
            wins += 1

    logging.info('Battle success ratio: %d%%' % (wins / game_count * 100))


def get_game():
    """Get game from API."""
    game = requests.get(get_game_url).json()
    return game


def get_weather(game_id):
    """Get weather information from API."""
    response = requests.get(get_weather_url % game_id)
    weather = xmltodict.parse(response.text)['report']
    return weather


def calculate_stats(knight):
    """Calculate the stats based on knight stats."""
    stats = {}
    empty_keys = 4
    stats_left = 20

    # find the largest number
    max_key = 'attack'
    for knight_key, dragon_key in stat_map.items():
        if knight[knight_key] > knight[max_key]:
            max_key = knight_key

    logging.debug('biggest: %s' % max_key)

    # deal with the largest number
    stats[stat_map[max_key]] = min(10, knight[max_key] + 2)
    empty_keys -= 1
    stats_left -= stats[stat_map[max_key]]
    logging.debug('%s: %i' % (stat_map[max_key], stats[stat_map[max_key]]))

    # leave the smallest numbers as is
    for knight_key, dragon_key in stat_map.items():
        if knight[knight_key] <= 4:
            stats[dragon_key] = knight[knight_key]
            empty_keys -= 1
            stats_left -= stats[dragon_key]
            logging.debug('%s: %i' % (dragon_key, stats[dragon_key]))

    # check whether any empty stats still exist
    if empty_keys != 0:
        stat_per_key_left = math.floor(stats_left / empty_keys)
    logging.debug('stats_left: %i' % stats_left)
    logging.debug('empty_keys: %i' % empty_keys)

    # divide stats left equally among others
    for knight_key, dragon_key in stat_map.items():
        if dragon_key not in stats and stat_per_key_left:
            logging.debug('stat_per_key_left: %i' % stat_per_key_left)
            # prevent emptying the stats in the process with min()
            stats[dragon_key] = min(stat_per_key_left, stats_left)
            empty_keys -= 1
            stats_left -= stats[dragon_key]
            logging.debug('dividing: %s: %i' % (dragon_key, stats[dragon_key]))
            logging.debug('stats_left: %i' % stats_left)

    # give out leftovers from previous block one by one
    if stats_left > 0:
        for knight_key, dragon_key in stat_map.items():
            if stats[dragon_key] < 10 and stats_left > 0:
                stats[dragon_key] += 1
                stats_left -= 1
                logging.debug('leftover: %s: %i' % (dragon_key, stats[dragon_key]))

    scale_thickness = stats['scaleThickness']
    claw_sharpness = stats['clawSharpness']
    wing_strength = stats['wingStrength']
    fire_breath = stats['fireBreath']
    return scale_thickness, claw_sharpness, wing_strength, fire_breath


def get_solution(knight, weather):
    """Get the solution for knight and weather combination."""
    logging.info(json.dumps(knight))
    if weather['code'] == 'SRO':  # storm
        logging.info('Not sending out a dragon')
        return {}  # do not send a dragon out
    elif weather['code'] == 'HVA':  # rain
        scale_thickness = 10
        claw_sharpness = 10
        wing_strength = 0
        fire_breath = 0
    elif weather['code'] in ['T E', 'FUNDEFINEDG']:  # heat or fog
        scale_thickness = 5
        claw_sharpness = 5
        wing_strength = 5
        fire_breath = 5
    else:
        scale_thickness, claw_sharpness, wing_strength, fire_breath = calculate_stats(knight)

    solution = {
        "dragon": {
            "scaleThickness": scale_thickness,
            "clawSharpness": claw_sharpness,
            "wingStrength": wing_strength,
            "fireBreath": fire_breath
        }
    }
    logging.info(json.dumps(solution['dragon']))
    return solution


def solve_game(game_id, solution):
    """Send the solution to API."""
    result = requests.put(put_solution_url % game_id, json=solution).json()
    logging.info(result)
    return result


if __name__ == '__main__':  # pragma: no cover
    game_count = int(sys.argv[1]) if len(sys.argv) > 2 else 1
    run(game_count)
