# -*- coding: utf-8 -*-
import struct

def encoder(dictionnaire): #les differents champs d'un paquet sont passees sous forme de dictionnaire cle:valeur
    #print("\ndictionnaire recu pour encodage:{0}".format(dictionnaire))
    ##############################################################
    #                        ENCODAGE EN TETE                     #
    ##############################################################
    taille=dictionnaire.get("taille")  #recup taille totale paquet
    seq=dictionnaire.get("seq") # recup num seq paquet
    Type=dictionnaire.get("Type") #recup type message
    seq_type=(seq << 6) | Type #concatenation seq et type 

    buf_header=struct.pack('!HH',taille,seq_type) #codage en tete en binaire
    
    ##############################################################
    #                        ENCODAGE CORPS MESSAGE                  #
    ##############################################################
    
    if Type==1: #Inscription
        
        user=dictionnaire.get("user").encode('utf-8')
        buf=struct.pack('{0}s'.format(len(user)),user)
        total_buf=buf_header+buf
        return total_buf
                
    elif Type==2: #Liste films
        i=0
        movie_buf=b''
        while(dictionnaire.get("taille{0}".format(i))): #tant qu'il y a des champ sous la forme tailleX ...
            size=dictionnaire.get("taille{0}".format(i))
            ip=dictionnaire.get("ip{0}".format(i)) #recuperer l'adresse IP sous forme string
            ip_cut=ip.split('.') #separer chaque octet de l'IP
            port=dictionnaire.get("port{0}".format(i))
            Id=dictionnaire.get("Id{0}".format(i))
            nom=(dictionnaire.get("nom{0}".format(i))).encode('utf-8')    
            buf=struct.pack('!BBBBBHB{0}s'.format(len(nom)),int(size),int(ip_cut[0]),int(ip_cut[1]),int(ip_cut[2]),int(ip_cut[3]),int(port),int(Id),nom)
            movie_buf=movie_buf+buf
            i+=1
        total_buf=buf_header+movie_buf
        return total_buf
            
    elif Type==3: #liste utilisateurs
        i=0
        user_buf=b''
        while(dictionnaire.get("taille{0}".format(i))):
            size=dictionnaire.get("taille{0}".format(i))
            Id=dictionnaire.get("Id{0}".format(i))
            user=dictionnaire.get("user{0}".format(i)).encode('utf-8')        
            buf=struct.pack('BB{0}s'.format(len(user)),int(size),int(Id),user)
            user_buf=user_buf+buf
            i+=1
        total_buf=buf_header+user_buf
        return total_buf
        
    elif Type==4: #mise a jour utilisateur
        Id=dictionnaire.get("Id")
        user=dictionnaire.get("user").encode('utf-8')    
        buf=struct.pack('B{0}s'.format(len(user)),int(Id),user)
        total_buf=buf_header+buf
        return total_buf
        
    elif Type==5: #message de chat
        message=dictionnaire.get("message").encode('utf-8')
        buf=struct.pack('{0}s'.format(len(message)),message)
        total_buf=buf_header+buf
        return total_buf
        
    elif Type==6: #joindre salon
        Id=dictionnaire.get("Id")
        buf=struct.pack('B',Id)
        total_buf=buf_header+buf
        return total_buf
        
    
    elif Type==8: #erreur inscription
        erreur=dictionnaire.get("erreur")
        buf=struct.pack('B',erreur)
        total_buf=buf_header+buf
        return total_buf
                
    elif Type==10: #redirection message instantané
        size=dictionnaire.get("size")
        user=dictionnaire.get("user").encode('utf-8')
        message=dictionnaire.get("message").encode('utf-8')
        buf=struct.pack('B{0}s{1}s'.format(len(user),len(message)),size,user,message)
        total_buf=buf_header+buf
        return total_buf
        
    elif (Type==7) | (Type==9) | (Type==11) | (Type==12) | (Type==63) : #regroupe tous les types de message n'envoyant que l'en tete (pas de data)
        total_buf=buf_header
        return total_buf
    

    
