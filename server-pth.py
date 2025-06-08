import socket
import threading
import sys
import signal
import logging
import os

# Файл, где сохраняются сведения о подключениях
CLIENT_LOG = 'clients.log'

# Конфигурация логгера
logging.basicConfig(
    filename='activity.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

# Глобальные состояния
is_running = True
is_paused = False
connections = []

def handle_connection(client_socket, client_address):
    """
    Обработка взаимодействия с одним клиентом.
    """
    logging.info(f"Новое соединение от {client_address}")
    with open(CLIENT_LOG, 'a') as f:
        f.write(f"Подключение: {client_address}\n")

    try:
        while True:
            payload = client_socket.recv(1024)
            if not payload:
                break
            message = payload.decode()
            logging.info(f"Получено от {client_address}: {message}")
            client_socket.send(payload)
    except ConnectionResetError:
        logging.warning(f"Оборвано соединение с {client_address}")
    finally:
        client_socket.close()
        logging.info(f"Клиент {client_address} отключён")

def accept_connections(server_socket):
    """
    Фоновый цикл приёма новых подключений.
    """
    global is_running, is_paused

    while is_running:
        if is_paused:
            threading.Event().wait(1)
            continue
        try:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_connection, args=(conn, addr))
            thread.start()
            connections.append(thread)
        except socket.timeout:
            continue
        except OSError:
            break

def run_server():
    global is_running, is_paused

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 9090))
    sock.listen()
    sock.settimeout(1)

    print("🟢 Сервер активен и ждёт подключения...")
    logging.info("Сервер запущен.")

    acceptor = threading.Thread(target=accept_connections, args=(sock,))
    acceptor.start()

    try:
        while True:
            cmd = input("💡 Команда (stop | pause | resume | logs | clear logs | clear clients): ").strip().lower()

            if cmd == "stop":
                print("⛔ Остановка сервера...")
                logging.info("Получена команда остановки.")
                is_running = False
                is_paused = False
                sock.close()
                break
            elif cmd == "pause":
                if not is_paused:
                    is_paused = True
                    print("⏸️ Приём подключений приостановлен.")
                    logging.info("Сервер поставлен на паузу.")
                else:
                    print("ℹ️ Сервер уже на паузе.")
            elif cmd == "resume":
                if is_paused:
                    is_paused = False
                    print("▶️ Сервер возобновил приём.")
                    logging.info("Сервер возобновил работу.")
                else:
                    print("ℹ️ Сервер уже работает.")
            elif cmd == "logs":
                if os.path.exists('activity.log'):
                    with open('activity.log', 'r') as log:
                        print("\n📄 Журнал активности:\n")
                        print(log.read())
                else:
                    print("⚠️ Лог-файл не найден.")
            elif cmd == "clear logs":
                open('activity.log', 'w').close()
                print("🧹 Логи очищены.")
                logging.info("Лог-файл очищен вручную.")
            elif cmd == "clear clients":
                open(CLIENT_LOG, 'w').close()
                print("🧾 Список клиентов очищен.")
                logging.info("Список клиентов очищен.")
            else:
                print("❓ Неизвестная команда.")
    except KeyboardInterrupt:
        print("\n⛔ Сервер завершает работу (Ctrl+C).")
        logging.info("Прервано вручную.")
        is_running = False
        is_paused = False
        sock.close()

    acceptor.join()
    for t in connections:
        t.join()

    print("🔚 Сервер выключен.")
    logging.info("Сервер выключен.")

if __name__ == "__main__":
    run_server()
