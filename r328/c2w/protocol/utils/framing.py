# -*- coding: utf-8 -*-
from c2w.protocol.utils.decode import decodeHeader

def framing(data):
    datagram=(b'',b'')
    if(len(data)>=4):
        header = decodeHeader(data)
        size = header.get("taille")
        if(len(data)>=size):
            datagram=(data[size:],data[0:size])
            return datagram
        else:
            datagram=(data,b'')
            return datagram
        
    else:
        datagram=(data,b'')
        return datagram