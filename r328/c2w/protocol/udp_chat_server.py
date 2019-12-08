# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
from c2w.protocol.utils.encode import encoder
from c2w.protocol.utils.decode import decoder
from c2w.main.constants import ROOM_IDS
from c2w.protocol.utils.userChat import userChat
from twisted.internet import reactor

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        self.tailleHeader=4
        self.listUser={}
        
    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
        
    def sendAck(self, message, user): #envoyer un message d'acquittement
        """
        Takes in parameter:
        :param string message: the message received
        :param string user: param user user: instance of the receiver user
        
        Used to send an acknolegment message when a message is received
        from a client
        """
        ack={}
        ack["taille"]=self.tailleHeader
        ack["Type"]=63
        
        numberSeq = message.get("seq")
        if (numberSeq == user.userSeq):
            ack["seq"]=message.get("seq")
            user.incrementeUserSeq()
        else:
            ack["seq"]=user.userSeq-1
        send=encoder(ack)
        print("E : {0}".format(ack))
        self.transport.write(send, (user.host, user.port))


    def addUser(self, name, message, user): #ajouter un nouvel utilisateur à la liste des utilisateurs utilisant l'application (cote serveur)
        """
        Takes in parameters :
        :param string name: the username of the new user
        :param string message: the message received
        :param user user: instance of the concerned user
    
        Used to add the user to the server.
        1) Username check :
            - not already used
            - less than 124 caracter
            - does not contain spaces
            
        2) Add the new user to the user list on the server in the MAIN ROOM
        """
        if (self.serverProxy.getUserByName(name)): #verifier si le nom d'utilisateur est dejà utilise ou non sur la liste
            dico={}
            dico["taille"]=self.tailleHeader+1
            dico["Type"]=8
            dico["erreur"]=1
            return dico #envoyer un message avec une erreur "1"
        
        if (len(name.encode('utf-8'))>124):  #verifier si le nom d'utilisateur ne depasse pas 124 caractères
            dico={}
            dico["taille"]=self.tailleHeader+1
            dico["Type"]=8
            dico["erreur"]=2 #envoyer un message avec une erreur "2"
            return dico
            
        if (" " in name): #verifier si le nom d'utilisateur contient des espaces
            dico={}
            dico["taille"]=self.tailleHeader+1
            dico["Type"]=8
            dico["erreur"]=3 #envoyer un message avec une erreur "3"
            return dico
            
        self.serverProxy.addUser(message.get("user"), ROOM_IDS.MAIN_ROOM, None,(user.host,user.port)) #si aucune des conditions n'est respectee, c'est que le nom peut etre utilise, on ajoute alors l'utilisateur à la liste
        dico={}
        dico["taille"]=self.tailleHeader
        dico["Type"]=7
        return dico
        
        
    def sendMessageToUserChat(self, message, user):
        """
        Takes in parameters :
        :param dict message: the received message
        :param user user: instance of the concerned user
            
        Adds the message in the wainting list of the receiver.
        If this list contains only ONE message, the sendMessageToClient
        function if launched.
        """
        message["seq"]=user.serverSeq
        user.addMessage(message)
        if(len(user.message)==1):
            self.sendMessageToClient(user)
            
            
    def sendMessageToClient(self, user):
        """
        Takes in parameters :
        :param user user: instance of the concerned user
        
        Sends the message to the concerned client and launchs the  
        sendAndWait function
        """
        message=user.message[0]
        message["seq"]=user.serverSeq
        send=encoder(message)
        print("E nom {0} : {1}".format(user.name,message))
        self.transport.write(send, (user.host,user.port))
        user.idSend=reactor.callLater(1, self.sendAndWait, user)
        
    
    def sendAndWait(self, user):
        """
        Takes in parameter :
        :param user user: instance of the concerned user
            
        Sets the SendAndWait functionality : it sends the message 10 times,
        every seconds
        
        """
        if(user.numberTransmission<10):
            send=encoder(user.message[0])
            print("E nom {0} : {1}".format(user.name,user.message[0]))
            #print("E : {0}".format(user.message[0]))
            self.transport.write(send, (user.host, user.port))
            user.numberTransmission+=1
            user.idSend=reactor.callLater(1, self.sendAndWait, user)
        if(user.numberTransmission==10):
            print("salut : {0}".format(user.name))
            user.idSend.cancel()
            self.deleteUser(user)
            
            
    def sendMovies(self, message):
        """
        Takes in parameter:
        :param dict message: the received message
        
        Function used to get the movies availables on the server and to send 
        them in a list to the newly connected client
        """
        movies=self.serverProxy.getMovieList() #recuperer la liste des films aupres du serveur 
        films={} #creatrion du dictionnaire à RENVOYER
        films["seq"]=message.get("seq")+1
        films["Type"]=2
        i=0
        taille=0
        while(i<len(movies)):
            films["ip{0}".format(i)]=movies[i].movieIpAddress #sur 4 octets
            films["port{0}".format(i)]=movies[i].moviePort #sur 1 octet
            films["Id{0}".format(i)]=movies[i].movieId #sur 1 octet
            films["nom{0}".format(i)]=movies[i].movieTitle #taille variable
            films["taille{0}".format(i)]=8+len(movies[i].movieTitle) #inclu ip, port, id, nom et lui meme sur 2 octets
            taille+=films.get("taille{0}".format(i))
            i+=1
            
        films["taille"]=self.tailleHeader+taille
        return films
        
    def sendUsers(self,message):
        """
        Takes in parameter:
        :param dict message: the received message
        
        Function used to get the users connected on the server and to send 
        them in a list to the newly connected client
        """
        
        users=self.serverProxy.getUserList()#recuper la liste des utilisateurs 
        utilisateurs={} #creatrion du dictionnaire à RENVOYER
        utilisateurs["seq"]=message.get("seq")+2
        utilisateurs["Type"]=3
        i=0
        taille=0
        
        while(i<len(users)): #tant que l'on arrive pas a la fin de la liste des utilisateurs
            utilisateurs["user{0}".format(i)]=users[i].userName #taille variable
            if(users[i].userChatRoom==ROOM_IDS.MAIN_ROOM): #si l'utilisateur est dans la main room ...
                utilisateurs["Id{0}".format(i)]=0 #l'id a envoyer est 0
            
            else:#sinon ...
                room=users[i].userChatRoom #on recupere l'id de la room dans lequel il se trouve
                print("roooooooooooooooooooom : {0}".format(room))
                movie=self.serverProxy.getMovieById(room)
                utilisateurs["Id{0}".format(i)]=movie.movieId #sur 1 octet
            utilisateurs["taille{0}".format(i)]=2+len(users[i].userName.encode('utf-8'))
            taille+=utilisateurs.get("taille{0}".format(i))
            i+=1
        utilisateurs["taille"]=self.tailleHeader+taille        
        return utilisateurs
        
    def updateUser(self,user,roomId):
        """
        Takes in parameter:
        :param user user: instance of the concerned user
        :param int roomId : the new room's id where the client is now connected
        
        Used to update the status of a user : in which room he is or if he has left the application
        This message is sent to all the users connected
        """
        dicoUpdate={}
        userName=user.name #recuperer l'utisateur dont on doit envoyer le nouveau statut
        dicoUpdate["seq"]=0
        dicoUpdate["Type"]=4
        dicoUpdate["taille"]=4+1+len(userName.encode('utf-8'))
        dicoUpdate["user"]=userName
        
        if(roomId==ROOM_IDS.MAIN_ROOM): #si l'utilisateur est dans la main room
            dicoUpdate["Id"]=0 # l'id vaut 0
        
        else: #sinon...
            dicoUpdate["Id"]=roomId #il vaut l'id passé en parametre

        allUsers=self.serverProxy.getUserList() #recuperation de la liste des utilisateurs connectes
        
        for u in allUsers: #pour chacun des utilisateurs de la liste:
            receiver=self.listUser.get("{0}".format(u.userAddress)) #on recupere l'instrance TCP pour cet utilisateur
            self.sendMessageToUserChat(dicoUpdate, receiver) #on envoie le dictionnaire a chaque client

            
    def messageToForward(self,message,user):
        """
        Takes in parameter:
        :param dict message: the received message
        :param user user: instance of the concerned user
        
        Used to prepare the message which will be forwarded
        
        e.g : chat message
        """
        dicoToSend={}
        dicoToSend["Type"]=10
        dicoToSend["size"]=len(user.name.encode('utf-8'))
        dicoToSend["user"]=user.name
        dicoToSend["message"]=message
        dicoToSend["taille"]=self.tailleHeader+1+len(user.name.encode('utf-8'))+len(message.encode('utf-8'))
        return dicoToSend
    
    def gestionStream(self, movieId):
        """
        Takes in parameter:
        :param int movieId : the id of the movie which have to be started
        
        Used to start the streaming of a movie
        """
        
        self.serverProxy.startStreamingMovie(self.serverProxy.getMovieById(movieId).movieTitle)
        
    def deleteUser(self, user):
        """
        Takes in parameter:
        :param user user: instance of the concerned user
        
        Used to delete a user on the server when this one 
        has totally left the application
        """
        
        if(self.serverProxy.getUserByAddress((user.host,user.port))):
            self.serverProxy.removeUser(user.name)
            self.updateUser(user,255) #id donné lorsqu'un utilisateur quitte la plateforme
            del self.listUser["{}".format((user.host,user.port))]
        else:
            del self.listUser["{}".format((user.host,user.port))]
            print(self.listUser)
    
    def receiverReady(self, user):
        """
        Takes in parameter:
        :param user user: instance of the concerned user
        
        Used to increment the client's sequence number on the server. It means
        that the client is ready to receive another message from the server
        """
        if(user.error==0): #si le message de connexion ne contient pas d'erreur
            user.idSend.cancel()  #on arrete le S&W
            user.delMessage() #on supprime le message de la liste des message a envoyer a l'utilisateur
            user.incrementeServerSeq() #on incremente le numero de sequence de cet utilisateur sur le serveur
            user.numberTransmission=1 #on réinitialise le numbre de transmissions
            
            if(len(user.message)>0): #si la la liste des messages a envoyer au client n'est pas vide
                self.sendMessageToClient(user) #on envoie le message suivant
            
        else: #sinon
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
            print(user.idSend)
            user.idSend.cancel() #on arrete le S&W           
            self.deleteUser(user) #on supprime l'utilisateur
            
    def forwardMessage(self, message, user):
        """
        Takes in parameter:
        :param dict message: the received message
        :param user user: instance of the concerned user

        Used to send the message which will be forwarded
        
        e.g : chat message
        """
        
        idMovieSender=self.serverProxy.getUserByName(user.name).userChatRoom#recherche de l'id de la room dans laquelle se trouve l'utilisateur
        usersList=self.serverProxy.getUserList()  #on recupere la liste des utilisateurs connectes au serveur
        receivers=[] #liste contenant les destinataires
        i=0
        while(i<len(usersList)): #tant que l'on arrive pas au bout de la liste des utilisateurs
            if(usersList[i].userChatRoom==idMovieSender): #si le destinataire est dans la meme room que l'emetteur
                receivers.append(usersList[i]) #on l'ajoute dans la liste des destinataires  
            i+=1
        
        for u in receivers: #pour chaque destinataire
            receiver=self.listUser.get("{0}".format(u.userAddress)) #on recupere l'instrance TCP pour cet utilisateur
            self.sendMessageToUserChat(message, receiver)#on envoie le dictionnaire a chaque client
                
    def joinOKRoom(self, message):
        """
        Takes in parameter:
        :param dict message: the received message
        
        Used to prepare the message which is sent to accept that a user has
        changed of room
        
        """
        
        dicoToSend={}
        dicoToSend["Type"]=11
        dicoToSend["taille"]=4
        return dicoToSend
    
        
    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        
        message = decoder(datagram) #on decode le message reçu
        print("\nR : {0}".format(message))
        
        if(self.listUser.get("{}".format(host_port))==None): #si l'utilisateur n'existe pas
            self.listUser["{}".format(host_port)]=userChat(message.get("user"),host_port) #on le crée
        
        user = self.listUser.get("{0}".format(host_port))
        Type = message.get("Type")
        Seq = message.get("seq")
        
        if Type == 63: #si le message est un acquittement
          if (Seq == user.serverSeq): #si le num de seq de l'ack est celui enregsitre sur le server
              self.receiverReady(user)
        
        else:#si ce n'est pas un ack
            if Seq < user.userSeq: #si le num de seq recu est inferieur a celui du client enregsitre sur le serveur
                self.sendAck(message, user) #on envoe un ack (=deja traite)
            
            else: #sinon
                self.sendAck(message, user) #on envoie un ack avant traitement
                
                if Type==1:  #si le message est une inscription
                    print(message.get("user"))
                    testAdding=self.addUser(message.get("user"), message, user)#on essaye d'ajouter l'utilisateur sur le serveur
                    if (len(testAdding) > 2): # si le retour contient un champ erreur en plus de l'entete
                        user.error=1  #on place la variable error a 1 pour signifier qu'une erreur est survenue
                        self.sendMessageToUserChat(testAdding, user) #on le place dans la liste des message a envoyer a l'utilisateur
                    
                    else: #s'il n'y a pas d'erreur
                        self.sendMessageToUserChat(testAdding, user)#on le place dans la liste des message a envoyer a l'utilisateur
                        movies=self.sendMovies(message)#recupere la liste des films
                        self.sendMessageToUserChat(movies, user)#on la place dans la liste des message a envoyer a l'utilisateur
                        users=self.sendUsers(message)#on recupere la liste des utilisateurs
                        self.sendMessageToUserChat(users, user)#on la place dans la liste des message a envoyer a l'utilisateur
                        self.updateUser(user,ROOM_IDS.MAIN_ROOM) #on actualise l'emplacement de l'utilisateur (il se trouve dans la main room)
                
                if Type==5: #si le message est un message de chat
                    messageToForward=self.messageToForward(message.get("message"), user)#on prepare le message a transferer
                    self.forwardMessage(messageToForward, user)#on transfere le message a tous les utilisateurs presents dans la main room
                    
                if Type==6: #si le message est une requete pour changer de room
                    okRoom = self.joinOKRoom(message)#on prepare a envoyer le message d'aceptation
                    self.sendMessageToUserChat(okRoom, user) #on le place dans la liste des message à envoyer à l'utilisateur
                    movieId=message.get("Id")#on recupere l'id de la nouvelle room
                    if movieId==0: #s'il vaut 0
                        self.serverProxy.updateUserChatroom(user.name, ROOM_IDS.MAIN_ROOM)#on actualise le statut de l'utilisateur qui se trouve dans la main room
                    
                    else: #sinon
                        self.serverProxy.updateUserChatroom(user.name, movieId) #on actualise le statut de l'utilisateur qui se trouve dans une movie room   
                        
                    self.updateUser(user,movieId) #on actualise le statut
                    
                if Type==9: #si le message est une requete de deconnexion
                    self.deleteUser(user) self.deleteUser() #on supprime l'utilisateur du serveur
                    

        pass
