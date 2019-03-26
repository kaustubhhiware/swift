from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/home/mininet/shared", perm="elradfmwMT")
# authorizer.add_anonymous("/home/mininet/")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("10.0.0.5", 5555), handler)
server.serve_forever()