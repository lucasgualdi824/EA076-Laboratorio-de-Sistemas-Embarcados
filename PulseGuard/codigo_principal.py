# main.py
import network
import urequests

from machine import SoftI2C, Pin
from utime import ticks_diff, ticks_us, ticks_ms, sleep 
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM


class HeartRateMonitor:
    """A simple heart rate monitor that uses a moving window to smooth the signal and find peaks."""

    def __init__(self, sample_rate=100, window_size=10, smoothing_window=5):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.smoothing_window = smoothing_window
        self.samples = []
        self.timestamps = []
        self.filtered_samples = []

    def add_sample(self, sample):
        """Add a new sample to the monitor."""
        timestamp = ticks_ms()
        self.samples.append(sample)
        self.timestamps.append(timestamp)

        # Apply smoothing
        if len(self.samples) >= self.smoothing_window:
            smoothed_sample = (
                sum(self.samples[-self.smoothing_window:]) / self.smoothing_window
            )
            self.filtered_samples.append(smoothed_sample)
        else:
            self.filtered_samples.append(sample)

        # Maintain the size of samples and timestamps
        if len(self.samples) > self.window_size:
            self.samples.pop(0)
            self.timestamps.pop(0)
            self.filtered_samples.pop(0)

    def find_peaks(self):
        """Find peaks in the filtered samples."""
        peaks = []

        if len(self.filtered_samples) < 3:  # Need at least three samples to find a peak
            return peaks

        # Calculate dynamic threshold based on the min and max of the recent window of filtered samples
        recent_samples = self.filtered_samples[-self.window_size:]
        min_val = min(recent_samples)
        max_val = max(recent_samples)
        threshold = (
            min_val + (max_val - min_val) * 0.5
        )  # 50% between min and max as a threshold

        for i in range(1, len(self.filtered_samples) - 1):
            if (
                self.filtered_samples[i] > threshold
                and self.filtered_samples[i - 1] < self.filtered_samples[i]
                and self.filtered_samples[i] > self.filtered_samples[i + 1]
            ):
                peak_time = self.timestamps[i]
                peaks.append((peak_time, self.filtered_samples[i]))

        return peaks

    def calculate_heart_rate(self):
        """Calculate the heart rate in beats per minute (BPM)."""
        peaks = self.find_peaks()

        if len(peaks) < 2:
            return None  # Not enough peaks to calculate heart rate

        # Calculate the average interval between peaks in milliseconds
        intervals = []
        for i in range(1, len(peaks)):
            interval = ticks_diff(peaks[i][0], peaks[i - 1][0])
            intervals.append(interval)

        average_interval = sum(intervals) / len(intervals)

        # Convert intervals to heart rate in beats per minute (BPM)
        heart_rate = (
            60000 / average_interval
        )  # 60 seconds per minute * 1000 ms per second

        return heart_rate


def main():
    # Conexão Wi-Fi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("iPhone de Lucas", 'lucas2002')
    print("Conectando-se à rede Wi-Fi...")
    while not wlan.isconnected():
        sleep(1)
    print("Conectado à rede Wi-Fi:", wlan.ifconfig())

    # I2C software instance
    i2c = SoftI2C(
        sda=Pin(16),  # SDA pin
        scl=Pin(17),  # SCL pin
        freq=400000,
    )  # I2C frequency

    # Sensor instance
    sensor = MAX30102(i2c=i2c)  # An I2C instance is required

    # Scan I2C bus to ensure that the sensor is connected
    if sensor.i2c_address not in i2c.scan():
        print("Sensor não encontrado.")
        return
    elif not (sensor.check_part_id()):
        # Check that the targeted sensor is compatible
        print("ID do dispositivo I2C não corresponde ao MAX30102 ou MAX30105.")
        return
    else:
        print("Sensor conectado e reconhecido.")

    # Load the default configuration
    print("Configurando o sensor com a configuração padrão.\n")
    sensor.setup_sensor()

    # Set the sample rate to 400: 400 samples/s are collected by the sensor
    sensor_sample_rate = 400
    sensor.set_sample_rate(sensor_sample_rate)

    # Set the number of samples to be averaged per each reading
    sensor_fifo_average = 8
    sensor.set_fifo_average(sensor_fifo_average)

    # Set LED brightness to a medium value
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    # Expected acquisition rate: 400 Hz / 8 = 50 Hz
    actual_acquisition_rate = int(sensor_sample_rate / sensor_fifo_average)

    sleep(1)

    print(
        "Iniciando aquisição de dados dos registros RED & IR...",
        "Pressione Ctrl+C para parar.\n",
    )
    sleep(1)

    # Initialize the heart rate monitor
    hr_monitor = HeartRateMonitor(
        # Select a sample rate that matches the sensor's acquisition rate
        sample_rate=actual_acquisition_rate,
        # Select a significant window size to calculate the heart rate (2-5 seconds)
        window_size=int(actual_acquisition_rate * 3),
    )

    # Setup to calculate the heart rate every 15 seconds
    hr_compute_interval = 15  # segundos
    ref_time = ticks_ms()  # Reference time

    # Variáveis para acumular os valores de BPM
    bpm_acumulados = []
    numero_de_medidas = 0

    while True:
        # O método check() precisa ser continuamente sondado para verificar se há novas leituras na fila FIFO do sensor.
        sensor.check()

        # Verifica se há amostras disponíveis
        if sensor.available():
            # Acessa a fila FIFO e coleta as leituras (inteiros)
            red_reading = sensor.pop_red_from_storage()
            ir_reading = sensor.pop_ir_from_storage()

            # Adiciona a leitura IR ao monitor de frequência cardíaca
            hr_monitor.add_sample(ir_reading)

        # Calcula periodicamente a frequência cardíaca a cada hr_compute_interval segundos
        if ticks_diff(ticks_ms(), ref_time) / 1000 > hr_compute_interval:
            # Calcula a frequência cardíaca
            heart_rate = hr_monitor.calculate_heart_rate()
            if heart_rate is not None:
                print("Frequência Cardíaca: {:.0f} BPM".format(heart_rate))
                bpm_acumulados.append(heart_rate)
                numero_de_medidas += 1

                # Calcula a média dos BPMs
                media_bpm = sum(bpm_acumulados) / len(bpm_acumulados)
                print("Média de BPM nos últimos {} segundos: {:.0f} BPM".format(hr_compute_interval, media_bpm))

                # Envia os dados para o servidor
                # Destaque: Mude o endereço IP abaixo para o IP do seu servidor Flask
                server_ip = "172.20.10.3"  # Alterar para o IP do servidor
                server_port = 5000
                url = f"http://{server_ip}:{server_port}/add"

                # Prepara o JSON a ser enviado
                dados_para_enviar = {
                    "batimentos": media_bpm,
                    "oximetria": 95.0,  # Substitua pelo valor real de oximetria, se disponível
                    "status": "Normal" if 50 <= media_bpm <= 100 else "Alerta"
                }

                try:
                    resposta = urequests.put(url, json=dados_para_enviar)
                    if resposta.status_code == 200:
                        print("Dados enviados com sucesso!\n")
                    else:
                        print(f"Falha ao enviar dados: {resposta.text}\n")
                except Exception as e:
                    print(f"Erro ao conectar com o servidor: {e}\n")

                # Reseta as variáveis de acumulação
                bpm_acumulados = []
                numero_de_medidas = 0
            else:
                print("Não há dados suficientes para calcular a frequência cardíaca.\n")
            
            # Reseta o tempo de referência
            ref_time = ticks_ms()


if __name__ == "__main__":
    main()

# 172.20.10.3
