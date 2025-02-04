import numpy as np
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# Функция для генерации сигнала в один момент времени
def create_signal_single_point(time_point, num_exp, num_cos, num_log, amp_exp, amp_cos, amp_log):
    total_signal = 0
    exp_const = 1
    freq_base = 2 * np.pi
    phase_shift = 0
    log_const = 1
    k_base = 1

    # Экспоненциальные компоненты
    if num_exp > 0:
        for i in range(num_exp):
            exp_amp = amp_exp[i] if i < len(amp_exp) else 0
            total_signal += exp_amp * np.exp(-time_point / exp_const)

    # Косинусные компоненты
    if num_cos > 0:
        for j in range(num_cos):
            cos_amp = amp_cos[j] if j < len(amp_cos) else 0
            frequency = freq_base * (j + 1)
            total_signal -= cos_amp * np.cos(frequency * time_point + phase_shift)

    # Логарифиические компоненты
    if num_log > 0:
        for k in range(num_log):
            log_amp = amp_log[k] if k < len(amp_log) else 0
            k_value = k_base * (k + 1)
            log_input = max(log_const * k_value * time_point, 1e-10)
            total_signal += log_amp * np.log10(log_input)

    return total_signal


# Класс для графического интерфейса
class SignalApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Генерация и обработка сигнала")

        # Параметры для генерации сигнала
        self.num_exp = 0
        self.num_cos = 2
        self.num_log = 2
        self.amp_exp = [0]
        self.amp_cos = [0.45, 0.55]
        self.amp_log = [0.43, 0.57]

        # Параметры для расчета ЕМА
        self.N = 5
        self.alpha = 2 / (self.N + 1)
        self.EMA_prev = None

        # Массивы для хранения данных
        self.time_values = []
        self.signal_values = []
        self.ema_values = []
        self.moving_avg_values = []

        # Параметры времени
        self.sampling_interval = 0.05
        self.total_duration = 10
        self.start_time = None
        self.current_time = 0
        self.running = False

        # Создаем элементы интерфейса
        self.create_widgets()

        # Инициализация источника данных
        self.data_source = "mathematical_model"  # Возможные значения: "analog_sensor", "digital_sensor", "mathematical_model", "api"

    def create_widgets(self):
        # Кнопки управления
        control_frame = ttk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_button = ttk.Button(control_frame, text="Старт", command=self.start_signal)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_button = ttk.Button(control_frame, text="Стоп", command=self.stop_signal, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Поля для отображения текущих значений
        value_frame = ttk.Frame(self.master)
        value_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(value_frame, text="Текуцее время:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.time_label = ttk.Label(value_frame, text="0.00 с")
        self.time_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(value_frame, text="Текуций сигнал:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.signal_label = ttk.Label(value_frame, text="0.0000")
        self.signal_label.grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(value_frame, text="Текущий ЕМА:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.ema_label = ttk.Label(value_frame, text="0.0000")
        self.ema_label.grid(row=2, column=1, sticky=tk.W, padx=5)

        # График
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.line1, = self.ax.plot([], [], label='Сигнал')
        self.line2, = self.ax.plot([], [], label='EMA', linestyle='--')
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Значение')
        self.ax.set_title('Сигнал и ЕМА ')
        self.ax.legend()
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def start_signal(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.start_time = time.time()
            self.EMA_prev = None
            self.time_values.clear()
            self.signal_values.clear()
            self.ema_values.clear()
            self.moving_avg_values.clear()
            self.ax.clear()
            self.line1, = self.ax.plot([], [], label='сигнал')
            self.line2, = self.ax.plot([], [], label='EMA', linestyle='--')
            self.ax.set_xlabel('Время (с)')
            self.ax.set_ylabel('Значение')
            self.ax.set_title('Сигнал и ЕМА ')
            self.ax.legend()
            self.ax.grid(True)

            self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def stop_signal(self):
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


    def generate_signal(self):
        while self.running and self.current_time < self.total_duration:
            self.current_time = time.time() - self.start_time

            signal_value = create_signal_single_point(
                self.current_time,
                self.num_exp,
                self.num_cos,
                self.num_log,
                self.amp_exp,
                self.amp_cos,
                self.amp_log
            )

            # Расчет ЕМА
            P = signal_value
            if self.EMA_prev is None:
                EMA = P
            else:
                EMA = (P * signal_value) + ((1 - self.alpha) * P)

            self.EMA_prev = EMA

            # Сохраняем значения для построения графиков
            self.time_values.append(self.current_time)
            self.signal_values.append(signal_value)
            self.ema_values.append(self.EMA_prev)

            # Обновляем линии на графике
            self.line1.set_data(self.time_values, self.signal_values)
            self.line2.set_data(self.time_values, self.ema_values)
            self.ax.relim()
            self.ax.autoscale()
            self.canvas.draw()

            time.sleep(self.sampling_interval)

            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = SignalApp(root)
    root.mainloop()
