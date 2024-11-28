# PulseGuard - Documentação do Projeto

## Visão Geral
O PulseGuard é um sistema projetado para monitorar a saúde de idosos através da medição da frequência cardíaca e da detecção de movimento. Ele utiliza o sensor de pulso **MAX30102** para medir a frequência cardíaca e níveis de oxigênio no sangue, e o sensor de presença **HC-SR501** para detectar atividade. Os dados coletados são enviados para um servidor Flask para monitoramento remoto, proporcionando segurança adicional para idosos que vivem sozinhos e atuando como uma "prova de vida".

Este projeto foi desenvolvido por dois estudantes de engenharia elétrica da Universidade Estadual de Campinas (UNICAMP), com o objetivo de criar um monitor de frequência cardíaca e oximetria de fácil acesso e alta precisão. O PulseGuard utiliza tecnologias modernas e componentes acessíveis para proporcionar uma ferramenta eficaz na vigilância da saúde cardiovascular em tempo real.

## Motivação do Projeto
A notícia publicada pela Exame ("Japão registra 40 mil pessoas mortas sozinhas em casa — 10% delas descobertas um mês após a morte", em 30 de agosto de 2024) destaca a alarmante tendência de indivíduos, especialmente idosos, a falecerem sozinhos em suas residências no Japão. Esse fenômeno, conhecido como "kodokushi", reflete desafios sociais significativos, como o isolamento, a falta de suporte familiar e a escassez de serviços de monitoramento de saúde acessíveis.

No Brasil, enfrentamos uma realidade semelhante devido ao rápido envelhecimento da população. Segundo dados do Instituto Brasileiro de Geografia e Estatística (IBGE), a população idosa no país está em constante crescimento, representando uma parcela cada vez maior da sociedade. Em 2020, havia aproximadamente 29 milhões de idosos no Brasil, e essa tendência deve continuar nas próximas décadas, aumentando a demanda por serviços de saúde, apoio social e tecnologias que promovam a qualidade de vida e a autonomia dessa parcela da população (IBGE, 2021).

Inspirados por esses desafios, decidimos desenvolver o PulseGuard para oferecer uma solução tecnológica que monitora a saúde cardiovascular de forma contínua e eficiente. Nosso objetivo é criar uma ferramenta que não apenas auxilia na vigilância da saúde, mas também contribui para a prevenção de situações de risco, promovendo a segurança e o bem-estar dos usuários.

## Objetivos do Projeto
- **Monitoramento em Tempo Real**: Capturar e exibir dados contínuos de batimentos cardíacos e níveis de oximetria.
- **Alertas Automatizados**: Emitir alertas visuais e sonoros quando os valores medidos estiverem fora dos parâmetros normais.
- **Interface Intuitiva**: Disponibilizar uma interface web para visualização e armazenamento dos dados coletados.
- **Acessibilidade e Facilidade de Uso**: Desenvolver um sistema que possa ser utilizado por pessoas sem conhecimentos técnicos avançados.

## Componentes Utilizados
### Hardware
- **BitDogLab (Raspberry Pi Pico)**: Microcontrolador principal, responsável pelo processamento dos dados e comunicação com os demais componentes.
- **Sensor MAX30102**: Sensor óptico para medição de frequência cardíaca e nível de oxigênio no sangue.
- **Sensor HC-SR501**: Sensor de presença utilizado para detectar movimento.
- **Conexão Wi-Fi**: Utilizada para enviar os dados coletados para o servidor Flask.

### Bibliotecas Python Utilizadas
- **Flask**: Para configurar um servidor web que recebe e exibe os dados.
- **urequests**: Para enviar requisições HTTP ao servidor Flask.
- **machine**: Para configurar os pinos GPIO e o I2C.
- **utime**: Para manipulação de temporização e controle de intervalos.
- **max30102.py**: Drivers para o sensor MAX30102.

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

## Esquema de Conexões (Hardware)

Para montar o PulseGuard, foram realizadas as seguintes conexões entre a BitDogLab e os componentes periféricos:

- **MAX30102**:
  - **VCC** -> 3V3
  - **GND** -> GND
  - **SDA** -> GPIO16
  - **SCL** -> GPIO17

- **HC-SR501**:
  - **VCC** -> 5V
  - **GND** -> GND
  - **OUT** -> GPIO 20

## Shield para Conexão dos Sensores
A conexão dos sensores **MAX30102** e **HC-SR501** à BitDogLab foi realizada através de um **shield** projetado especificamente para comportar ambos os sensores. Este shield facilita a montagem e manutenção do sistema, garantindo conexões seguras e organizadas. Além disso, o shield utiliza um **cabo flat IDC** de 14 pinos, que permite uma conexão rápida e eficiente entre o microcontrolador e os sensores. Essa abordagem torna o sistema mais modular e fácil de ser reproduzido, além de reduzir a quantidade de fios soltos e minimizar o risco de falhas de conexão.

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
O sensor de presença **HC-SR501** é conectado a um pino GPIO configurado como entrada:

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
1. **Configuração do Ambiente**: Conecte os sensores MAX30102 e HC-SR501 ao microcontrolador (BitDogLab).
2. **Rede Wi-Fi**: Configure o código para se conectar à rede Wi-Fi local, alterando o SSID e a senha.
3. **Servidor Flask**: Execute o servidor Flask no computador ou em um servidor remoto que tenha acesso à rede.
4. **Execução do Código**: Carregue o código no Raspberry Pi Pico e inicie a execução para começar a monitorar os sinais vitais e a presença do idoso.

## Sobre o Desenvolvimento
Os códigos apresentados neste projeto foram desenvolvidos principalmente com base em referências existentes para a configuração e utilização dos sensores mencionados, além de contar com contribuições da ferramenta de inteligência artificial ChatGPT no processo iterativo de correção de erros, especialmente na configuração do Servidor Flask.

Durante o desenvolvimento do PulseGuard, a principal dificuldade encontrada foi a configuração do sensor de frequência cardíaca e oximetria MAX30102. O modelo inicialmente adquirido apresentou limitações significativas, tanto na consistência do funcionamento quanto na precisão das medições. Após a aquisição de um novo e diferente modelo, a configuração tornou-se mais fácil e intuitiva, resultando em um aumento substancial na precisão das leituras de batimentos cardíacos. No entanto, a troca do sensor exigiria adaptações na conexão ao shield projetado que não puderam ser realizadas em tempo hábil, devido à mudança na localização física dos pinos conectores, tornando necessário o uso de jumpers.

Como as medições foram realizadas utilizando conexões I2C via GPIO, o uso de jumpers longos introduziu desafios adicionais, como interferências e ruídos elétricos, uma vez que os jumpers podem atuar como antenas e captar ruídos do ambiente. Além disso, o comprimento maior dos fios aumentou a indutância e a capacitância parasitas, degradando a qualidade dos sinais de clock (SCL) e dados (SDA), o que resultou em eventuais leituras incorretas e comprometeu a precisão das medições.

## Melhorias Futuras
- **Notificações por SMS**: Enviar notificações automáticas para cuidadores ou familiares quando ocorrerem alertas críticos.
- **Armazenamento em Nuvem**: Integrar o armazenamento dos dados coletados em um banco de dados na nuvem, para histórico de longo prazo e acesso remoto.
- **Detecção de Queda**: Adicionar um sensor de queda para melhorar a segurança e fornecer alertas adicionais em casos de emergência.
- **Integração com Modelo Preditivo de IA**: Implementação de um modelo preditivo baseado em aprendizado de máquina para analisar as tendências nas medições de frequência cardíaca e oximetria ao longo do tempo. Esse modelo poderia identificar padrões normais para cada indivíduo e detectar anomalias ou desvios significativos em relação às medições rotineiras. Ao detectar tais desvios, o sistema seria capaz de emitir alertas preventivos, informando cuidadores e familiares sobre possíveis problemas de saúde antes que se tornem críticos. 
