from machine import Pin
from time import sleep

# Configuração do pino para o sensor de presença
sensor_presenca = Pin(18, Pin.IN)  # Substitua 25 pelo GPIO que você conectou

print("Iniciando teste do sensor de presença HC-SR501...")

try:
    while True:
        if sensor_presenca.value():
            print("Movimento detectado!")
        else:
            print("Sem movimento.")
        
        # Pequena pausa para evitar sobrecarga
        sleep(0.5)

except KeyboardInterrupt:
    print("Teste encerrado.")
