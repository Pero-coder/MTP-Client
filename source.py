#!/usr/bin/env python3

import socket
from typing import Tuple
import pynetstring
import base64
from tkinter import StringVar, Tk, ttk


window = Tk()
window.title("MTP Client")

HOST = '159.89.4.84'  # The server's hostname or IP address
PORT = 42069        # The port used by the server

def send_meme(host: str, port: int, nick: str, password: str, image: str, description: str, 
              nsfw: str) -> str:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

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
        port = pynetstring.decode(port)[0].decode("utf-8")[2:]

        d_token, total_data_len = data_channel(nick, password, int(port), token,
                image, description, nsfw)

        print("total_data_len:", total_data_len)
        data_len_check = s.recv(1024)
        print("<-", data_len_check.decode("utf-8"))
        if data_len_check.decode("utf-8").find(str(total_data_len)) == -1:
            print("Message lenght doesn't match")

        s.sendall(pynetstring.encode(f"C {d_token}"))
        print(f"-> C {d_token}")

        success = s.recv(1024)
        print("<-", success.decode("utf-8"))


def data_channel(nick: str, password: str, port: int, token: str, image: str, 
        description: str, nsfw: str) -> Tuple[str, int]:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, port))

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
                raise Exception("Data lenght didn't match")
            
            responce = s.recv(1024)
            print("<-", responce.decode("utf-8"))

        return (pynetstring.decode(responce)[0].decode("utf-8")[6:], total_data_len)


def main_window(window: Tk) -> None:
    nick = StringVar()
    nick_label = ttk.Label(window, text="Nick:")
    nick_entry = ttk.Entry(window, textvariable=nick)
    nick_label.grid(row=0, column=0)
    nick_entry.grid(row=0, column=1)

    password = StringVar()
    password_label = ttk.Label(window, text="Password:")
    password_entry = ttk.Entry(window, textvariable=password)
    password_label.grid(row=0, column=2)
    password_entry.grid(row=0, column=3)

    host = StringVar()
    host_label = ttk.Label(window, text="Host:")
    host_entry = ttk.Entry(window, textvariable=host)
    host_label.grid(row=1, column=0)
    host_entry.grid(row=1, column=1)

    port = StringVar()
    port_label = ttk.Label(window, text="Port:")
    port_entry = ttk.Entry(window, textvariable=port)
    port_label.grid(row=1, column=2)
    port_entry.grid(row=1, column=3)



# nick = input("Nick: ")
# password = input("Password: ")
# description = input("Description: ")
# nsfw = input("NSFW (true/false): ")
# while not nsfw in ["true", "false"]:
    # print("Invalid input! 'true' or 'false' only")
    # nsfw = input("NSFW (true/false): ")
# image = base64.b64encode(open(r"C:\Users\tompe\Desktop\padoru_astolfo.png", "rb").read()).decode("ascii")

# send_meme(HOST, PORT, nick, password, image, description, nsfw)


if __name__ == "__main__":
    main_window(window)
    window.mainloop()
