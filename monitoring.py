import time 
import logging
from data_handler import get_status
from sms_alerts import send_sms

#
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

#Глобальное состояние системы
current_state = {
    "temperature": "normal",    # Состояние температуры
    "voltage": {},              # Состояние напряжения для каждой фазы
    "power": {}                 # Состояние потребления для каждой фазы
}

#Проверка температуры
def check_temperature = {
    alerts = []
    if "hsensor" in data: 
        try: 
            temperature = float(data["hsensor"][1]["value"])  # Температура
            if temperature > 26.5 and current_state["temperature"] == "normal":
                current_state["temperature"] = "high"
                alerts.append(f"Температура превысила порог: {temperature}°C")
            elif temperature <= 26.5 and current_state["temperature"] == "high":
                current_state["temperature"] = "normal"
                alerts.append(f"Температура вернулась в норму: {temperature}°C")
        except (IndexError, ValueError, KeyError):
            logging.warning("Ошибка при обработке данных температуры")
    return alerts
}


# Проверка напряжения
def check_voltage(data):
    alerts = []
    if "powermetter" in data and "voltage" in data["powermetter"]:
        for i, phase in enumerate(data["powermetter"]["voltage"]):
            key = f"voltage_phase_{i + 1}"
            try:
                voltage = float(phase["value"])
                if voltage < 200 and current_state.get(key, "normal") == "normal":
                    current_state[key] = "low"
                    alerts.append(f"Низкое напряжение на фазе {i + 1}: {voltage} В")
                elif voltage >= 200 and current_state.get(key, "normal") == "low":
                    current_state[key] = "normal"
                    alerts.append(f"Напряжение на фазе {i + 1} вернулось в норму: {voltage} В")
            except (ValueError, KeyError):
                logging.warning(f"Ошибка при обработке данных напряжения фазы {i + 1}")
    return alerts


# Проверка потребления
def check_power_consumption(data):
    alerts = []
    if "powermetter" in data and "powers" in data["powermetter"]:
        for i, power in enumerate(data["powermetter"]["powers"][:3]):
            key = f"power_phase_{i + 1}"
            try:
                power_value = float(power)
                if power_value > 3.5 and current_state.get(key, "normal") == "normal":
                    current_state[key] = "high"
                    alerts.append(f"Высокое потребление на фазе {i + 1}: {power_value} кВт/ч")
                elif power_value <= 3.5 and current_state.get(key, "normal") == "high":
                    current_state[key] = "normal"
                    alerts.append(f"Потребление на фазе {i + 1} вернулось в норму: {power_value} кВт/ч")
            except (ValueError, IndexError):
                logging.warning(f"Ошибка при обработке данных потребления фазы {i + 1}")
    return alerts

# Основная функция мониторинга
def monitor():
    logging.info("Запуск мониторинга...")
    phone_numbers = ["+79991234567"]  # Список номеров для отправки SMS

    while True:
        try:
            # Получаем данные через API
            status = get_status()
            if not status:
                logging.error("Не удалось получить данные.")
                time.sleep(300)  # Ждём перед следующей попыткой
                continue

            # Проверяем данные
            alerts = []
            alerts.extend(check_temperature(status))
            alerts.extend(check_voltage(status))
            alerts.extend(check_power_consumption(status))

            if alerts:
                for alert in alerts:
                    logging.info(f"Обнаружен алерт: {alert}")
                    # Отправляем SMS всем номерам
                    for phone_number in phone_numbers:
                        send_sms(phone_number, alert)

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")

        # Ждём перед следующей проверкой (5 минут)
        time.sleep(300)

if __name__ == "__main__":
    monitor()
