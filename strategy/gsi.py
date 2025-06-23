from flask import Flask, request
import json

app = Flask(__name__)

def parse_gsi_data(data):
    """解析GSI数据并返回关键信息"""
    # print(data)
    try:
        phrase = data['map']['phase']
        round = data['map']['round']
        if_have_c4 = 'c4' in str(data['player']['weapons'])
        money  = data['player']['state']['money']
        print(phrase, round, if_have_c4, money)
        # 基本信息
        game_info = {
            'game': data['provider']['name'],
            'steam_id': data['provider']['steamid'],
            'version': data['provider']['version']

        }
        
        # 地图信息
        map_info = {
            'map': data['map']['name'],
            'mode': data['map']['mode'],
            'phase': data['map']['phase'],
            'round': data['map']['round']
        }
        
        # 玩家信息
        player = data['player']
        player_info = {
            'name': player['name'],
            'team': player['team'],
            'health': player['state']['health'],
            'armor': player['state']['armor'],
            'money': player['state']['money'],
            'kills': player['match_stats']['kills'],
            'deaths': player['match_stats']['deaths'],
            'assists': player['match_stats']['assists']
        }
        
        return {
            'game_info': game_info,
            'map_info': map_info,
            'player_info': player
        }
    except KeyError as e:
        return {'error': f'数据解析错误: {str(e)}'}

@app.route('/', methods=['POST'])
def gsi():
    data = request.json
    parsed_data = parse_gsi_data(data)
    with open('gsi.json', 'w') as f:
        json.dump(parsed_data, f)
    return '', 200

if __name__ == '__main__':
    app.run(port=3000)
