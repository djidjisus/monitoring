# data_handler.py
import requests
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Функция для получения данных с устройства
def get_status():
    url = "http://172.22.0.55/status.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе: {e}")
        return None

# Отдельная функция для получения текущего времени
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Функция для анализа датчиков (температуры, влажности и точки росы)
def analyze_hsensor(data):
    if not data or "hsensor" not in data:
        return "Ошибка: Блок 'hsensor' не обнаружен"
    
    hsensor_data = data["hsensor"]
    values = []

    current_time = get_current_time()

    for sensor in hsensor_data:
        if "value" in sensor:
            try:
                value = float(sensor["value"])
                values.append(value)
            except ValueError:
                logging.warning(f"Некорректное значение 'value': {sensor['value']}")

    if not values:
        return f"Нет данных о значениях датчиков. Время: {current_time}"
    
    results = [f"Время: {current_time}"]  # Добавляем время
    if len(values) >= 1:  # Влажность
        humidity = values[0]
        results.append(f"Влажность: {humidity}%")

    if len(values) >= 2:  # Температура
        temperature = values[1]
        results.append(f"Температура: {temperature}°C")

    if len(values) >= 3:  # Точка росы
        dew_point = values[2]
        results.append(f"Точка росы: {dew_point}°C")

    return "\n".join(results)

# Функция для анализа напряжения по каждой фазе
def analyze_voltage(data):
    if not data or "powermetter" not in data or "voltage" not in data["powermetter"]:
        return "Ошибка: блок 'voltage' не обнаружен"
    
    voltage_data = data["powermetter"]["voltage"]
    results = []

    # Получение текущего времени
    current_time = get_current_time()
    results.append(f"Время: {current_time}")  # Добавляем время

    for i, phase in enumerate(voltage_data):
        phase_number = i + 1  # Номер фазы
        if "value" in phase:
            try:
                value = float(phase["value"])
                results.append(f"Фаза {phase_number}: {value} В")
            except ValueError:
                results.append(f"Фаза {phase_number}: Некорректные данные")
        else:
            results.append(f"Фаза {phase_number}: Данные отсутствуют")
    return "\n".join(results)

# Функция для анализа потребления по каждой фазе
def analyze_power_consumption(data):
    if not data or "powermetter" not in data or "powers" not in data["powermetter"]:
        return "Ошибка: блок 'powers' не обнаружен"
    
    powers = data["powermetter"]["powers"]
    results = []

    # Получение текущего времени
    current_time = get_current_time()
    results.append(f"Время: {current_time}")  # Добавляем время

    for i in range(3):  # Первые три значения фазы
        phase_number = i + 1  # Номер фазы
        if i < len(powers):
            try:
                value = float(powers[i])
                results.append(f"Фаза {phase_number}: {value} кВт/ч")
            except ValueError:
                results.append(f"Фаза {phase_number}: Некорректные данные")
        else:
            results.append(f"Фаза {phase_number}: данные отсутствуют")
    return "\n".join(results)