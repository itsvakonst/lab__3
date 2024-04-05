import os
import socket
import struct
import time
import json

HOST = '127.0.0.1'  # IP-адрес сервера
PORT = 8888  # порт сервера

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Подключение к серверу {HOST}:{PORT} успешно!")

client_socket.send('3'.encode('utf-8')) 
def pack_data(data):
    """
    Упаковывает данные перед отправкой через сокет.
    """
    packed_data = json.dumps(data).encode()
    return packed_data

def send_changes(sock, folder):
    """
    Отправляет изменения в содержимом папки через сокет.
    """
    files1 = get_directory_structure(folder)
    packed_data = pack_data(files1)
    sock.sendall(packed_data)

def receive_changes(sock):
    """
    Получает изменения в содержимом папки через сокет.
    """
    data = sock.recv(1024)  # предполагаем, что не более 1024 байт
    if data:
        file_data = json.loads(data.decode())
        print(f"Received {len(file_data)} files with sizes: {file_data}")
        # Далее можно добавить логику применения изменений к папке

def send_command_to_server(command, folder, sock):
    """
    Отправляет команду на сервер и получает ответ.
    command (str): Команда для отправки на сервер.
    folder (str): Путь к папке для синхронизации.
    sock (socket.socket): Сокетное соединение с сервером.
    """
    # Отправляем команду на сервер
    sock.sendall(command.encode())

    # Получаем ответ от сервера
    data = sock.recv(1024)  # предполагаем, что не более 1024 байт

    # Если получены данные
    if data:
        # Декодируем JSON
        file_data = json.loads(data.decode())
        print(f"Received {len(file_data)} files with sizes: {file_data}")
        # Далее можно добавить логику применения изменений к папке

    # Отправляем содержимое папки на сервер
    send_changes(sock, folder)

def get_directory_structure(folder):
    """
    Получает структуру папки, возвращает список файлов и их размеры.
    """
    files = []
    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            filesize = os.path.getsize(filepath)
            files.append((filename, filesize))
    return files

if __name__ == "__main__":
    folder1 = input("Введите путь к первой папке: ")
    folder2 = input("Введите путь ко второй папке: ")

    # Установить сокетное соединение с сервером
    server_address = (HOST,PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connected = False
    while not connected:
        try:
            sock.connect(server_address)
            connected = True
        except ConnectionRefusedError:
            print("Не удалось установить соединение. Повторная попытка через 10 секунд...")
            time.sleep(10)

    while True:
        # Отправить команду на сервер и данные о папке
        send_command_to_server("update", folder1, sock)
        # Получить изменения от сервера
        receive_changes(sock)
        # Дополнительно можно добавить логику ожидания или цикла проверки каждые n секунд
        time.sleep(5)