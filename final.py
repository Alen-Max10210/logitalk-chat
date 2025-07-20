from customtkinter import *
from PIL import Image
from socket import *
import threading

class AuthWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x400")
        self.title("Вхід")
        self.resizable(True, False)

        #ліва частина
        self.left_frame = CTkFrame(self)
        self.left_frame.pack(side = "left", fill = "both")

        image_ctk = CTkImage(light_image=Image.open("bg (2).png"), size=(450, 400))
        self.image_label = CTkLabel(self.left_frame, text="Welcome", image=image_ctk,
                                    font=("Helvetica", 60, "bold"), text_color="white")
        self.image_label.pack()

        #права частина
        self.right_frame = CTkFrame(self, fg_color="white")
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side = "right", fill = "both", expand="True")

        self.label = CTkLabel(self.right_frame, font=("Helvetica", 25), text="LogiTalk", text_color="#6753cc")
        self.label.pack(pady = 60)

        self.name_entry = CTkEntry(self.right_frame, placeholder_text="☻ ім'я",
                              placeholder_text_color="#6753cc", fg_color="#eae6ff",
                              border_color="#eae6ff" , corner_radius=45, font=("Helvetica", 25), width=220)
        self.name_entry.pack()

        setting = CTkImage(light_image=Image.open("setting.png"), size=(10, 10))
        self.setting_btn = CTkButton(self.right_frame, text="Налаштування",
                              text_color="#6753cc", fg_color="#eae6ff",
                              corner_radius=45, font=("Helvetica", 25), image=setting,
                              hover_color="#cdc9e1")
        self.setting_btn.pack()

        self.enter_btn = CTkButton(self.right_frame, text="УВІЙТИ", text_color="white",
                                   fg_color="#d06fc0", corner_radius=45,
                                   font=("Helvetica", 25), hover_color="#7b226c", command=self.open_chat)
        self.enter_btn.pack()


    def open_chat(self):
        username = self.name_entry.get().strip()
        if not username:
            username = "Noname"
            return username
        self.destroy()
        #перехід на наступне вікно
        chat_window = MainWindow(username)
        chat_window.mainloop()


class MainWindow(CTk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        self.geometry('800x600')
        self.minsize(500, 400)
        self.label = None

        self.menu_width = 50
        self.target_menu_width = 50
        self.is_show_menu = False
        self.speed_menu = 5

        self.menu_frame = CTkFrame(self, width=self.menu_width, height=600)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.btn_menu = CTkButton(self, text='▶️', width=50, command=self.click_show_menu)
        self.btn_menu.place(x=0, y=0)

        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення', height=40)
        self.btn_send = CTkButton(self, text=">", width=40, height=40, command=self.send_message)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('5.tcp.eu.ngrok.io', 16698))
            hello = f'{self.username} приєднався(-лась) до чату!\n'
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon = True).start()
        except Exception as e:
            self.add_messsage(f"Не вдалося підключитися до сервера {e}")

        self.after(100, self.adaptive_ui)

    def click_show_menu(self):
        self.is_show_menu = not self.is_show_menu
        self.target_menu_width = 200 if self.is_show_menu else 50
        self.btn_menu.configure(text="MENU" if self.is_show_menu else "▶️")

        if self.is_show_menu:
            self.label = CTkLabel(self.menu_frame, text="Ім'я")
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Введіть ваше ім'я")
            self.entry.pack()
        else:
            if self.label:
                self.label.destroy()
            if self.entry:
                self.entry.destroy()

        self.animate_menu()

    def animate_menu(self):
        if self.menu_width != self.target_menu_width:
            if self.menu_width < self.target_menu_width:
                self.menu_width = min(self.menu_width + self.speed_menu, self.target_menu_width)
            else:
                self.menu_width = max(self.menu_width - self.speed_menu, self.target_menu_width)

            self.menu_frame.configure(width=self.menu_width)
            self.after(10, self.animate_menu)

    def adaptive_ui(self):
        SCALE = 1.25
        width = self.winfo_width() / SCALE
        height = self.winfo_height() / SCALE

        self.menu_frame.configure(height=height)

        input_panel_height = 60
        spacing = 10

        chat_x = self.menu_width + 10
        chat_width = width - self.menu_width - 30
        chat_height = height - input_panel_height - spacing

        self.chat_field.place(x=chat_x, y=0)
        self.chat_field.configure(width=chat_width, height=chat_height)

        entry_width = width - self.menu_width - 100
        entry_y = height - input_panel_height

        self.message_entry.place(x=chat_x, y=entry_y)
        self.message_entry.configure(width=entry_width)

        self.btn_send.place(x=chat_x + entry_width + 10, y=entry_y)

        self.after(100, self.adaptive_ui)

    def add_messsage(self, text):
        self.chat_field.configure(state = "normal")
        self.chat_field.insert(END, f"      {text}\n")
        self.chat_field.configure(state = 'disable')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_messsage(f'{self.username}: {message}')
            data = f'TEXT@{self.username}@{message}\n'
            try:
                self.sock.sendall(data.encode())
            except:
                pass

        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ''
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@',3)
        msg_type = parts[0]

        if msg_type == 'TEXT':
            if len(parts) >= 3:
                author = parts[1]
                message= parts[2]
                self.add_messsage(f'{author}: {message}')

        else:
            self.add_messsage(line)


window = AuthWindow()
window.mainloop()