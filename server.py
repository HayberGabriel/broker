import threading
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter.simpledialog import askstring
from tkinter.simpledialog import Dialog
import socket
import pickle

class SocketServer:
    def __init__(self, broker):
        self.broker = broker
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))  # Escolha uma porta disponível
        self.server_socket.listen(5)

        print("Aguardando conexões...")
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão aceita de {addr}")

            # Inicia uma nova thread para lidar com o cliente
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Decodifica os dados recebidos
                message = pickle.loads(data)

                # Processa a mensagem recebida (implemente conforme necessário)
                self.process_message(message)

        finally:
            client_socket.close()

    def process_message(self, message):
        # Lógica para processar a mensagem recebida (implemente conforme necessário)
        print(f"Mensagem recebida: {message}")

class Broker:
    def __init__(self):
        self.topics = {"Tópico Inicial": ["Mensagem teste", "Segunda mensagem"]}
        self.clients = []

    def add_topic(self, topic_name):
        self.topics[topic_name] = []

    def remove_topic(self, topic_name):
        if topic_name in self.topics:
            del self.topics[topic_name]
        return list(self.topics.keys())

    def add_client(self, client):
        self.clients.append(client)

    def list_topic_messages(self, topic_name):
        if topic_name in self.topics:
            return self.topics[topic_name]
        else:
            return []
        
    def add_message_to_topic(self, topic_name, message):
        self.topics[topic_name].append(message)

class Client:
    def __init__(self, name):
        self.name = name
        self.subscriptions = ["Tópico Inicial"]
        self.messages_from_topic = {"topic": ["message1", "message2"]}
        self.queue = {"from":["message1", "message2"]}

    def subscribe_to_topic(self, topic_name):
        self.subscriptions.append(topic_name)

    def unsubscribe_from_topic(self, topic_name):
        self.subscriptions.remove(topic_name)

    def add_in_messages_from_topic(self, topic_name, message):
        if topic_name not in self.messages_from_topic:
            self.messages_from_topic[topic_name] = []
        self.messages_from_topic[topic_name].append(message)

    def receive_direct_message(self, sender_name, message):
        print(f"Direct message received from '{sender_name}': {message}")

class RemoveQueueDialog(simpledialog.Dialog):
    def __init__(self, parent, queues):
        self.queues = queues
        super().__init__(parent, title="Remover Fila")

    def body(self, master):
        tk.Label(master, text="Selecione a fila a ser removida:").pack()

        self.queue_name = tk.StringVar()
        self.queue_name.set(self.queues[0])

        self.queue_selection = ttk.Combobox(master, textvariable=self.queue_name, values=self.queues)
        self.queue_selection.pack()

    def apply(self):
        self.result = self.queue_name.get()

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

class ListQueueMessagesDialog(simpledialog.Dialog):
    def __init__(self, parent, queues):
        self.queues = queues
        super().__init__(parent, title="Listar Mensagens da Fila")

    def body(self, master):
        tk.Label(master, text="Selecione a fila para listar mensagens:").pack()

        self.queue_name = tk.StringVar()
        self.queue_name.set(self.queues[0])

        self.queue_selection = ttk.Combobox(master, textvariable=self.queue_name, values=self.queues)
        self.queue_selection.pack()

    def apply(self):
        self.result = self.queue_name.get()
      
class SelectTopicDialog(simpledialog.Dialog):
    def __init__(self, parent, broker):
        self.broker = broker
        super().__init__(parent, title="Selecionar Tópico")

    def body(self, master):
        tk.Label(master, text="Selecione o tópico para enviar mensagem:").pack()

        self.topic_name = tk.StringVar()
        initial_topics = list(self.broker.topics.keys())
        self.topic_name.set(initial_topics[0])

        self.topic_selection = ttk.Combobox(master, textvariable=self.topic_name, values=initial_topics)
        self.topic_selection.pack()

    def apply(self):
        self.result = self.topic_name.get()

class SelectRecipientDialog:
    def __init__(self, parent, clients):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Selecionar Destinatário")

        self.label = tk.Label(self.dialog, text="Selecione o destinatário:")
        self.label.pack(padx=10, pady=10)

        self.recipient_var = tk.StringVar()
        self.recipient_var.set(clients[0])  # Defina o primeiro cliente como padrão
        self.recipient_menu = ttk.Combobox(self.dialog, textvariable=self.recipient_var, values=clients)
        self.recipient_menu.pack(padx=10, pady=10)

        self.select_button = tk.Button(self.dialog, text="Selecionar", command=self.select)
        self.select_button.pack(padx=10, pady=10)

    def select(self):
        self.result = self.recipient_var.get()
        self.dialog.destroy()

class SendDirectMessageDialog(Dialog):
    def __init__(self, parent, recipients):
        self.recipients = recipients
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
            self.result = (recipient, message)
            self.cancel()

class AdminApp:
    def __init__(self, root, broker):
        self.root = root
        self.root.title("Interface do Admin")
        self.broker = broker

        self.queue_count = 1

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

        self.queue_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.queue_frame, text="Filas")

        self.create_queue_button = tk.Button(self.queue_frame, text="Adicionar Fila", command=self.add_queue, padx=20)
        self.create_queue_button.pack()

        self.remove_queue_button = tk.Button(self.queue_frame, text="Remover Fila", command=self.remove_queue, padx=20)
        self.remove_queue_button.pack()

        self.list_queue_messages_button = tk.Button(self.queue_frame, text="Listar Quantidade de Mensagens na Fila", command=self.list_queue_messages, padx=20)
        self.list_queue_messages_button.pack()

        self.topic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.topic_frame, text="Tópicos")

        self.add_topic_button = tk.Button(self.topic_frame, text="Adicionar Tópico", command=self.add_topic, padx=20)
        self.add_topic_button.pack()

        self.remove_topic_button = tk.Button(self.topic_frame, text="Remover Tópico", command=self.remove_topic, padx=20)
        self.remove_topic_button.pack()

        self.list_topic_messages_button = tk.Button(self.topic_frame, text="Listar Mensagens do Tópico",
                                                    command=self.list_topic_messages, padx=20)
        self.list_topic_messages_button.pack()

    def add_queue(self):
        queue_name = f"fila{self.queue_count}"
        self.broker.add_queue(queue_name)
        self.message_text.insert(tk.END, f"Fila '{queue_name}' adicionada.\n")
        self.queue_count += 1

    def remove_queue(self):
        queues = list(self.broker.queues.keys())
        if not queues:
            self.message_text.insert(tk.END, "Não há filas para remover.\n")
            return

        dialog = RemoveQueueDialog(self.root, queues)
        if dialog.result:
            queue_name = dialog.result
            self.broker.remove_queue(queue_name)
            self.message_text.insert(tk.END, f"Fila '{queue_name}' removida.\n")

    def list_queue_messages(self):
      queues = list(self.broker.queues.keys())
      if not queues:
          self.message_text.insert(tk.END, "Não há filas para listar mensagens.\n")
          return

      dialog = ListQueueMessagesDialog(self.root, queues)
      if dialog.result:
          queue_name = dialog.result
          message_count = self.broker.list_messages_count(queue_name)
          self.message_text.insert(tk.END, f"A fila '{queue_name}' contém {message_count} mensagens.\n")

    def add_topic(self):
        topic_name = askstring("Adicionar Tópico", "Nome do Tópico:")
        if topic_name:
            self.broker.add_topic(topic_name)
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' adicionado.\n")

    def remove_topic(self):
        topics = list(self.broker.topics.keys())
        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos para remover.\n")
            return

        dialog = RemoveTopicDialog(self.root, topics)
        if dialog.result:
            topic_name = dialog.result
            self.broker.remove_topic(topic_name)
            self.message_text.insert(tk.END, f"Tópico '{topic_name}' removido.\n")

    def list_topic_messages(self):
        topics = list(self.broker.topics.keys())

        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos para listar mensagens.\n")
            return

        dialog = ListTopicMessagesDialog(self.root, topics)
        if dialog.result:
            topic_name = dialog.result
            messages = self.broker.list_topic_messages(topic_name)

            if not messages:
                self.message_text.insert(tk.END, f"Não há mensagens no tópico '{topic_name}'.\n")
            else:
                self.message_text.insert(tk.END, f"Mensagens no tópico '{topic_name}':\n")
                for message in messages:
                    self.message_text.insert(tk.END, f"{message}\n")  # Ajuste aqui

if __name__ == "__main__":
    broker = Broker()
    server = SocketServer(broker)

    root = tk.Tk()
    AdminApp(root, broker)  # Passamos a instância do broker para a aplicação
    root.mainloop()