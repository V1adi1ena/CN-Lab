import socket
import sys

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "172.26.52.18"
SERVER_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(100):
    sock.sendto(
        str(i).encode(),
        (SERVER_IP, SERVER_PORT)
    )
    print(f"发送数据包 {i}")

sock.sendto(b"END", (SERVER_IP, SERVER_PORT))

print("发送完成")

sock.close()
