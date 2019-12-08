# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging
from c2w.protocol.utils.encode import encoder
from c2w.protocol.utils.decode import decoder
from c2w.protocol.utils.framing import framing
from c2w.main.constants import ROOM_IDS
from c2w.protocol.utils.userChat import userChat
from twisted.internet import reactor

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_server_protocol')


class c2wTcpChatServerProtocol(Protocol):

    def __init__(self, serverProxy, clientAddress, clientPort):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param clientAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param clientPort: The port number used by the c2w server,
            given by the user.

        Class implementing the TCP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: clientAddress

            The IP address of the client corresponding to this 
            protocol instance.

        .. attribute:: clientPort

            The port number used by the client corresponding to this 
            protocol instance.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.

        .. note::
            The IP address and port number of the client are provided
            only for the sake of completeness, you do not need to use
            them, as a TCP connection is already associated with only
            one client.
        """
        #: The IP address of the client corresponding to this 
        #: protocol instance.
        self.clientAddress = clientAddress
        #: The port number used by the client corresponding to this 
        #: protocol instance.
        self.clientPort = clientPort
        #: The serverProxy, which the protocol must use
        #: to interact with the user and movie store in the server.
        self.serverProxy = serverProxy
        self.fram = b''
        self.tailleHeader=4
        self.listUser={}
        self.user=None
    
    def sendAck(self, message): #envoyer un message d'acquittement
        """
        Takes in parameter:
        :param string message: the message received
        
        Used to send an acknolegment message when a message is received
        from a client
        """
        ack={}
        ack["taille"]=self.tailleHeader
        ack["Type"]=63
        
        numberSeq = message.get("seq")
        
        if (numberSeq == self.user.userSeq):
            
            ack["seq"]=message.get("seq")
            self.user.incrementeUserSeq()
            
        else:
            
            ack["seq"]=self.user.userSeq-1
            
        send=encoder(ack)
        
        self.transport.write(send)

        print("E nom {0} : {1}".format(self.user.name,ack))
        
    def addUser(self, name, message): 
        """
        Takes in parameters :
        :param string name: the username of the new user
        :param string message: the message received
    
        Used to add the user to the server.
        1) Username check :
            - not already used
            - less than 124 caracter
            - does not contain spaces
            
        2) Add the new user to the user list on the server in the MAIN ROOM
        """
        if (self.serverProxy.getUserByName(name)): #verifier si le nom d'utilisateur est deja utilise ou non sur la liste
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
         
        self.serverProxy.addUser(message.get("user"), ROOM_IDS.MAIN_ROOM, self, (self.user.host,self.user.port)) #si aucune des conditions n'est respectee, c'est que le nom peut etre utilise, on ajoute alors l'utilisateur a la liste
        dico={}
        dico["taille"]=self.tailleHeader
        dico["Type"]=7
        return dico
        
    def sendMessageToUserChat(self, message):
        """
        Takes in parameter :
        :param dict message:the message received
             
        Adds the message in the wainting list of the receiver.
        If this list contains only ONE message, the sendMessageToClient
        function if launched.
        """
        message["seq"]=self.user.serverSeq
        self.user.addMessage(message)
        if(len(self.user.message)==1):
            self.sendMessageToClient()
            
            
    def sendMessageToClient(self):
        """
        Sends the message to the concerned client and launchs the  
        sendAndWait function
        """
        
        message=self.user.message[0]
        message["seq"]=self.user.serverSeq
        send=encoder(message)
        print("E nom {0} : {1}".format(self.user.name,message))
        self.transport.write(send)
        self.user.idSend=reactor.callLater(1, self.sendAndWait)
        
    def sendAndWait(self):
        """            
        Sets the SendAndWait functionality : the message is sent every seconds 
        10 times
        """
        if(self.user.numberTransmission<10):
            
            send=encoder(self.user.message[0])
            print("E nom {0} : {1}".format(self.user.name,self.user.message[0]))
            self.transport.write(send)
            self.user.numberTransmission+=1
            self.user.idSend=reactor.callLater(1, self.sendAndWait)
            
        if(self.user.numberTransmission==10):
            
            self.user.idSend.cancel()
            self.deleteUser()
            
    def sendMovies(self, message):
        """
        Takes in parameter:
        :param dict message: the received message
        
        Function used to get the movies availables on the server and to send 
        them in a list to the newly connected client
        """
    
        movies=self.serverProxy.getMovieList() #recuperer la liste des films aupres du serveur 
        films={} #creatrion du dictionnaire a RENVOYER
        films["seq"]=message.get("seq")+1
        films["Type"]=2
        i=0
        taille=0
        
        while(i<len(movies)): #tant que l'on arrive pas a la fin de la liste des films
            
            films["ip{0}".format(i)]=movies[i].movieIpAddress #sur 4 octets
            films["port{0}".format(i)]=movies[i].moviePort #sur 1 octet
            films["Id{0}".format(i)]=movies[i].movieId #sur 1 octet
            films["nom{0}".format(i)]=movies[i].movieTitle #taille variable
            films["taille{0}".format(i)]=8+len(movies[i].movieTitle.encode('utf-8')) #inclu ip, port, id, nom et lui meme sur 2 octets
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
        utilisateurs={} #creatrion du dictionnaire a RENVOYER
        utilisateurs["Type"]=3
        i=0
        taille=0
        
        while(i<len(users)):  #tant que l'on arrive pas a la fin de la liste des utilisateurs
            
            utilisateurs["user{0}".format(i)]=users[i].userName #taille variable
            
            if(users[i].userChatRoom==ROOM_IDS.MAIN_ROOM): #si l'utilisateur est dans la main room ...
                
                utilisateurs["Id{0}".format(i)]=0 #l'id a envoyer est 0
                
            else: #sinon ...
                
                room=users[i].userChatRoom #on recupere l'id de la room dans lequel il se trouve
                movie=self.serverProxy.getMovieById(room)
                utilisateurs["Id{0}".format(i)]=movie.movieId #sur 1 octet
                
            utilisateurs["taille{0}".format(i)]=2+len(users[i].userName.encode('utf-8'))
            taille+=utilisateurs.get("taille{0}".format(i))
            i+=1
        utilisateurs["taille"]=self.tailleHeader+taille  
        
        return utilisateurs
        
    def updateUser(self,roomId):
        """
        Takes in parameter:
        :param int roomId : the new room's id where the client is now connected
        
        Used to update the status of a user : in which room he is or if he has left the application
        This message is sent to all the users connected
        """
        dicoUpdate={}
        userName=self.user.name #recuperer l'utisateur dont on doit envoyer le nouveau statut
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
    
            receiver=u.userChatInstance #on recupere l'instrance TCP pour cet utilisateur
            receiver.sendMessageToUserChat(dicoUpdate) #on envoie le dictionnaire a chaque client
    
    def messageToForward(self,message):
        """
        Takes in parameter:
        :param dict message: the received message
        
        Used to prepare the message which will be forwarded
        
        e.g : chat message
        """
        
        dicoToSend={}
        dicoToSend["Type"]=10
        dicoToSend["size"]=len(self.user.name.encode('utf-8'))
        dicoToSend["user"]=self.user.name
        dicoToSend["message"]=message
        dicoToSend["taille"]=self.tailleHeader+1+len(self.user.name.encode('utf-8'))+len(message.encode('utf-8'))
        
        return dicoToSend
    
    def gestionStream(self, movieId):
        """
        Takes in parameter:
        :param int movieId : the id of the movie which have to be started
        
        Used to start the streaming of a movie
        """
        
        self.serverProxy.startStreamingMovie(self.serverProxy.getMovieById(movieId).movieTitle)
        
    def deleteUser(self):
        """
        Used to delete a user on the server when this one 
        has totally left the application
        """
        
        if(self.serverProxy.getUserByAddress((self.user.host,self.user.port))):
            
            self.serverProxy.removeUser(self.user.name)
            self.updateUser(255) #id donné lorsqu'un utilisateur quitte la plateforme
            
    def receiverReady(self):
        """
        Used to increment the client's sequence number on the server. It means
        that the client is ready to receive another message from the server
        """
        
        if(self.user.error==0): #si le message de connexion ne contient pas d'erreur
            
            self.user.idSend.cancel() #on arrete le S&W
            self.user.delMessage() #on supprime le message de la liste des message a envoyer a l'utilisateur
            self.user.incrementeServerSeq() #on incremente le numero de sequence de cet utilisateur sur le serveur
            self.user.numberTransmission=1 #on réinitialise le numbre de transmissions
            
            if(len(self.user.message)>0): #si la la liste des messages a envoyer au client n'est pas vide
                
                self.sendMessageToClient() #on envoie le message suivant
                
        else: #sinon
            
            self.user.idSend.cancel()#on arrete le S&W           
            self.deleteUser()#on supprime l'utilisateur
            
    def forwardMessage(self, message):
        """
        Takes in parameter:
        :param dict message: the received message

        Used to send the message which will be forwarded
        
        e.g : chat message
        """
        
        idMovieSender=self.serverProxy.getUserByName(self.user.name).userChatRoom #recherche de l'id de la room dans laquelle se trouve l'utilisateur
        
        usersList=self.serverProxy.getUserList() #on recupere la liste des utilisateurs connectes au serveur
        receivers=[] #liste contenant les destinataires
        i=0
    
        while(i<len(usersList)): #tant que l'on arrive pas au bout de la liste des utilisateurs
            if(usersList[i].userChatRoom==idMovieSender): #si le destinataire est dans la meme room que l'emetteur
                receivers.append(usersList[i]) #on l'ajoute dans la liste des destinataires   
            i+=1
                
        for u in receivers: #pour chaque destinataire
            receiver=u.userChatInstance #on recupere l'instrance TCP pour cet utilisateur
            receiver.sendMessageToUserChat(message) #on envoie le dictionnaire a chaque client
                
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

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """
        self.fram+=data #on ajoute les donnees recues avec celles non utilisees que l'on avait precedemment 

        datagram=framing(self.fram) #permet de savoir s'il y a message complet
        #datagram est un est un tuple:
        # premier champ : données inutilisables
        # second champ : message complet ou vide
        
        if (datagram[1]!=b''): #s'il y a un message complet
            
            
            self.fram=datagram[0] #on stock les donnees inutilisables
            message = decoder(datagram[1]) #on decode le message
            print("R : {0}".format(message))
            if(self.serverProxy.getUserByAddress((self.clientAddress,self.clientPort))==None): #si l'utilisateur n'existe pas
                self.user=userChat(message.get("user"),(self.clientAddress, self.clientPort)) #on le crée
                
            Type = message.get("Type")
            Seq = message.get("seq")
        
            if Type == 63: #si le message est un acquittement
                
                if (Seq == self.user.serverSeq): #si le num de seq de l'ack est celui enregsitre sur le server
                    self.receiverReady() 
                    
            else: #si ce n'est pas un ack
                if Seq < self.user.userSeq: #si le num de seq recu est inferieur a celui du client enregsitre sur le serveur
                    self.sendAck(message) #on envoe un ack (=deja traite)
                
                else: #sinon
                    self.sendAck(message) #on envoie un ack avant traitement
                
                if Type==1: #si le message est une inscription
                    testAdding=self.addUser(message.get("user"), message) #on essaye d'ajouter l'utilisateur sur le serveur
                    if (len(testAdding) > 2): # si le retour contient un champ erreur en plus de l'entete
                    
                        self.user.error=1 #on place la variable error a 1 pour signifier qu'une erreur est survenue
                        self.sendMessageToUserChat(testAdding) #on le place dans la liste des message a envoyer a l'utilisateur
                        
                    else: #s'il n'y a pas d'erreur
                        
                        self.sendMessageToUserChat(testAdding) #on le place dans la liste des message a envoyer a l'utilisateur
                        movies=self.sendMovies(message) #recupere la liste des films
                        self.sendMessageToUserChat(movies) #on la place dans la liste des message a envoyer a l'utilisateur
                        users=self.sendUsers(message) #on recupere la liste des utilisateurs
                        self.sendMessageToUserChat(users) #on la place dans la liste des message a envoyer a l'utilisateur
                        self.updateUser(ROOM_IDS.MAIN_ROOM) #on actualise l'emplacement de l'utilisateur (il se trouve dans la main room)
                        
                if Type==5: #si le message est un message de chat
                    
                    messageToForward=self.messageToForward(message.get("message")) #on prepare le message a transferer
                    self.forwardMessage(messageToForward) #on transfere le message a tous les utilisateurs presents dans la main room
                    
                if Type==6: #si le message est une requete pour changer de room
                    okRoom = self.joinOKRoom(message) #on prepare a envoyer le message d'aceptation
                    self.sendMessageToUserChat(okRoom) #on le place dans la liste des message à envoyer à l'utilisateur
                    movieId=message.get("Id") #on recupere l'id de la nouvelle room
                    
                    if movieId==0: #s'il vaut 0
                        self.serverProxy.updateUserChatroom(self.user.name, ROOM_IDS.MAIN_ROOM) #on actualise le statut de l'utilisateur qui se trouve dans la main room
                        
                    else : #sinon  
                        self.serverProxy.updateUserChatroom(self.user.name, movieId) #on actualise le statut de l'utilisateur qui se trouve dans une movie room
                        
                    self.updateUser(movieId) #on actualise le statut
                    
                if Type==9: #si le message est une requete de deconnexion
                    
                    self.deleteUser() #on supprime l'utilisateur du serveur
        
        else: #sinon
            self.fram=datagram[0] #on stocke les donnes inutilisables pour la suite
            
        
        pass
