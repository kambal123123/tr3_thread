import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Показывает прогресс в консоли

# Получаем адрес сервера от пользователя
target_host = input("🔍 Введите IP или домен для проверки портов: ")

# Преобразуем доменное имя в IP-адрес
try:
    ip_address = socket.gethostbyname(target_host)
except socket.gaierror:
    print(f"❌ Не удалось определить IP для '{target_host}'. Завершение.")
    sys.exit()

# Диапазон портов для анализа
first_port = 1
last_port = 65535  # Можно ограничить, например, 1024

print(
    f"🚀 Начинаем проверку {target_host} ({ip_address}) на порты от {first_port} до {last_port}."
)


# Функция, которая проверяет доступность одного порта
def check_port(port_number):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((ip_address, port_number))
        s.close()
        return port_number if result == 0 else None
    except Exception:
        return None


active_ports = []

try:
    # Создаем пул потоков для параллельного сканирования
    with ThreadPoolExecutor(max_workers=100) as pool:
        tasks = {
            pool.submit(check_port, port): port
            for port in range(first_port, last_port + 1)
        }

        with tqdm(total=last_port - first_port + 1, desc="Проверка портов") as progress:
            for task in as_completed(tasks):
                port = tasks[task]
                try:
                    outcome = task.result()
                    if outcome:
                        active_ports.append(outcome)
                except Exception as err:
                    print(f"⚠️ Ошибка при проверке порта {port}: {err}")
                finally:
                    progress.update(1)

except KeyboardInterrupt:
    print("\n⛔️ Процесс прерван вручную.")
    sys.exit()
except socket.error as sock_err:
    print(f"📡 Ошибка сокета: {sock_err}")
    sys.exit()

# Вывод результатов
active_ports.sort()
if active_ports:
    print("\n✅ Найдены открытые порты:")
    for open_port in active_ports:
        print(f"🟢 Порт {open_port} доступен")
else:
    print("\n🔒 Нет открытых портов в заданном диапазоне.")

print("✅ Сканирование завершено.")
