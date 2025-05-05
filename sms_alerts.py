import gammu

def send_sms(phone_number, message):
    """
    Отправляет SMS на указанный номер телефона через GSM-модем.
    """
    try:
        # Настройка соединения с GSM-модемом
        state_machine = gammu.StateMachine()
        state_machine.ReadConfig()  # Читает конфигурацию из ~/.gammurc
        state_machine.Init()

        # Подготовка сообщения
        message_data = {
            "Text": message,
            "SMSC": {"Location": 1},
            "Number": phone_number,
        }

        # Отправка SMS
        state_machine.SendSMS(message_data)
        logging.info(f"SMS успешно отправлено на номер {phone_number}: {message}")

    except Exception as e:
        logging.error(f"Ошибка при отправке SMS: {e}")