from tkinter import ttk
from tkinter.simpledialog import askstring
from admin import *
import tkinter as tk

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Bem vindo {client.name}!")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))
        threading.Thread(target=self.receive_updates).start()

        self.shared_variable = tk.IntVar()
        self.shared_variable.set(6)
        self.label = tk.Label(root, textvariable=self.shared_variable, font=('Helvetica', 24))
        #self.label.pack(pady=20)

        increment_button = tk.Button(root, text="Incrementar", command=self.increment_value)
        #increment_button.pack()

        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Text widget para exibir mensagens com barra de rolagem
        self.scrollbar = tk.Scrollbar(self.main_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.message_text = tk.Text(self.main_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.message_text.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.message_text.yview)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 12345))

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

    def increment_value(self):
        new_value = self.shared_variable.get() + 1
        self.client_socket.send(str(new_value).encode())

    def receive_updates(self):
        while True:
            data = self.client_socket.recv(1024)
            if not data:
                break
            value = int(data.decode())
            self.shared_variable.set(value)    

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
                for message in client.topics[selected_topic]:
                    self.message_text.insert(tk.END, f"- {message}\n")
                self.message_text.insert(tk.END, "\n")

    def show_direct_messages(self):
        self.message_text.insert(tk.END, "Suas mensagens diretas:\n")

        for sender, messages in client.direct_messages.items():
            #if sender != client.name:
                self.message_text.insert(tk.END, f"{sender}\n")
                for message in messages:
                    self.message_text.insert(tk.END, f"- {message}\n")
                self.message_text.insert(tk.END, "\n")

    def send_direct_message(self, recipient):
        def send_message():
            message = message_entry.get()

            # Adicione esta lógica para enviar a mensagem diretamente para o destinatário
            client.send_direct_message(recipient, message)

            send_direct_message_dialog.destroy()

        send_direct_message_dialog = tk.Toplevel(self.root)
        send_direct_message_dialog.title(f"Enviar Mensagem Direta para '{recipient}'")

        tk.Label(send_direct_message_dialog, text=f"Enviar mensagem direta para '{recipient}':").pack()

        message_entry = tk.Entry(send_direct_message_dialog, width=50)
        message_entry.pack()

        send_button = tk.Button(send_direct_message_dialog, text="Enviar", command=send_message)
        send_button.pack()

    def subscribe_topic(self):
        if client:
            # Obtenha a lista atualizada de tópicos
            topics = list(client.topics.keys())
            
            if not topics:
                self.message_text.insert(tk.END, "Não há tópicos disponíveis para assinar.\n")
                return

            dialog = ListTopicMessagesDialog(self.root, topics)
            selected_topic = dialog.result  # Obter o tópico selecionado

            if selected_topic:
                if selected_topic in client.subscriptions:
                    self.message_text.insert(tk.END, f"Você já está inscrito nesse tópico.\n")
                else:
                    client.subscribe_to_topic(selected_topic)
                    self.message_text.insert(tk.END, f"Cliente assinou o tópico '{selected_topic}'.\n")
                    self.message_text.insert(tk.END, f"Agora você está inscrito nesses tópicos: {client.subscriptions}.\n")
            else:
                pass
    
    def unsubscribe_topic(self):
        if client:
            topics = list(client.topics.keys())

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
        topics = list(client.topics.keys())
        if not topics:
            self.message_text.insert(tk.END, "Não há tópicos disponíveis para enviar mensagens.\n")
            return

        dialog = SelectTopicDialog(self.root, client)
        if dialog.result:
            topic_name = dialog.result
            message = askstring("Enviar Mensagem para Tópico", "Digite a Mensagem:")
            if message:
                client.add_message_in_topic(topic_name, message)
                self.message_text.insert(tk.END, f"Mensagem enviada para o tópico '{topic_name}': {message}\n")

    def open_send_direct_message_dialog(self):
            recipients = [client_name for client_name in broker.clients]

            if not recipients:
                self.message_text.insert(tk.END, "Você não pode enviar mensagens diretas porque não há destinatários disponíveis.\n")
                return

            dialog = SelectRecipientDialog(self.root, recipients)
            selected_recipient = dialog.result

            if selected_recipient:
                self.send_direct_message(selected_recipient)

if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    client_name = simpledialog.askstring("Nome do Cliente", "Digite seu nome:")
    if client_name:
        client = Client(client_name)
    broker.add_client(client)  # Adiciona a instância do cliente ao invés do nome
    client_app = ClientApp(root)
    root.mainloop()