import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from threading import Thread
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot")

        # Chat window
        self.chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # User input field
        self.user_input = tk.Entry(root)
        self.user_input.pack(padx=10, pady=10, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)

        # Initialize the chatbot process
        self.chatbot_process = subprocess.Popen(['python', 'launch.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Start a thread to read the chatbot's output
        self.output_thread = Thread(target=self.read_output)
        self.output_thread.daemon = True
        self.output_thread.start()

        # Start a thread to read the chatbot's error logs
        self.error_thread = Thread(target=self.read_errors)
        self.error_thread.daemon = True
        self.error_thread.start()

    def send_message(self, event=None):
        message = self.user_input.get()
        if message:
            self.chat_window.config(state='normal')
            self.chat_window.insert(tk.END, f"You: {message}\n")
            self.chat_window.config(state='disabled')
            self.chat_window.yview(tk.END)
            self.user_input.delete(0, tk.END)
            self.chatbot_process.stdin.write(f"{message}\n")
            self.chatbot_process.stdin.flush()
            logging.info(f"Sent message to chatbot: {message}")

    def read_output(self):
        while True:
            output = self.chatbot_process.stdout.readline()
            if output:
                self.chat_window.config(state='normal')
                self.chat_window.insert(tk.END, f"Bot: {output}")
                self.chat_window.config(state='disabled')
                self.chat_window.yview(tk.END)
                logging.info(f"Received response from chatbot: {output.strip()}")
            elif self.chatbot_process.poll() is not None:
                break

    def read_errors(self):
        while True:
            error = self.chatbot_process.stderr.readline()
            if error:
                self.chat_window.config(state='normal')
                self.chat_window.insert(tk.END, f"Error: {error}")
                self.chat_window.config(state='disabled')
                self.chat_window.yview(tk.END)
                logging.error(f"Chatbot error: {error.strip()}")
            elif self.chatbot_process.poll() is not None:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatBotUI(root)
    root.mainloop()
