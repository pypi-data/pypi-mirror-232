

import socket

#
#	https://stackoverflow.com/a/36331860/2600905
#
def FIND_AN_OPEN_PORT ():
    with socket.socket () as SOCKET:
        SOCKET.bind (('', 0))
        return SOCKET.getsockname () [1]