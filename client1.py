import socket
import json

HOST = '127.0.0.1'  # IP-адрес сервера
PORT = 8888  # порт сервера

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Подключение к серверу {HOST}:{PORT} успешно!")

client_socket.send('1'.encode('utf-8')) 

def send_command_to_server(command):
    client_socket.sendall(command.encode())
    json_data = b""
    while True:
        chunk = client_socket.recv(1024)
        if not chunk:
            break
        json_data += chunk
    programs_info = json.loads(json_data)

    # Выводим содержимое JSON с отступами для красивого форматирования
    print("Содержимое JSON:")
    print(json.dumps(programs_info, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    print('Для выхода: "exit"\nДля обновления: "update"')
    while True:
        command = input('> ')
        if command == 'update':
            # Отправляем команду "update" серверу для обновления информации о программах
            send_command_to_server("update")
        elif command == 'exit':
            break