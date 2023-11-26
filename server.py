from tkinter import ttk, simpledialog
from tkinter.simpledialog import askstring
import socket
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import pickle

class Client:
    def __init__(self, name):
        self.name = name
        self.subscriptions = []
        self.direct_messages = {"from1": ["tchau"], "from2": ["oi", "oi"]}

    def subscribe_to_topic(self, topic_name):
        self.subscriptions.append(topic_name)

    def unsubscribe_from_topic(self, topic_name):
        if topic_name in self.subscriptions:
            self.subscriptions.remove(topic_name)

    def send_direct_message(self, recipient, message):
        if recipient in self.direct_messages:
            self.direct_messages[recipient].append(message)
        else:
            self.direct_messages[recipient] = [message]

class Broker:
    def __init__(self):
        self.topics = {"Tópico Inicial": ["Mensagem teste", "Segunda mensagem"]}
        self.clients = {"ExemploCliente": Client("ExemploCliente")}

    def add_client(self, client):
        self.clients[client.name] = client

    def remove_client(self, client):
        self.clients.remove(client)

    def get_clients(self):
        return list(self.clients.keys())

    def get_direct_messages(self, client_name):
        if client_name in self.clients:
            return self.clients[client_name].direct_messages
        else:
            return {}

    def add_topic(self, topic):
        self.topics[topic] = []

    def add_message_in_topic(self, topic, message):
        self.topics[topic].append(message)

    def remove_topic(self, topic):
        del self.topics[topic]

    def get_topics(self):
        return list(self.topics.keys())

    def get_messages_from_topic(self, topic_name):
        return self.topics.get(topic_name, [])

class Server:
    broker = Broker()

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
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                self.broadcast(data)

            except ConnectionResetError:
                print("Conexão encerrada.")
                self.clients.remove(client_socket)
                break

    def broadcast_clients_update(self, clients):
        data = {
            "type": "clients_update",
            "clients": clients
        }
        self.broadcast_data(data)

    def broadcast_topics_update(self, topics):
        data = {
            "type": "topics_update",
            "topics": topics
        }
        self.broadcast_data(data)

    def broadcast_data(self, data):
        serialized_data = pickle.dumps(data)
        for client_socket in self.clients:
            try:
                client_socket.send(serialized_data)
            except Exception as e:
                print("Erro ao enviar mensagem:", e)

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin")

        self.admin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.admin_socket.connect(('localhost', 12345))
        threading.Thread(target=self.receive_updates).start()

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.main_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.message_text = tk.Text(self.main_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.message_text.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.message_text.yview)
        self.message_text.see("end")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.direct_messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.direct_messages_frame, text="Mensagens Diretas")

        self.remove_direct_message_button = tk.Button(self.direct_messages_frame, text="Remover Mensagem Direta",
                                                      command=self.remove_direct_message, padx=20)
        self.remove_direct_message_button.pack()

        self.show_messages_count_button = tk.Button(self.direct_messages_frame, text="Mostrar Quantidade de Mensagens",
                                                    command=self.show_messages_count, padx=20)
        self.show_messages_count_button.pack()

        self.topic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.topic_frame, text="Tópicos")

        self.add_topic_button = tk.Button(self.topic_frame, text="Adicionar Tópico", command=self.add_topic, padx=20)
        self.add_topic_button.pack()

        self.remove_topic_button = tk.Button(self.topic_frame, text="Remover Tópico", command=self.remove_topic, padx=20)
        self.remove_topic_button.pack()

    def receive_updates(self):
        while True:
            data = self.admin_socket.recv(1024)
            if not data:
                break

    def add_topic(self):
        topic_name = askstring("Adicionar Tópico", "Nome do Tópico:")
        if topic_name:
            server.broker.add_topic(topic_name)
            server.broadcast_topics_update(server.broker.get_topics())
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' adicionado.\n")

    def remove_topic(self):
        topics = server.broker.get_topics()
        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos para remover.\n")
            return

        dialog = RemoveTopicDialog(self.root, topics)
        if dialog.result:
            topic_name = dialog.result
            server.broker.remove_topic(topic_name)
            server.broadcast_topics_update(server.broker.get_topics())
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' removido.\n")

    def show_messages_count(self):
            clients = list(server.broker.clients.keys())

            if not clients:
                self.message_text.insert(tk.END, "Não há clientes para mostrar a quantidade de mensagens diretas.\n")
                return

            dialog = SelectRecipientDialog(self.root, clients)
            client_name = dialog.result

            if client_name:
                direct_messages = server.broker.get_direct_messages(client_name)

                if direct_messages:
                    senders = list(direct_messages.keys())

                    sender_options = [f"{sender}" for sender in senders]

                    dialog_sender = SelectRecipientDialog(self.root, sender_options)
                    selected_sender_option = dialog_sender.result

                    selected_sender = selected_sender_option.split(' (')[0] if selected_sender_option else None

                    if selected_sender:
                        message_count = len(direct_messages[selected_sender])
                        messagebox.showinfo("Quantidade de Mensagens", f"O cliente {client_name} tem {message_count} mensagens diretas do remetente {selected_sender}.")
                    else:
                        self.message_text.insert(tk.END, "Operação de mostrar quantidade de mensagem direta cancelada. Remetente não selecionado.\n")
                else:
                    self.message_text.insert(tk.END, f"Não há mensagens diretas para '{client_name}'.\n")
                    
    def remove_direct_message(self):
        clients = list(server.broker.clients.keys())

        if not clients:
            self.message_text.insert(tk.END, "Não há clientes para remover mensagens diretas.\n")
            return

        dialog = SelectRecipientDialog(self.root, clients)
        recipient = dialog.result

        if recipient:
            direct_messages = server.broker.get_direct_messages(recipient)

            if direct_messages:
                senders = list(direct_messages.keys())

                sender_options = [f"{sender}" for sender in senders]

                dialog_sender = SelectRecipientDialog(self.root, sender_options)
                selected_sender_option = dialog_sender.result

                selected_sender = selected_sender_option.split(' (')[0] if selected_sender_option else None

                if selected_sender:
                    if selected_sender in server.broker.clients[recipient].direct_messages:
                        del server.broker.clients[recipient].direct_messages[selected_sender]

                    self.message_text.insert(tk.END,
                                             f"Todas as mensagens diretas de '{selected_sender}' para '{recipient}' foram removidas.\n")
                else:
                    self.message_text.insert(tk.END,
                                             "Operação de remoção de mensagem direta cancelada. Remetente não selecionado.\n")
            else:
                self.message_text.insert(tk.END, f"Não há mensagens diretas para '{recipient}'.\n")

    def update_message_listbox(self, message_listbox, direct_messages, selected_sender):
        messages = direct_messages.get(selected_sender, [])
        message_listbox.delete(0, tk.END)

        for message in messages:
            message_listbox.insert(tk.END, message)

class RemoveTopicDialog(simpledialog.Dialog):
    def __init__(self, parent, topics):
        self.topics = topics
        super().__init__(parent, title="Tópicos")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico:").pack()

        self.topic_name = tk.StringVar()
        self.topic_name.set(self.topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=self.topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()

class SelectTopicDialog(simpledialog.Dialog):
    def __init__(self, parent, topics):
        self.topics = topics
        super().__init__(parent, title="Selecionar Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico para enviar mensagem:").pack()

        self.topic_name = tk.StringVar()
        self.topic_name.set(self.topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=self.topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()

class ListTopicMessagesDialog(simpledialog.Dialog):
    def __init__(self, parent, topics):
        self.topics = topics
        super().__init__(parent, title="Listar Mensagens do Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico para listar mensagens:").pack()

        self.topic_name = tk.StringVar()
        self.topic_name.set(self.topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=self.topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()

class SelectRecipientDialog(simpledialog.Dialog):
    def __init__(self, parent, clients):
        self.clients = clients
        super().__init__(parent, title="Selecionar Destinatário")

    def body(self, master):
        tk.Label(master, text="Selecione o destinatário:").pack()

        self.recipient_var = tk.StringVar()
        self.recipient_var.set(self.clients[0])
        self.recipient_menu = ttk.Combobox(master, textvariable=self.recipient_var, values=self.clients)
        self.recipient_menu.pack()

    def apply(self):
        self.result = self.recipient_var.get()

if __name__ == "__main__":
    root = tk.Tk()
    server = Server()
    AdminApp(root)
    root.mainloop()
