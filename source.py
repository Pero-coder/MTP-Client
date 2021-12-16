#!/usr/bin/env python3

import socket
import pynetstring
import base64
from typing import Tuple
from tkinter import StringVar, Tk, ttk, filedialog, Text
from tkinter.messagebox import showerror, showinfo


window = Tk()
window.title("MTP Client")


def check_data(host: str, port: str, nick: str, password: str, image: str,
               description: str, nsfw: str) -> str:
    """Checks if given data are valid and handles possible error."""


    if "" in [host, port, nick, password, image, description]:
        showerror("Unfilled entry!", "All entries has to be filled!")
        return

    if port.isdigit():
        port = int(port)
        if port <= 65535 and port >= 0:
            pass

        else:
            showerror("Invalid port", "Port is invalid number!")
            return
    else:
        showerror("Invalid port", "Port isn't number!")
        return

    if nsfw == "":
        nsfw = "false"

    try:
        send_meme(host, int(port), nick, password, image, description, nsfw)
    except Exception as error:
        showerror("Send error", str(error))  


def send_meme(host: str, port: int, nick: str, password: str, image: str,
              description: str, nsfw: str) -> str:
    """Connects and takes care of communication with server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except Exception as error:
            showerror("Connection failed", str(error))
            return

        message = "C MTP V:1.0"
        s.sendall(pynetstring.encode(f"{message}"))
        print(f"-> {message}")

        data = s.recv(1024)
        print("<-", data.decode("utf-8"))

        s.sendall(pynetstring.encode(f"C {nick}"))
        print(f"-> C {nick}")

        token = s.recv(1024)
        print("<-", token.decode("utf-8"))

        port = s.recv(1024)
        print("<-", port.decode("utf-8"))

        token = pynetstring.decode(token)[0].decode("utf-8")[2:]
        d_port = pynetstring.decode(port)[0].decode("utf-8")[2:]

        d_token, total_data_len = data_channel(host, int(d_port), nick, password, token,
                image, description, nsfw)

        data_len_check = s.recv(1024)
        print("<-", data_len_check.decode("utf-8"))
        if data_len_check.decode("utf-8").find(str(total_data_len)) == -1:
            s.sendall(pynetstring.encode("E Data length doesn't match"))
            raise Exception("Data length didn't match length sent by server")

        s.sendall(pynetstring.encode(f"C {d_token}"))
        print(f"-> C {d_token}")

        success = s.recv(1024)
        print("<-", success.decode("utf-8"))

        if success.decode().find("S ACK") != -1:
            showinfo("Success", "Meme was successfully delivered!")


def data_channel(host: str, port: int, nick: str, password: str, token: str, image: str, 
        description: str, nsfw: str) -> Tuple[str, int]:
    """
    Communicates with server in data channel, sends data.
    Returns data token and length of sent data
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        s.sendall(pynetstring.encode(f"C {nick}"))
        print(f"-> C {nick}")

        check_token = s.recv(1024)
        print("<-", check_token.decode("utf-8"))
        if check_token.decode("utf-8").find(token) == -1:
            s.sendall(pynetstring.encode("E Invalid token"))
            raise Exception("Token didn't match token sent by server")
        
        responce = s.recv(1024)
        print("<-", responce.decode("utf-8"))

        req = [image, password, description, nsfw]
        total_data_len = 0

        for data in req:
            total_data_len += len(data)
            s.sendall(pynetstring.encode(f"C {data}"))
            print(f"-> C {(data[:25] + '..') if len(data) > 25 else data}")

            check = s.recv(1024)
            print("<-", check.decode("utf-8"))
            if check.decode("utf-8").find(str(len(data))) == -1:
                s.sendall(pynetstring.encode("E Data doesn't match"))
                raise Exception("Data length didn't match")
            
            responce = s.recv(1024)
            print("<-", responce.decode("utf-8"))

        return (pynetstring.decode(responce)[0].decode("utf-8")[6:], total_data_len)

class GUI_client:
    def __init__(self, window: Tk) -> None:
        self.image = ""
        self.window = window
    
    def open_file(self) -> None:
        """Open and convert image to right format"""
        try:
            with filedialog.askopenfile(
                    "rb", 
                    defaultextension=(".png", ".jpg"),
                    title="Choose meme"
                    ) as file:

                image_path_label = ttk.Label(self.window, text=f"Selected file: {file.name}")
                image_path_label.grid(row=7, column=0, columnspan=3)

                self.image = base64.b64encode(file.read()).decode("ascii")
        
        except AttributeError:
            pass


    def main_window(self) -> None:
        """Displays form for filling needed information"""

        nick = StringVar()
        nick_label = ttk.Label(self.window, text="Nick:")
        nick_entry = ttk.Entry(self.window, textvariable=nick)
        nick_label.grid(row=0, column=0)
        nick_entry.grid(row=0, column=1)

        password = StringVar()
        password_label = ttk.Label(self.window, text="Password:")
        password_entry = ttk.Entry(window, textvariable=password)
        password_label.grid(row=0, column=2)
        password_entry.grid(row=0, column=3)

        host = StringVar()
        host_label = ttk.Label(self.window, text="Host:")
        host_entry = ttk.Entry(self.window, textvariable=host)
        host_label.grid(row=1, column=0)
        host_entry.grid(row=1, column=1)

        port = StringVar()
        port_label = ttk.Label(self.window, text="Port:")
        port_entry = ttk.Entry(self.window, textvariable=port)
        port_label.grid(row=1, column=2)
        port_entry.grid(row=1, column=3)

        nsfw = StringVar()
        nsfw_label = ttk.Label(self.window, text="NSFW:")
        nsfw_button = ttk.Checkbutton(self.window, variable=nsfw, onvalue="true", offvalue="false")
        nsfw_label.grid(row=2, column=0)
        nsfw_button.grid(row=2, column=1, sticky="W")

        description_label = ttk.Label(self.window, text="Description:")
        description = Text(window, height=5, width=50, font="Calibri")
        description_label.grid(row=3, column=0)
        description.grid(row=4, column=0, rowspan=2, columnspan=4)


        select_image = ttk.Button(self.window, text="Select meme", command=self.open_file)
        select_image.grid(row=6, column=0)

        send_button = ttk.Button(
                window, 
                command=lambda: check_data(host.get(), port.get(), nick.get(), 
                        password.get(), self.image, description.get(1.0, "end-1c"), 
                        nsfw.get().lower()), text="Send meme")

        send_button.grid(row=6, column=3)

if __name__ == "__main__":
    mw = GUI_client(window)
    mw.main_window()
    window.mainloop()
