import socket

HOST = "0.0.0.0"
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((HOST, PORT))

print("-------Service started---------")

received = set()

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()

    if message == "END":
        break
    seq = int (message)
    received.add(seq)

    print(f"收到数据包{seq}，来自{addr}")

lost = set(range(100)) - received

print("\n发送数据包：100")
print(f"收到数据包数：{len(received)}")
print(f"丢失数据包数：{len(lost)}")
print("--------service over----------")

if lost:
    print("lost package: ", sorted(lost))
else:
    print("No lost")
sock.close()