#!/usr/bin/env python3

import socket
from typing import Tuple
import pynetstring
import base64

image = base64.b64encode(open(r"C:\Users\tompe\Desktop\padoru_astolfo.png", "rb").read()).decode("ascii")

HOST = '159.89.4.84'  # The server's hostname or IP address
PORT = 42069        # The port used by the server

def get_token_and_port(nick: str, password: str, image: str, description: str,
                       nsfw: str) -> Tuple[str, int]:

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        s.sendall(pynetstring.encode("C MTP V:1.0"))
        print("-> C MTP V:1.0")

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

        d_token = data_channel(nick, password, int(port), token, image, description, nsfw)

        data = s.recv(1024)
        print("<-", data.decode("utf-8"))

        s.sendall(pynetstring.encode(f"C {d_token}"))
        print(f"-> C {d_token}")

        data = s.recv(1024)
        print("<-", data.decode("utf-8"))


def data_channel(nick: str, password: str, port: int, token: str, image: str,
                 description: str, nsfw: str) -> str:

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

        for data in req:
            s.sendall(pynetstring.encode(f"C {data}"))
            print(f"-> C {(data[:25] + '..') if len(data) > 25 else data}")

            check = s.recv(1024)
            print("<-", check.decode("utf-8"))
            if check.decode("utf-8").find(str(len(data))) == -1:
                s.sendall(pynetstring.encode("E Data doesn't match"))
                raise Exception("Data didn't match")
            
            responce = s.recv(1024)
            print("<-", responce.decode("utf-8"))

        return pynetstring.decode(responce)[0].decode("utf-8")[6:]


nick = input("Nick: ")
password = input("Password: ")
description = input("Description: ")
nsfw = input("NSFW (true/false): ")
while not nsfw in ["true", "false"]:
    print("Invalid input! 'true' or 'false' only")
    nsfw = input("NSFW (true/false): ")

get_token_and_port(nick, password, image, description, nsfw)
