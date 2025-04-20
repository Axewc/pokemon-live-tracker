import socket

class MemoryClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))

    def read_memory(self, address: int, length: int) -> bytes:
        command = f"m{address:x},{length:x}\n".encode()
        self.sock.sendall(command)
        response = self.sock.recv(1024).strip()
        return bytes.fromhex(response.decode())

    def close(self):
        if self.sock:
            self.sock.close()