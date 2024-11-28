# PulseGuard - Documentação do Projeto

## Visão Geral
PulseGuard é um sistema projetado para monitorar a saúde de idosos através da medição da frequência cardíaca e da detecção de movimento. Ele utiliza o sensor de pulso **MAX30102** para medir a frequência cardíaca e níveis de oxigênio no sangue, e o sensor de presença **HC-SR501** para detectar atividade. Os dados coletados são enviados para um servidor Flask para monitoramento remoto, proporcionando segurança adicional para idosos que vivem sozinhos.

## Objetivos do Projeto
- Monitorar a frequência cardíaca e o nível de oxigênio no sangue dos idosos.
- Emitir alertas quando a frequência cardíaca estiver fora dos valores normais.
- Detectar a presença e o movimento do idoso, enviando notificações caso o movimento não seja detectado dentro de um período de tempo esperado.
- Fornecer uma interface web para visualização dos dados coletados em tempo real.

## Componentes Utilizados
### Hardware
- **Raspberry Pi Pico**: Microcontrolador principal.
- **Sensor MAX30102**: Sensor óptico para medição de frequência cardíaca e nível de oxigênio.
- **Sensor HC-SR501**: Sensor de presença utilizado para detectar movimento.
- **Conexão Wi-Fi**: Utilizada para enviar os dados coletados para o servidor Flask.

### Bibliotecas Python Utilizadas
- **Flask**: Para configurar um servidor web que recebe e exibe os dados.
- **urequests**: Para enviar requisições HTTP ao servidor Flask.
- **machine**: Para configurar os pinos GPIO e o I2C.
- **utime**: Para manipulação de temporização e controle de intervalos.

## Arquitetura do Sistema

O sistema é composto de três principais subsistemas:

1. **Monitoramento da Frequência Cardíaca**
    - Utiliza o sensor MAX30102 para medir a frequência cardíaca em intervalos definidos.
    - Os dados são processados para determinar os batimentos por minuto (BPM).
    - Caso os valores de BPM estejam fora do intervalo esperado, um alerta é emitido.

2. **Detecção de Movimento**
    - Utiliza o sensor HC-SR501 para detectar se há movimento.
    - Caso nenhum movimento seja detectado dentro de um período determinado, um alerta é gerado e enviado ao servidor.

3. **Servidor Flask para Coleta de Dados**
    - O servidor Flask recebe os dados do PulseGuard via requisições HTTP PUT.
    - Os dados recebidos são armazenados em uma lista e exibidos em uma página web, facilitando o monitoramento pelos familiares ou cuidadores.

## Explicação do Código

### Conexão à Rede Wi-Fi
O código primeiro se conecta a uma rede Wi-Fi, necessária para enviar os dados ao servidor Flask. Isso é feito usando o módulo `network`:

```python
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("iPhone de Lucas", "lucas2002")
```

Há uma verificação contínua para garantir que a conexão foi estabelecida antes de prosseguir com o resto do programa.

### Inicialização do Sensor MAX30102
O sensor MAX30102 é inicializado e configurado para medir a frequência cardíaca e o nível de oxigênio no sangue. O código realiza uma varredura no barramento I2C para garantir que o sensor está conectado corretamente:

```python
i2c = SoftI2C(sda=Pin(16), scl=Pin(17), freq=400000)
sensor = MAX30102(i2c=i2c)
```

Se o sensor for detectado, ele é configurado para começar as medições.

### Inicialização do Sensor de Presença HC-SR501
O sensor de presença **HC-SR501** é conectado ao pino GPIO 20 configurado como entrada:

```python
sensor_presenca_pin = Pin(20, Pin.IN)
```

Este sensor detecta movimento no ambiente, o que é essencial para verificar a atividade do idoso.

### Monitoramento da Frequência Cardíaca
Os dados do sensor MAX30102 são verificados continuamente. Quando há novas leituras disponíveis, elas são processadas e adicionadas a um monitor de frequência cardíaca (`HeartRateMonitor`). Este monitor utiliza uma janela deslizante para suavizar o sinal e detectar picos, calculando a frequência cardíaca em BPM:

```python
if sensor.available():
    ir_reading = sensor.pop_ir_from_storage()
    hr_monitor.add_sample(ir_reading)
```

Após um intervalo de 15 segundos, o BPM médio é calculado e enviado ao servidor Flask.

### Envio dos Dados ao Servidor Flask
Os dados coletados, incluindo BPM e nível de oxigênio, são enviados ao servidor Flask para armazenamento e visualização:

```python
dados_para_enviar = {
    "batimentos": media_bpm,
    "oximetria": 95.0,
    "status": "Normal" if 50 <= media_bpm <= 100 else "Alerta"
}
resposta = urequests.put(url, json=dados_para_enviar)
```

### Detecção de Presença e Envio de Alertas
Caso o sensor HC-SR501 detecte movimento, um alerta de presença é enviado ao servidor Flask. Isso é útil para garantir que o idoso está ativo e respondendo ao sistema:

```python
if sensor_presenca_pin.value():
    dados_presenca = {
        "evento": "Movimento detectado",
        "status": "Alerta"
    }
    resposta = urequests.put(url, json=dados_presenca)
```

### Interface Web com Flask
O servidor Flask recebe os dados enviados e os exibe em formato de tabela para fácil visualização dos cuidadores. A página HTML básica é renderizada utilizando `render_template_string`:

```python
@app.route('/', methods=['GET'])
def exibir_dados():
    # Template HTML para exibir os dados em tabela
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dados Recebidos</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
                text-align: center;
            }
            td {
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h2>Dados Recebidos do PulseGuard</h2>
        <table>
            <thead>
                <tr>
                    <th>Batimentos (BPM)</th>
                    <th>Oximetria</th>
                    <th>Status</th>
                    <th>Evento</th>
                </tr>
            </thead>
            <tbody>
                {% for dado in dados %}
                <tr>
                    <td>{{ dado.get('batimentos', 'N/A') }}</td>
                    <td>{{ dado.get('oximetria', 'N/A') }}</td>
                    <td>{{ dado.get('status', 'N/A') }}</td>
                    <td>{{ dado.get('evento', 'N/A') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, dados=dados)
```

## Como Executar o Projeto
1. **Configuração do Ambiente**: Conecte os sensores MAX30102 e HC-SR501 ao microcontrolador (Raspberry Pi Pico).
2. **Rede Wi-Fi**: Configure o código para se conectar à rede Wi-Fi local, alterando o SSID e a senha.
3. **Servidor Flask**: Execute o servidor Flask no computador ou em um servidor remoto que tenha acesso à rede.
4. **Execução do Código**: Carregue o código no Raspberry Pi Pico e inicie a execução para começar a monitorar os sinais vitais e a presença do idoso.

## Melhoria Futuras
- **Notificações por SMS**: Enviar notificações automáticas para cuidadores ou familiares quando ocorrerem alertas críticos.
- **Armazenamento em Nuvem**: Integrar o armazenamento dos dados coletados em um banco de dados na nuvem, para histórico de longo prazo e acesso remoto.
- **Detecção de Queda**: Adicionar um sensor de queda para melhorar a segurança e fornecer alertas adicionais em casos de emergência.

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir **Issues** e **Pull Requests** para melhorias e correções. Por favor, siga as diretrizes de contribuição descritas no arquivo `CONTRIBUTING.md`.

## Licença
Este projeto está licenciado sob a Licença MIT. Consulte o arquivo `LICENSE` para obter mais informações.

---
Esta documentação descreve detalhadamente o funcionamento do PulseGuard, facilitando a manutenção e o desenvolvimento futuro. Se você tiver dúvidas ou sugestões de melhorias, contribua através do repositório no GitHub!
