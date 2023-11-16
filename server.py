from tkinter import ttk, simpledialog
from tkinter.simpledialog import askstring
from tkinter.simpledialog import Dialog
import socket, pickle, threading, tkinter as tk
import tkinter.messagebox as messagebox

class SocketServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(5)
        self.clients = []
        self.clients_lock = threading.Lock()

        print("Aguardando conexões...")
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão aceita de {addr}")

            with self.clients_lock:
                self.clients.append((client_socket, addr))

            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self):
        pass

class Broker:
    def __init__(self):
        self.clients = {"ExemploCliente": Client("ExemploCliente")}
        
    def add_client(self, client):
        self.clients[client.name] = client

    def remove_client(self, client):
        self.clients.remove(client)

    def get_clients(self):
        return self.clients

    def get_direct_messages(self, client_name):
        if client_name in self.clients:
            return self.clients[client_name].direct_messages
        else:
            return []
        
    def get_direct_messages_for_client(self, client_name):
        if client_name in self.clients:
            return self.clients[client_name].direct_messages
        else:
            return {}
    
    def add_topic(self, topic):
        for client in self.clients.values():
            client.add_topic(topic)

class Client:
    topics = {"Tópico Inicial": ["Mensagem teste", "Segunda mensagem"]}

    def __init__(self, name):
        self.name = name
        self.subscriptions = []
        self.direct_messages = {"from1": ["tchau"], "from2" : ["oi", "oi"]}

    def add_topic(self, topic_name):
        Client.topics[topic_name] = []

    def subscribe_to_topic(self, topic_name):
        if topic_name in Client.topics:
            self.subscriptions.append(topic_name)

    def unsubscribe_from_topic(self, topic_name):
        self.subscriptions.remove(topic_name)

    def add_message_in_topic(self, topic_name, message):
        if topic_name in Client.topics:
            Client.topics[topic_name].append(message)
        else:
            Client.topics[topic_name] = [message]

    def send_direct_message(self, recipient, message):
        if recipient in self.direct_messages:
            self.direct_messages[recipient].append(message)
        else:
            self.direct_messages[recipient] = [message]

class ListDirectMessagesDialog(simpledialog.Dialog):
    def __init__(self, parent, senders):
        self.senders = senders
        super().__init__(parent, title="Selecionar Mensagens Diretas")

    def body(self, frame):
        ttk.Label(frame, text="Selecione o remetente:").pack(pady=10)
        self.sender_var = tk.StringVar()
        self.sender_var.set(self.senders[0] if self.senders else "")
        sender_menu = ttk.Combobox(frame, textvariable=self.sender_var, values=self.senders)
        sender_menu.pack(pady=10)
        return sender_menu

    def apply(self):
        selected_sender = self.sender_var.get()
        self.result = ("Remover", selected_sender)

class RemoveTopicDialog(simpledialog.Dialog):
    def __init__(self, parent, topics):
        self.topics = topics
        super().__init__(parent, title="Remover Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico a ser removido:").pack()

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

class SendTopicMessageDialog(simpledialog.Dialog):
    def __init__(self, parent, topics):
        self.topics = topics
        super().__init__(parent, title="Enviar Mensagem para Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico para enviar mensagem:").pack()

        self.topic_name = tk.StringVar()
        self.topic_name.set(self.topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=self.topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()
   
class SelectTopicDialog(simpledialog.Dialog):
    def __init__(self, parent, client):
        self.client = client
        super().__init__(parent, title="Selecionar Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico para enviar mensagem:").pack()

        self.topic_name = tk.StringVar()
        initial_topics = list(self.client.topics.keys())
        self.topic_name.set(initial_topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=initial_topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()

class SelectDirectMessageDialog(simpledialog.Dialog):
    def __init__(self, parent, client, direct_messages):
        self.client = client
        self.direct_messages = direct_messages
        super().__init__(parent, title=f"Selecionar Mensagem Direta para {self.client}")

    def body(self, master):
        tk.Label(master, text="Selecione a mensagem direta:").pack()

        self.direct_message_var = tk.StringVar()
        self.direct_message_listbox = tk.Listbox(master, listvariable=self.direct_message_var, selectmode=tk.SINGLE)
        self.direct_message_listbox.pack()

        # Obter as mensagens diretas do cliente específico
        client_direct_messages = self.direct_messages.get(self.client, {}).keys()

        for direct_message in client_direct_messages:
            self.direct_message_listbox.insert(tk.END, direct_message)

    def apply(self):
        selected_direct_message = self.direct_message_listbox.get(tk.ACTIVE)
        self.result = selected_direct_message

class SelectRecipientDialog(simpledialog.Dialog):
    def __init__(self, parent, clients):
        self.clients = clients
        super().__init__(parent, title="Selecionar Destinatário")

    def body(self, master):
        tk.Label(master, text="Selecione o destinatário:").pack()

        self.recipient_var = tk.StringVar()
        self.recipient_var.set(self.clients[0])  # Defina o primeiro cliente como padrão
        self.recipient_menu = ttk.Combobox(master, textvariable=self.recipient_var, values=self.clients)
        self.recipient_menu.pack()

    def apply(self):
        self.result = self.recipient_var.get()

class SendDirectMessageDialog(Dialog):
    def __init__(self, parent, recipients, client):
        self.recipients = recipients
        self.client = client
        super().__init__(parent)

    def body(self, master):
        self.title("Enviar Mensagem Direta")
        tk.Label(master, text="Selecione o destinatário:").pack()

        self.recipient_var = tk.StringVar()
        self.recipient_listbox = tk.Listbox(master, listvariable=self.recipient_var, selectmode=tk.SINGLE)
        self.recipient_listbox.pack()

        for recipient in self.recipients:
            self.recipient_listbox.insert(tk.END, recipient)

        tk.Label(master, text="Digite a mensagem:").pack()
        self.message_entry = tk.Entry(master)
        self.message_entry.pack()

    def buttonbox(self):
        box = tk.Frame(self)
        send_button = tk.Button(box, text="Enviar", width=10, command=self.send_message)
        box.pack()
        send_button.pack(side=tk.LEFT)
        self.bind("<Return>", self.send_message)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def send_message(self, event=None):
        recipient = self.recipient_listbox.get(tk.ACTIVE)
        message = self.message_entry.get()
        if recipient and message:
            self.client.send_direct_message(self.client.name, message)
            self.result = (recipient, message)
            self.cancel()

class ShowMessagesCountDialog(simpledialog.Dialog):
    def __init__(self, parent, client, direct_messages):
        self.client = client
        self.direct_messages = direct_messages
        super().__init__(parent, title=f"Quantidade de Mensagens para {self.client}")

    def body(self, master):
        # Obter a lista de mensagens diretas do cliente específico
        client_direct_messages = self.direct_messages.get(self.client, {}).keys()

        tk.Label(master, text=f"Selecione a mensagem direta para {self.client}:").pack()

        self.direct_message_var = tk.StringVar()
        self.direct_message_listbox = tk.Listbox(master, listvariable=self.direct_message_var, selectmode=tk.SINGLE)
        self.direct_message_listbox.pack()

        for direct_message in client_direct_messages:
            self.direct_message_listbox.insert(tk.END, direct_message)

    def apply(self):
        selected_direct_message = self.direct_message_listbox.get(tk.ACTIVE)
        # Obter a lista real de mensagens diretas
        messages = self.direct_messages.get(self.client, {}).get(selected_direct_message, [])
        messagebox.showinfo("Quantidade de Mensagens", f"Quantidade de mensagens para {self.client} - {selected_direct_message}: {len(messages)}")

class AdminApp:
    def __init__(self, root, broker):
        self.root = root
        self.root.title("Interface do Admin")
        self.broker = broker

        self.topic_name = tk.StringVar()
        self.topic_name.set("topic1")

        self.client_name = tk.StringVar()
        self.client_name.set("Cliente1")

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

        # Aba para mensagens diretas
        self.direct_messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.direct_messages_frame, text="Mensagens Diretas")

        self.show_direct_messages_button = tk.Button(self.direct_messages_frame, text="Visualizar Mensagens Diretas",
                                                     command=self.show_direct_messages, padx=20)
        self.show_direct_messages_button.pack()

        self.remove_direct_message_button = tk.Button(self.direct_messages_frame, text="Remover Mensagem Direta",
                                                      command=self.remove_direct_message, padx=20)
        self.remove_direct_message_button.pack()

        self.show_messages_count_button = tk.Button(self.direct_messages_frame, text="Mostrar Quantidade de Mensagens",
                                                    command=self.show_messages_count, padx=20)
        self.show_messages_count_button.pack()

        # Aba para tópicos
        self.topic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.topic_frame, text="Tópicos")

        self.add_topic_button = tk.Button(self.topic_frame, text="Adicionar Tópico", command=self.add_topic, padx=20)
        self.add_topic_button.pack()

        self.remove_topic_button = tk.Button(self.topic_frame, text="Remover Tópico", command=self.remove_topic, padx=20)
        self.remove_topic_button.pack()

        self.list_topic_messages_button = tk.Button(self.topic_frame, text="Listar Mensagens do Tópico",
                                                    command=self.list_topic_messages, padx=20)
        self.list_topic_messages_button.pack()

    def add_topic(self):
        topic_name = askstring("Adicionar Tópico", "Nome do Tópico:")
        if topic_name:
            Client.topics[topic_name] = []
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' adicionado.\n")

    def remove_topic(self):
        topics = list(Client.topics.keys())
        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos para remover.\n")
            return

        dialog = RemoveTopicDialog(self.root, topics)
        if dialog.result:
            topic_name = dialog.result
            del Client.topics[topic_name]
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' removido.\n")

    def list_topic_messages(self):
        topics = list(Client.topics.keys())

        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos para listar mensagens.\n")
            return

        dialog = ListTopicMessagesDialog(self.root, topics)
        if dialog.result:
            topic_name = dialog.result
            messages = Client.topics.get(topic_name, [])

            if not messages:
                self.message_text.insert(tk.END, f"Não há mensagens no tópico '{topic_name}'.\n")
            else:
                self.message_text.insert(tk.END, f"Mensagens no tópico '{topic_name}':\n")
                for message in messages:
                    self.message_text.insert(tk.END, f"{message}\n")  # Ajuste aqui

    def show_messages_count(self):
        client_name = askstring("Selecionar Cliente", "Digite o nome do cliente:")
        if client_name:
            messages = self.broker.get_direct_messages(client_name)
            message_count = len(messages)
            messagebox.showinfo("Quantidade de Mensagens", f"O cliente {client_name} tem {message_count} mensagens diretas.")

    def show_direct_messages(self):
        # Adicione a lógica para exibir mensagens diretas aqui
        clients = list(self.broker.clients.keys())

        if not clients:
            self.message_text.insert(tk.END, "Não há clientes para exibir mensagens diretas.\n")
            return

        # Selecionar cliente
        dialog = SelectRecipientDialog(self.root, clients)
        recipient = dialog.result

        if recipient:
            # Obter as mensagens diretas do cliente
            direct_messages = self.broker.get_direct_messages_for_client(recipient)

            if direct_messages:
                senders = list(direct_messages.keys())
                
                # Criar uma janela personalizada para exibir as mensagens diretas
                show_messages_dialog = tk.Toplevel(self.root)
                show_messages_dialog.title(f"Mensagens Diretas de {recipient}")

                tk.Label(show_messages_dialog, text=f"Mensagens diretas do {recipient}:").pack(pady=10)

                for sender, messages in direct_messages.items():
                    tk.Label(show_messages_dialog, text=f"Remetente: {sender}").pack()
                    for message in messages:
                        tk.Label(show_messages_dialog, text=f"- {message}").pack()
                    tk.Label(show_messages_dialog, text="").pack()

            else:
                self.message_text.insert(tk.END, f"Não há mensagens diretas para '{recipient}'.\n") 
    
    def remove_direct_message(self):
        clients = list(self.broker.clients.keys())

        if not clients:
            self.message_text.insert(tk.END, "Não há clientes para remover mensagens diretas.\n")
            return

        # Selecionar cliente
        dialog = SelectRecipientDialog(self.root, clients)
        recipient = dialog.result

        if recipient:
            # Obter as mensagens diretas do cliente
            direct_messages = self.broker.get_direct_messages_for_client(recipient)

            if direct_messages:
                senders = list(direct_messages.keys())
                
                # Criar uma janela personalizada para exibir as mensagens diretas e permitir a seleção
                select_message_dialog = tk.Toplevel(self.root)
                select_message_dialog.title("Selecionar Mensagem Direta para Remover")

                tk.Label(select_message_dialog, text="Selecione o remetente:").pack(pady=10)

                sender_var = tk.StringVar()
                sender_var.set(senders[0] if senders else "")
                sender_menu = ttk.Combobox(select_message_dialog, textvariable=sender_var, values=senders)
                sender_menu.pack(pady=10)

                def remove_message():
                    selected_sender = sender_var.get()
                    messages = direct_messages[selected_sender]

                    if messages:
                        selected_message = message_listbox.get(tk.ACTIVE)
                        
                        if selected_message:
                            messages.remove(selected_message)
                            self.message_text.insert(tk.END,
                                                    f"Mensagem direta removida de '{selected_sender}': {selected_message}\n")
                            select_message_dialog.destroy()
                        else:
                            self.message_text.insert(tk.END,
                                                    "Operação de remoção de mensagem direta cancelada.\n")
                    else:
                        self.message_text.insert(tk.END,
                                                f"Não há mensagens diretas de '{selected_sender}' para remover.\n")

                remove_button = tk.Button(select_message_dialog, text="Remover", command=remove_message)
                remove_button.pack()

                tk.Label(select_message_dialog, text="Selecione a mensagem:").pack(pady=10)

                message_var = tk.StringVar()
                message_listbox = tk.Listbox(select_message_dialog, listvariable=message_var, selectmode=tk.SINGLE)
                message_listbox.pack()

                sender_menu.bind("<<ComboboxSelected>>", lambda event: self.update_message_listbox(message_listbox, direct_messages, sender_var.get()))

                select_message_dialog.protocol("WM_DELETE_WINDOW", lambda: self.message_text.insert(tk.END,
                                                                                                    "Operação de remoção de mensagem direta cancelada.\n"))
            else:
                self.message_text.insert(tk.END, f"Não há mensagens diretas para '{recipient}'.\n")

    def update_message_listbox(self, message_listbox, direct_messages, selected_sender):
        messages = direct_messages.get(selected_sender, [])
        message_listbox.delete(0, tk.END)  # Limpa a lista atual

        for message in messages:
            message_listbox.insert(tk.END, message)
        
if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    AdminApp(root, broker)
    SocketServer()
    root.mainloop()