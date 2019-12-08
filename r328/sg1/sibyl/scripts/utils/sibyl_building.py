# -*- coding: utf-8 -*-
import struct

def building(date,message):
    
    taille=4+2+len(message) #taille en octet
    buf=struct.pack('!IH{0}s'.format(len(message.encode('utf-8'))),date,taille,message.encode('utf-8')) #le ! permet d'éviter l'endianness (dire dans quel sens sont envoyés les int), ! = network-endian
    return buf
    pass

def decoding(datagram):

    #header=struct.unpack_from('IH',datagram) #récupération de la date et de la taille
    buf=struct.unpack_from('!IH{0}s'.format(struct.unpack_from('!IH',datagram)[1]-6),datagram) #décodage pour récupérer la question
    return buf
    pass
    
def header(datagram):
    buf=struct.unpack_from('!IH',datagram)
    return buf
    pass
    
