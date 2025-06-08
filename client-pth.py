import socket  # Библиотека для работы с сетевыми соединениями

def run_client():
    # Настройка подключения к серверу
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = 'localhost'
    server_port = 9090
    server = (server_host, server_port)

    try:
        client.connect(server)
        print(f"🟢 Подключение к {server_host}:{server_port} прошло успешно.")
    except ConnectionRefusedError:
        print("🔴 Сервер не отвечает. Проверьте, запущен ли он.")
        return
    except socket.error as err:
        print(f"⚠️ Ошибка при подключении: {err}")
        return

    try:
        while True:
            user_message = input("👉 Введите сообщение ('exit' для выхода): ")

            if user_message.strip().lower() == "exit":
                print("🚪 Завершение сессии.")
                break

            try:
                client.sendall(user_message.encode("utf-8"))
            except (BrokenPipeError, socket.error) as send_err:
                print(f"📡 Ошибка отправки: {send_err}")
                break

            try:
                response = client.recv(1024)
                if not response:
                    print("📴 Сервер закрыл соединение.")
                    break
                print("🗨 Ответ сервера:", response.decode("utf-8"))
            except socket.error as recv_err:
                print(f"❌ Ошибка получения данных: {recv_err}")
                break

    finally:
        client.close()
        print("🔒 Соединение закрыто.")

if __name__ == "__main__":
    run_client()
