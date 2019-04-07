import io
import pickle
import psutil
import socket
import time

PORT = 8192

def make_and_send_message(msg_type, content, file_path, to, msg_socket, port):
    """
    """
    msg = message.Message(msg_type=msg_type, content=content, file_path=file_path)
    send_message(msg=msg, to=to, msg_socket=msg_socket, port=port)


def send_message(msg, to, msg_socket=None, port=PORT):
    """
    """
    if msg_socket is None:
        msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            msg_socket.connect((to, port))
        except OSError:
            # Raised if endpoint is already connected. No action is needed.
            pass

    msg.sender = msg_socket.getsockname()[0]
    msg_data = io.BytesIO(pickle.dumps(msg))

    try:
        while True:
            chunk = msg_data.read(BUFFER_SIZE)
            if not chunk:
                break
            msg_socket.send(chunk)
    except BrokenPipeError:
        pass

    try:
        msg_socket.shutdown(socket.SHUT_WR)
        msg_socket.close()
    except OSError:
        pass