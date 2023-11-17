import socket
import threading

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(1)
        self.clients = []

        print("Aguardando conexões...")
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client_socket, _ = self.server_socket.accept()
            print("Conexão aceita.")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Propaga a atualização para todos os clientes
                self.broadcast(data)

            except ConnectionResetError:
                print("Conexão encerrada.")
                self.clients.remove(client_socket)
                break


    def broadcast(self, data):
        for client_socket in self.clients:
            try:
                client_socket.send(data)
            except Exception as e:
                print("Erro ao enviar mensagem:", e)

if __name__ == "__main__":
    Server()
