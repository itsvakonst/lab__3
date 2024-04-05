#!/usr/bin/python3

import socket
import asyncio
import os
import json
import datetime
import time
from filecmp import dircmp


# ----------------------------
# Для клиента 1
def get_programs_in_path(path):
    """
    Функция, получает список программ в указанной директории.
    принимает:
        path (str): путь к директории.
    возвращает:
        list: список программ.
    """
    programs = []

    # существует ли указанная директория и является ли она директорией
    if os.path.exists(path) and os.path.isdir(path):
        # получаем список файлов в директории
        files = os.listdir(path)
        # фильтруем файлы, чтобы остались только исполняемые программы
        programs = [file for file in files if
                    (file.endswith(".exe") or file.endswith(".dll"))]

    return programs


def get_programs_in_path_env():
    """
    Функция, получает информацию о директориях из переменной окружения PATH
    и список программ в каждой директории.
    возвращает: словарь с информацией о директориях и программах.
    """
    # значение переменной окружения PATH
    path_env = os.getenv("PATH")
    # делим значение на отдельные пути
    paths = path_env.split(os.pathsep)

    programs_info = {}

    # для каждого пути получаем список программ
    for path in paths:
        programs = get_programs_in_path(path)
        programs_info[path] = programs

    return programs_info


def save_programs_info_to_file(programs_info, filepath):
    """
    Функция, сохраняет информацию о программах в файл в формате JSON
        programs_info (dict): словарь с информацией о программах
        filepath (str): путь к файлу который JSON
    """
    with open(filepath, "w") as file:
        # сохраняем словарь в файл в формате JSON с отступами 4
        json.dump(programs_info, file, indent=4)


# ----------------------------
# Для клиента 2/4
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class BinaryTree:
    def __init__(self):
        self.root = None

    def get_root(self):
        return self.root

    def add(self, val):
        if not self.root:
            self.root = Node(val)
        else:
            self._add(val, self.root)

    def _add(self, val, node):
        if val < node.value:
            if node.left:
                self._add(val, node.left)
            else:
                node.left = Node(val)
        else:
            if node.right:
                self._add(val, node.right)
            else:
                node.right = Node(val)

    def tree_to_dict(self):
        return self._tree_dict(self.root)

    def _tree_dict(self, node):
        if node is None:
            return None
        else:
            return {"value": node.value,
                    "left": self._tree_dict(node.left),
                    "right": self._tree_dict(node.right)}


def save_binary_tree(tree_dicted, filename):
    with open(filename, 'a') as file:
        json.dump(tree_dicted, file)


def create_directory():
    now = datetime.datetime.now()
    folder_name = now.strftime("%d-%m-%Y_%H-%M-%S")
    os.mkdir(folder_name)
    return folder_name
# ----------------------------

# Для клиента 3
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
# ----------------------------


class Server:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    async def handle_client(self, reader, writer):
        result = None
        input_data = await reader.read(1)
        input_data = input_data.decode('utf-8')

        if input_data == "1":
            print("varya")
            result = await self.varya(reader)

        elif input_data == "2":
            print("alisa")
            result = await self.delya(reader)

        elif input_data == "3":
            print("dasha")
            result = await self.dasha(reader)

        elif input_data == "4":
            print("delya")
            result = await self.delya(reader)

        if result:
            writer.write(result)
            writer.close()
            await writer.wait_closed()

    # 1
    async def varya(self, reader):
        # Получаем команду от клиента
        command = ""
        piece = await reader.read(64)
        if piece:
            command += piece.decode()
            if command == "update":
                # Получаем информацию о программах
                programs_info = get_programs_in_path_env()
                # Сохраняем информацию в файл
                save_programs_info_to_file(programs_info, "programs_info.json")
        json_file = json.dumps(programs_info).encode('utf-8')
        return json_file
    
    #2
    async def alisa(self, reader):
        folder_name = create_directory()
        file_counter = 0
        Tree = BinaryTree()

        while True:
            data = ""
            piece = await reader.read(64)
            if piece:
                data += piece.decode()
                print(data)
                if data == 'save':
                    file_counter += 1
                    filename = f"{folder_name}/{file_counter}.json"
                    save_binary_tree(Tree.tree_to_dict(), filename)
                    print('файл сохранен')
                    break
                if "GET_FILE" in data:
                    print(data)
                    data = data[8:]
                    file_info = data.split(",")
                    folder_name = file_info[0]
                    file_number = file_info[1]
                    filename = f"{folder_name}/{file_number}.json"
                    with open(filename, 'r') as file:
                        file_data = file.read().encode('utf-8')
                    return file_data
                else:
                    number = int(data)
                    Tree.add(number)

    #3
    async def dasha(self, reader):
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

    #4
    async def delya(self, reader):
        folder_name = create_directory()
        file_counter = 0
        Tree = BinaryTree()

        while True:
            data = ""
            piece = await reader.read(64)
            if piece:
                data += piece.decode()
                print(data)
                if data == 'save':
                    file_counter += 1
                    filename = f"{folder_name}/{file_counter}.json"
                    save_binary_tree(Tree.tree_to_dict(), filename)
                    print('файл сохранен')
                    break
                if "GET_FILE" in data:
                    print(data)
                    data = data[8:]
                    file_info = data.split(",")
                    folder_name = file_info[0]
                    file_number = file_info[1]
                    filename = f"{folder_name}/{file_number}.json"
                    with open(filename, 'r') as file:
                        file_data = file.read().encode('utf-8')
                    return file_data
                else:
                    number = int(data)
                    Tree.add(number)

    def start(self, is_async=True):
        # if is_async:
        asyncio.run(self._async_start())
        # else:
        #    self._thread_start()

    async def _async_start(self):
        self.server = await asyncio.start_server(
            self.handle_client, self._host, self._port)
        addr = self.server.sockets[0].getsockname()
        print(f'Сервер запущен на {addr}')
        async with self.server:
            await self.server.serve_forever()

    def _thread_start(self):
        # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.bind((self._host, self._port))
        # server_socket.listen(1)
        # print(f"Сервер запущен и слушает на {self._host}:{self._port}")
        # try:
        # while True:
        # client_sock, address = server_socket.accept()
        # print(f"Принято соединение от {address}")
        # client_handler = threading.Thread(
        # target=handle_client,
        # args=(client_sock,)  # Передаем сокет клиента в поток
        # )
        # client_handler.start()
        # finally:
        # server_socket.close()
        pass


if __name__ == "__main__":
    HOST = '127.0.0.1'  # IP-адрес сервера
    PORT = 8888  # порт сервера
    server = Server(HOST, PORT)
    server.start()