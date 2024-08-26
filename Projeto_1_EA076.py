from machine import Pin, SoftI2C, ADC, PWM
import neopixel
import time
import random
from ssd1306 import SSD1306_I2C

# Configuração do OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Configuração da matriz de NeoPixels
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

# Configuração do joystick
joystick_x = ADC(Pin(27))
joystick_y = ADC(Pin(26))
button_sw = Pin(22, Pin.IN, Pin.PULL_UP)

# Configuração dos botões A e B
button_a = Pin(5, Pin.IN, Pin.PULL_UP)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Configuração dos LEDs da matriz
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Configuração do buzzer
buzzer = PWM(Pin(21))

# Direções possíveis
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']

# Lista para armazenar os melhores placares
leaderboard = []

# Função para ajustar a intensidade da cor
def adjust_brightness(color, intensity):
    return (int(color[0] * intensity), int(color[1] * intensity), int(color[2] * intensity))

# Função para acender uma seta na matriz
def display_arrow(direction, color):
    np.fill((0, 0, 0))  # Apaga todos os LEDs
    if direction == 'UP':
        np[LED_MATRIX[1][2]] = color
        np[LED_MATRIX[2][0]] = color
        np[LED_MATRIX[2][1]] = color
        np[LED_MATRIX[2][2]] = color
        np[LED_MATRIX[2][3]] = color
        np[LED_MATRIX[2][4]] = color
        np[LED_MATRIX[0][2]] = color
        np[LED_MATRIX[1][1]] = color
        np[LED_MATRIX[1][3]] = color
    elif direction == 'DOWN':
        np[LED_MATRIX[3][2]] = color
        np[LED_MATRIX[2][0]] = color
        np[LED_MATRIX[2][1]] = color
        np[LED_MATRIX[2][2]] = color
        np[LED_MATRIX[2][3]] = color
        np[LED_MATRIX[2][4]] = color
        np[LED_MATRIX[4][2]] = color
        np[LED_MATRIX[3][1]] = color
        np[LED_MATRIX[3][3]] = color
    elif direction == 'LEFT':
        np[LED_MATRIX[2][1]] = color
        np[LED_MATRIX[0][2]] = color
        np[LED_MATRIX[2][0]] = color
        np[LED_MATRIX[4][2]] = color
        np[LED_MATRIX[2][2]] = color
        np[LED_MATRIX[3][2]] = color
        np[LED_MATRIX[1][2]] = color
        np[LED_MATRIX[1][1]] = color
        np[LED_MATRIX[3][1]] = color
    elif direction == 'RIGHT':
        np[LED_MATRIX[0][2]] = color
        np[LED_MATRIX[1][2]] = color
        np[LED_MATRIX[1][3]] = color
        np[LED_MATRIX[2][2]] = color
        np[LED_MATRIX[2][3]] = color
        np[LED_MATRIX[2][4]] = color
        np[LED_MATRIX[3][2]] = color
        np[LED_MATRIX[3][3]] = color
        np[LED_MATRIX[4][2]] = color
    np.write()

# Função para desenhar um círculo azul
def display_circle(color):
    np.fill((0, 0, 0))  # Apaga todos os LEDs
    np[LED_MATRIX[1][1]] = color
    np[LED_MATRIX[1][3]] = color
    np[LED_MATRIX[3][1]] = color
    np[LED_MATRIX[3][3]] = color
    np[LED_MATRIX[0][2]] = color
    np[LED_MATRIX[4][2]] = color
    np[LED_MATRIX[2][0]] = color
    np[LED_MATRIX[2][4]] = color
    np.write()

# Função para preencher a matriz com uma cor
def fill_matrix(color):
    np.fill(color)
    np.write()

# Função para ler a direção do joystick
def read_joystick():
    x = joystick_x.read_u16()
    y = joystick_y.read_u16()
    if x < 10000:
        return 'RIGHT'  # Invertido
    elif x > 60000:
        return 'LEFT'   # Invertido
    elif y < 10000:
        return 'DOWN'   # Invertido
    elif y > 60000:
        return 'UP'     # Invertido
    return None

# Função para emitir som de erro
def error_sound():
    buzzer.freq(500)
    buzzer.duty_u16(1000)
    time.sleep(0.5)
    buzzer.duty_u16(0)

# Função para adicionar um placar ao leaderboard
def add_to_leaderboard(score):
    global leaderboard
    leaderboard.append(score)
    leaderboard = sorted(leaderboard, reverse=True)[:5]  # Mantém os 5 melhores placares

# Função para exibir o leaderboard
def display_leaderboard():
    oled.fill(0)
    oled.text('Leaderboard:', 0, 0)
    for i, score in enumerate(leaderboard):
        oled.text(f'{i + 1}. {score}', 0, 10 + i * 10)
    oled.show()
    time.sleep(5)  # Exibe por 5 segundos

# Função para exibir o menu inicial
def display_menu():
    selected_option = 0
    while True:
        oled.fill(0)
        oled.text('1. Jogo Solo', 0, 0)
        oled.text('2. Leaderboard', 0, 10)
        oled.text('3. Modo 1 v 1', 0, 20)
        oled.text('> ' + ('Jogo Solo' if selected_option == 0 else 'Leaderboard' if selected_option == 1 else 'Modo 1 v 1'), 0, 40)
        oled.show()
        
        direction = read_joystick()
        if direction == 'UP':
            selected_option = (selected_option - 1) % 3
            time.sleep(0.2)
        elif direction == 'DOWN':
            selected_option = (selected_option + 1) % 3
            time.sleep(0.2)
        elif button_sw.value() == 0:
            display_countdown()
            return selected_option

# Função para exibir o temporizador de 5 segundos
def display_countdown():
    for i in range(3, 0, -1):
        oled.fill(0)
        oled.text(f'Iniciando em: {i}', 0, 0)
        oled.show()
        time.sleep(1)

def one_vs_one_mode():
    def player_turn(player_num):
        score = 0
        start_time = time.ticks_ms()
        while time.ticks_ms() - start_time < 30000:  # 30 segundos para jogar
            if random.random() < 0.5:
                circle_color = adjust_brightness((0, 0, 255), 0.05)
                display_circle(circle_color)
                turn_start_time = time.ticks_ms()
                while time.ticks_ms() - turn_start_time < 600:
                    if button_b.value() == 0:
                        score += 1
                        oled.fill(0)
                        oled.text(f'Jogador {player_num}', 0, 0)
                        oled.text(f'Placar: {score}', 0, 10)
                        oled.show()
                        fill_matrix(adjust_brightness((0, 30, 0), 0.05))  # Verde ajustado
                        time.sleep(0.15)  # Exibe a tela verde por 0.5 segundo
                        break
                    elif button_sw.value() == 0:
                        continue
                else:
                    fill_matrix(adjust_brightness((30, 0, 0), 0.05))  # Vermelho ajustado
                    np.write()  # Exibe a tela vermelha imediatamente
                    oled.fill(0)
                    oled.text(f'Jogador {player_num} Errou!', 0, 0)
                    oled.show()
                    error_sound()
                    return score, True  # Retorna o placar e sinaliza erro
            else:
                direction = random.choice(DIRECTIONS)
                intensity = 0.05
                arrow_color = adjust_brightness((255, 255, 0), intensity)
                display_arrow(direction, arrow_color)
                turn_start_time = time.ticks_ms()
                while time.ticks_ms() - turn_start_time < 600:
                    if button_sw.value() == 0:
                        continue
                    joystick_direction = read_joystick()
                    if joystick_direction == direction:
                        score += 1
                        oled.fill(0)
                        oled.text(f'Jogador {player_num}', 0, 0)
                        oled.text(f'Placar: {score}', 0, 10)
                        oled.show()
                        fill_matrix(adjust_brightness((0, 30, 0), intensity))  # Verde ajustado
                        time.sleep(0.15)  # Exibe a tela verde por 0.5 segundo
                        break
                    elif button_sw.value() == 0:
                        fill_matrix(adjust_brightness((30, 0, 0), intensity))  # Vermelho ajustado
                        np.write()  # Exibe a tela vermelha imediatamente
                        oled.fill(0)
                        oled.text(f'Jogador {player_num} Errou!', 0, 0)
                        oled.show()
                        error_sound()
                        return score, True  # Retorna o placar e sinaliza erro
                else:
                    fill_matrix(adjust_brightness((30, 0, 0), intensity))  # Vermelho ajustado
                    np.write()  # Exibe a tela vermelha imediatamente
                    oled.fill(0)
                    oled.text(f'Jogador {player_num} Errou!', 0, 0)
                    oled.show()
                    error_sound()
                    return score, True  # Retorna o placar e sinaliza erro
        return score, False  # Retorna o placar sem erro

    # Turno do jogador 1
    oled.fill(0)
    oled.text('Jogador 1, pronto?', 0, 0)
    oled.text('Pressione o Joystick', 0, 20)
    oled.show()
    while button_sw.value() == 1:
        time.sleep(0.1)
    display_countdown()
    score1, erro1 = player_turn(1)

    # Se o jogador 1 errar, passa para o jogador 2
    oled.fill(0)
    oled.text('Jogador 2, pronto?', 0, 0)
    oled.text('Pressione o Joystick', 0, 20)
    oled.show()
    while button_sw.value() == 1:
        time.sleep(0.1)
    display_countdown()
    score2, erro2 = player_turn(2)
    
    # Exibir resultado final
    oled.fill(0)
    if score1 > score2:
        oled.text(f'Parabens,', 0, 0)
        oled.text(f'Jogador 1 Ganhou!', 0, 10)
    elif score2 > score1:
        oled.text(f'Parabens,', 0, 0)
        oled.text(f'Jogador 2 Ganhou!', 0, 10)
    else:
        oled.text(f'Empate!', 0, 0)
    oled.text(f'Placar 1: {score1}', 0, 30)
    oled.text(f'Placar 2: {score2}', 0, 40)
    oled.show()
    time.sleep(5)

# Função para reJogo Solo com temporizador visual
def restart_game():
    for i in range(5, 0, -1):
        oled.fill(0)
        oled.text('Pressione A para', 0, 0)
        oled.text('reJogo Solo', 0, 10)
        oled.text(f'Restante: {i}s', 0, 30)
        oled.show()
        time.sleep(1)
        if button_a.value() == 0:  # ReJogo Solo se o botão A for pressionado
            display_countdown()
            reaction_test()
            return

# Função principal do jogo
def reaction_test():
    score = 0
    difficulty = 1
    while True:
        if difficulty >= 15 and random.random() < 0.5:
            circle_color = adjust_brightness((0, 0, 255), 0.05)  # Ajuste a intensidade do azul
            display_circle(circle_color)
            start_time = time.ticks_ms()
            while time.ticks_ms() - start_time < 550:
                if button_b.value() == 0:
                    score += difficulty
                    difficulty += 1
                    oled.fill(0)
                    oled.text('Placar: ' + str(score), 0, 0)
                    oled.text('Dificuldade: ' + str(difficulty), 0, 10)
                    oled.show()
                    fill_matrix(adjust_brightness((0, 30, 0), 0.05))  # Verde ajustado
                    time.sleep(0.1)  # Exibe a tela verde por 0.5 segundo
                    break
                elif button_sw.value() == 0:
                    continue
            else:
                fill_matrix(adjust_brightness((30, 0, 0), 0.05))  # Vermelho ajustado
                np.write()  # Exibe a tela vermelha imediatamente
                oled.fill(0)
                oled.text('Seu tempo acabou!', 0, 0)
                oled.text('Placar: ' + str(score), 0, 20)
                oled.text('Dificuldade: ' + str(difficulty), 0, 30)
                oled.show()
                error_sound()
                add_to_leaderboard(score)
                return
        else:
            direction = random.choice(DIRECTIONS)
            intensity = 0.05
            arrow_color = adjust_brightness((255, 255, 0), intensity)
            display_arrow(direction, arrow_color)
            start_time = time.ticks_ms()
            while time.ticks_ms() - start_time < 550:
                if button_sw.value() == 0:
                    continue
                joystick_direction = read_joystick()
                if joystick_direction:
                    if joystick_direction == direction:
                        score += difficulty
                        difficulty += 1
                        oled.fill(0)
                        oled.text('Placar: ' + str(score), 0, 0)
                        oled.text('Dificuldade: ' + str(difficulty), 0, 10)
                        oled.show()
                        fill_matrix(adjust_brightness((0, 30, 0), intensity))  # Verde ajustado
                        time.sleep(0.1)  # Exibe a tela verde por 0.5 segundo
                        break
                    else:
                        fill_matrix(adjust_brightness((30, 0, 0), intensity))  # Vermelho ajustado
                        np.write()  # Exibe a tela vermelha imediatamente
                        oled.fill(0)
                        oled.text('Errado!', 0, 0)
                        oled.text('Placar: ' + str(score), 0, 20)
                        oled.text('Dificuldade: ' + str(difficulty), 0, 30)
                        oled.show()
                        error_sound()
                        add_to_leaderboard(score)
                        return
            else:
                fill_matrix(adjust_brightness((30, 0, 0), intensity))  # Vermelho ajustado
                np.write()  # Exibe a tela vermelha imediatamente
                oled.fill(0)
                oled.text('Seu tempo acabou!', 0, 0)
                oled.text('Placar: ' + str(score), 0, 20)
                oled.text('Dificuldade: ' + str(difficulty), 0, 30)
                oled.show()
                error_sound()
                add_to_leaderboard(score)
                return
        time.sleep(0.5)

# Loop principal para Jogo Solo ou exibir o leaderboard
while True:
    option = display_menu()
    if option == 0:
        reaction_test()
        restart_game()
    elif option == 1:
        display_leaderboard()
    elif option == 2:
        one_vs_one_mode()
