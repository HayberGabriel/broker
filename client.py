import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring
from server import *
import socket
import threading
import pickle

class SocketClient:
    def __init__(self, client):
        self.client = client
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conecta ao servidor (certifique-se de que o servidor está em execução)
        self.client_socket.connect(('localhost', 12345))

        # Inicia uma nova thread para lidar com a comunicação do servidor
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, message):
        # Envia a mensagem serializada para o servidor
        data = pickle.dumps(message)
        self.client_socket.send(data)

    def receive_messages(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                # Decodifica os dados recebidos
                message = pickle.loads(data)

                # Processa a mensagem recebida (implemente conforme necessário)
                self.process_message(message)

        finally:
            self.client_socket.close()

    def process_message(self, message):
        # Lógica para processar a mensagem recebida (implemente conforme necessário)
        print(f"Mensagem recebida pelo cliente: {message}")

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface do Cliente")

        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Text widget para exibir mensagens com barra de rolagem
        self.scrollbar = tk.Scrollbar(self.main_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.message_text = tk.Text(self.main_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.message_text.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.message_text.yview)

        # Rolar para a última linha automaticamente
        self.message_text.see("end")

        self.send_topic_message_button = tk.Button(self.main_frame, text="Enviar Mensagem para Tópico", command=self.open_send_topic_dialog, padx=20)
        self.send_topic_message_button.pack()

        self.send_topic_message_button = tk.Button(self.main_frame, text="Enviar Mensagem Direta", command=self.open_send_direct_message_dialog, padx=20)
        self.send_topic_message_button.pack()

        self.subscribe_topic_button = tk.Button(self.main_frame, text="Assinar Tópico", command=self.subscribe_topic, padx=20)
        self.subscribe_topic_button.pack()

        # Botão para cancelar a assinatura de um tópico
        self.unsubscribe_topic_button = tk.Button(self.main_frame, text="Cancelar Assinatura", command=self.unsubscribe_topic, padx=20)
        self.unsubscribe_topic_button.pack()

    def subscribe_topic(self):
        if client:
            topics = list(broker.topics.keys())

            if not topics:
                self.message_text.insert(tk.END, "Não há tópicos disponíveis para assinar.\n")
                return

            dialog = ListTopicMessagesDialog(self.root, topics)
            selected_topic = dialog.result  # Obter o tópico selecionado

            if selected_topic in client.subscriptions:
                self.message_text.insert(tk.END, f"Você já está inscrito nesse tópico.\n")
               
            else:
                client.subscribe_to_topic(selected_topic)
                self.message_text.insert(tk.END, f"Cliente assinou o tópico '{selected_topic}'.\n")
                self.message_text.insert(tk.END, f"Agora você está inscrito nesses tópicos'{client.subscriptions}'.\n")

    def unsubscribe_topic(self):
        if client:
            topics = list(client.subscriptions)

            if not topics:
                self.message_text.insert(tk.END, "Você não assinou nenhum tópico.\n")
                return

            dialog = ListTopicMessagesDialog(self.root, topics)
            selected_topic = dialog.result  # Obter o tópico selecionado

            if selected_topic:
                client.unsubscribe_from_topic(selected_topic)
                self.message_text.insert(tk.END, f"Cliente cancelou a assinatura do tópico '{selected_topic}'.\n")
                self.message_text.insert(tk.END, f"Agora você está inscrito nesses tópicos'{client.subscriptions}'.\n")

    def open_send_topic_dialog(self):
        topics = list(broker.topics.keys())
        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos disponíveis para enviar mensagens.\n")
            return

        dialog = SelectTopicDialog(self.root, broker)
        if dialog.result:
            topic_name = dialog.result
            message = askstring("Enviar Mensagem para Tópico", "Digite a Mensagem:")
            if message:
                client.add_in_messages_from_topic(topic_name, message)
                broker.add_message_to_topic(topic_name, message)
                self.message_text.insert(tk.END, f"Mensagem enviada para o tópico '{topic_name}': {message}\n")

    def open_send_direct_message_dialog(self):
        recipients = [client.name for client in broker.clients]
        dialog = SendDirectMessageDialog(self.root, recipients)
        result = dialog.result
        if result:
          recipient, message = result
          client.send_direct_message(recipient, message)
          self.message_text.insert(tk.END, f"Mensagem direta para '{recipient}': {message}\n")

if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    client = Client(broker)
    broker.add_client(client)
    socket_client = SocketClient(client)
    ClientApp(root)
    root.mainloop()