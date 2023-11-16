from tkinter import ttk
from tkinter.simpledialog import askstring
from server import *
import socket, time, pickle, threading, tkinter as tk

class SocketClient:
    def __init__(self, client):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        client.socket = self.client_socket

        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        while True:
            # Adicione a lógica para receber mensagens do servidor aqui
            pass

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Bem vindo {client.name}!")

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

        self.show_topic_messages_button = tk.Button(self.main_frame, text="Mostrar Mensagens dos Tópicos", command=self.show_topic_messages, padx=20)
        self.show_topic_messages_button.pack()

        # Botão para exibir mensagens diretas
        self.show_direct_messages_button = tk.Button(self.main_frame, text="Mostrar Mensagens Diretas", command=self.show_direct_messages, padx=20)
        self.show_direct_messages_button.pack()


    def show_topic_messages(self):
        if client:
            topics = list(client.subscriptions)

            if not topics:
                self.message_text.insert(tk.END, "Você não assinou nenhum tópico.\n")
                return

            dialog = ListTopicMessagesDialog(self.root, topics)
            selected_topic = dialog.result  # Obter o tópico selecionado

            if selected_topic:
                self.message_text.insert(tk.END, f"Mostrando mensagens do tópico '{selected_topic}':\n")
                for message in broker.get_topic_messages(selected_topic):
                    self.message_text.insert(tk.END, f"- {message}\n")
                self.message_text.insert(tk.END, "\n")

    def show_direct_messages(self):
        if client:
            self.message_text.insert(tk.END, "Suas mensagens diretas:\n")

            for sender, messages in client.direct_messages.items():
                self.message_text.insert(tk.END, f"Remetente: {sender}\n")
                for message in messages:
                    self.message_text.insert(tk.END, f"- {message}\n")
                self.message_text.insert(tk.END, "\n")

            if not client.direct_messages:
                self.message_text.insert(tk.END, "Você não tem mensagens diretas.\n")

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
        recipients = [client_name for client_name in broker.clients if client_name != client.name]
        dialog = SendDirectMessageDialog(self.root, recipients, client)
        result = dialog.result
        if result:
            recipient, message = result
            client.send_direct_message(recipient, message)
            self.message_text.insert(tk.END, f"Mensagem direta para '{recipient}': {message}\n")

if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    client_name = simpledialog.askstring("Nome do Cliente", "Digite seu nome:")
    if client_name:
        client = Client(client_name, broker)
        broker.add_client(client)  # Adiciona a instância do cliente ao invés do nome
    socket_client = SocketClient(client)
    ClientApp(root)
    root.mainloop()