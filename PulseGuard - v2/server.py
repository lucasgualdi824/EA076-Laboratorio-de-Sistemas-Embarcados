from flask import Flask, request, jsonify

app = Flask(__name__)

dados = []  # Lista para armazenar os dados enviados pelo PulseGuard

@app.route('/add', methods=['PUT'])
def receber_dados():
    global dados
    novo_dado = request.get_json()
    dados.append(novo_dado)
    return "Dados recebidos", 200

@app.route('/', methods=['GET'])
def exibir_dados():
    return jsonify(dados)  # Retorna os dados coletados em formato JSON

if __name__ == '__main__':
    app.run(host='172.20.10.3', port=5000)
