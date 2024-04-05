import os
import time
from filecmp import dircmp
import socket
import struct
import json
import asyncio

def copy_file(src_file, dst_file):
    """
    Копирует файл из src_file в dst_file.
    """
    try:
        with open(src_file, 'rb') as src, open(dst_file, 'wb') as dst:
            dst.write(src.read())
    except IOError as e:
        print(f"Ошибка при копировании файла {src_file} в {dst_file}: {e}")

def copy_directory(src_dir, dst_dir):
    """
    Функция для копирования директории.
    """
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)
        if os.path.isdir(src_item):
            copy_directory(src_item, dst_item)
        else:
            copy_file(src_item, dst_item)

def delete_file(file_path):
    """
    Функция для удаления файла или директории.
    """
    if os.path.isdir(file_path):
        for item in os.listdir(file_path):
            delete_file(os.path.join(file_path, item))
        os.rmdir(file_path)
    else:
        os.remove(file_path)

def synchronize_folders(folder1, folder2):
    server_address = (HOST,PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        print("Ждем подключения программы 2...")
        conn, addr = sock.accept()
        print("Программа 2 подключена:", addr)

        while True:
            dcmp = dircmp(folder1, folder2)
            missing_files = dcmp.left_only
            extra_files = dcmp.right_only

            for missing_file in missing_files:
                src_file = os.path.join(folder1, missing_file)
                dst_file = os.path.join(folder2, missing_file)
                if os.path.isfile(src_file):
                    copy_file(src_file, dst_file)
                    print('Файл скопирован:', dst_file)
                elif os.path.isdir(src_file):
                    copy_directory(src_file, dst_file)
                    print('Директория скопирована:', dst_file)

            for extra_file in extra_files:
                src_file = os.path.join(folder2, extra_file)
                if os.path.isfile(src_file) or os.path.isdir(src_file):
                    delete_file(src_file)
                    print('Файл или директория удалены:', src_file)

            time.sleep(5)  # Проверка каждые 5 секунд

class Server:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    async def handle_client(self, reader, writer):
        result = None
        input_data = await reader.read(1)
        input_data = input_data.decode('utf-8')

        if input_data == "3":
            print("Программа 3")
            result = await self.receive_changes(reader)

        if result:
            writer.write(result)
            writer.close()
            await writer.wait_closed()

    async def receive_changes(self, reader):
        data = b''  # Создаем пустой байтовый объект для хранения данных

        while True:
            tmp = await reader.read(1024)  
            if tmp:  # Если получены данные
                data += tmp  # Добавляем их к уже полученным данным
            else:  # Если данные пусты
                break  # Прерываем цикл

        if data:  # Если получены данные
            file_data = json.loads(data.decode())  # Декодируем JSON
            print(f"Received {len(file_data)} files with sizes: {file_data}")  # Выводим информацию о полученных файлах
            return data  # Возвращаем полученные данные
        else:
            return None

    def start(self, is_async=True):
        asyncio.run(self._async_start())

    async def _async_start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self._host, self._port)
        addr = self.server.sockets[0].getsockname()
        print(f'Сервер запущен на {addr}')
        async with self.server:
            await self.server.serve_forever()

if __name__ == "__main__":
    HOST = '127.0.0.1'  # IP-адрес сервера
    PORT = 8888  # порт сервера
    folder1 = input("Введите путь к первой папке: ")
    folder2 = input("Введите путь ко второй папке: ")

    synchronize_folders(folder1, folder2)

    server = Server(HOST, PORT)
    server.start()