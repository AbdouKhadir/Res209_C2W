# -*- coding: utf-8 -*-
import struct



def decoder(message):

	dico={}
	dico["taille"]=(struct.unpack_from('!H',message))[0]
	seq_type=struct.unpack_from('!H',message,2)[0]
	dico["seq"]=(seq_type >> 6)
	dico["Type"]=(seq_type & 15)
	Type=(seq_type & 15)

	pass

	if Type==1: #Inscription

		usersize=dico.get("taille")-4
		dico["user"]=(struct.unpack_from('{0}s'.format(usersize),message,4))[0].decode('utf-8')
		return dico

	elif Type==2: #Liste films

		i=1
		currentsize=4
		while(currentsize<dico.get("taille")):
			dico["taille{0}".format(i)]=(struct.unpack_from('!B',message,currentsize))[0]
			ip1=struct.unpack_from('!B',message,currentsize+1)[0]
			ip2=struct.unpack_from('!B',message,currentsize+2)[0]
			ip3=struct.unpack_from('!B',message,currentsize+3)[0]
			ip4=struct.unpack_from('!B',message,currentsize+4)[0]
			dico["ip{0}".format(i)]="{0}.{1}.{2}.{3}".format(ip1, ip2, ip3, ip4)
			dico["port{0}".format(i)]=(struct.unpack_from('!H',message,currentsize+5))[0]
			dico["Id{0}".format(i)]=struct.unpack_from('!B',message,currentsize+7)[0]
			filmsize=dico.get("taille{0}".format(i))-8
			print(currentsize+8)
			dico["nom{0}".format(i)]=(struct.unpack_from('{0}s'.format(filmsize),message,currentsize+8)[0]).decode('utf-8')
			currentsize+=dico.get("taille{0}".format(i))
			i+=1
		return dico


	elif Type==3: #liste utilisateurs

		i=1
		currentsize=4
		while(currentsize<dico.get("taille")):
			dico["taille{0}".format(i)]=(struct.unpack_from('!B',message,currentsize))[0]
			dico["Id{0}".format(i)]=struct.unpack_from('!B',message,currentsize+1)[0]
			usersize=dico.get("taille{0}".format(i))-2
			dico["user{0}".format(i)]=struct.unpack_from('{0}s'.format(usersize),message,currentsize+2)[0].decode('utf-8')
			currentsize+=dico.get("taille{0}".format(i))
			i+=1
		return dico

	elif Type==4: #mise a jour utilisateur

		dico["Id"]=struct.unpack_from('!B',message,4)[0]
		usersize=dico.get("taille")-5
		dico["user"]=(struct.unpack_from('{0}s'.format(usersize),message,5))[0].decode('utf-8')
		return dico

	elif Type==5: #message de chat

		messagesize=dico.get("taille")-4
		dico["message"]=(struct.unpack_from('{0}s'.format(messagesize),message,4))[0].decode('utf-8')
		return dico

	elif Type==6: #joindre salon

		dico["Id"]=struct.unpack_from('!B',message,4)[0]
		return dico

	elif Type==8: #erreur inscription

		dico["erreur"]=struct.unpack_from('!B',message,4)[0]
		return dico

	elif Type==10: #redirection message instantané

		dico["size"]=struct.unpack_from('!B',message,4)[0]
		usersize=dico.get("size")
		dico["user"]=(struct.unpack_from('{0}s'.format(usersize),message,5))[0].decode('utf-8')
		messagesize=dico.get("taille")-5-dico.get("size")
		messagestart=5+dico.get("size")
		dico["message"]=(struct.unpack_from('{0}s'.format(messagesize),message,messagestart))[0].decode('utf-8')

		return dico


	elif (Type==7) | (Type==9) | (Type==11) | (Type==12) | (Type==13) : #regroupe tous les types de message n'envoyant que l'en tete (pas de data)

		return dico

