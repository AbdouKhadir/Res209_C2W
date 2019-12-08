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
# -*- coding: utf-8 -*-
import struct


def decoder(datagram):
    mainDict={}
    length,seqType = struct.unpack_from('!HH',datagram,0)
    seq=seqType>>6
    Type=seqType & 63
    mainDict['taille']=length
    mainDict['sequence']=seq
    mainDict['Type']=Type
    #print(mainDict)
    if Type==1:#Inscription
         userName=struct.unpack_from('{0}s'.format(length-4),datagram,4)
         mainDict['user']=userName[0].decode("utf8")
         print(mainDict)
         return mainDict

    elif Type==2: #Liste films

        nbreOctetsDecodes=4
        i=1
        while nbreOctetsDecodes<length:
            size=struct.unpack_from('!B',datagram,nbreOctetsDecodes)[0]
            taille,ip1,ip2,ip3,ip4,port,Id,nom=struct.unpack_from('!BBBBBHB{0}s'.format(size-8),datagram, nbreOctetsDecodes)
            ip=str(str(ip1)+"."+str(ip2)+"."+str(ip3)+"."+str(ip4))
            mainDict['taille{0}'.format(i)]=taille
            mainDict['ip{0}'.format(i)]=ip
            mainDict['port{0}'.format(i)]=port
            mainDict['Id{0}'.format(i)]=Id
            mainDict['nom{0}'.format(i)]=nom.decode('utf8')
            nbreOctetsDecodes+=taille
            i+=1
        print(mainDict)
        return mainDict

    elif Type==3: #liste utilisateurs
        nbreOctetsDecodes=4
        i=1
        while nbreOctetsDecodes!=length:
            size=struct.unpack_from('!B',datagram,nbreOctetsDecodes)[0]
            taille,Id,nom=struct.unpack_from('BB{0}s'.format(size-2),datagram, nbreOctetsDecodes)
            mainDict['taille{0}'.format(i)]=taille
            mainDict['Id{0}'.format(i)]=Id
            mainDict['user{0}'.format(i)]=nom.decode('utf8')
            nbreOctetsDecodes+=taille
            i+=1
        #print(mainDict)
        return mainDict

    elif Type==4: #mise a jour utilisateur TEST VALIDE
        Id,userName=struct.unpack_from('B{0}s'.format(length-5),datagram,4)
        #print(Id, userName)
        mainDict["Id"]=Id
        mainDict["user"]=userName.decode("utf8")
        #print(mainDict)
        return mainDict

    elif Type==5:#message de chat TEST VALIDE
        message=struct.unpack_from('{0}s'.format(length-4),datagram,4)
        mainDict["message"]=message[0].decode("utf8")
        return mainDict

    elif Type==6:#joindre salon TEST VALIDE
        Id=struct.unpack_from('B',datagram,4)
        mainDict["Id"]=Id[0]
        #print(mainDict)
        return mainDict

    elif Type==8: # erreur inscription TEST VALIDE
        mainDict["erreur"]=struct.unpack_from('!B',datagram, 4)[0]
        return mainDict

    elif Type==10: #redirection message TEST VALIDE
        size=struct.unpack_from('!B',datagram,4)[0]
        user,message=struct.unpack_from('{0}s{1}s'.format(size, length-5-size),datagram,5)
        mainDict["size"]=size
        mainDict["user"]=user.decode("utf8")
        mainDict["message"]=message.decode("utf8")
        return mainDict

    elif (Type==7) | (Type==9) | (Type==11) | (Type==12) | (Type==13) : #regroupe tous les types de message n'envoyant que l'en tete (pas de data)
        #print(mainDict)
        return mainDict



