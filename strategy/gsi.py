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
        return {
            'phrase': phrase,
            'round': round,
            'if_have_c4': if_have_c4,
            'money': money
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
