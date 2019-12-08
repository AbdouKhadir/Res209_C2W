#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Serigne A.K. DIOUF
#
# Created:     28/04/2017
# Copyright:   (c) Serigne A.K. DIOUF 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import struct
encoder='abcdefghijklmnopqrstuvwxyz'.encode("utf8")
print(type(encoder))
coder=struct.pack('{}s'.format(len(encoder)),encoder)
print(type(coder))

coderNbre=struct.pack('BBBB',46,50,12,214)
decoder=struct.unpack_from('BBBB', coderNbre,0)
for elm in coderNbre:
    dof=hex(elm)
    print(dof, end='')
print('    ',decoder)
##for lettre in coderNbre:
##    print(hex(lettre), end='')
##print(coderNbre, decoder)
##for lettre in encoder:
##    kk=hex(lettre)
##    coder=coder+kk
##    print(kk, end='')
##print('')
##print(coder)
##decoder=encoder.decode("utf8")
##print(decoder)
