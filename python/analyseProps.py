# -*- coding: utf-8 -*-

import os
execfile('%s' % os.environ["PYTHON_LIBRARY"])

propsFile = sys.argv[0]
print ""
print "Fichier props : ",propsFile
print ""
print "Informations sur le serveur d applications"
print "------------------------------------------"
print ""


def loadFileContents(file):
	fichier=open(file, "r")
	index=0
	t_Ress={}
	global flagErreur
	flagErreur = 0

	#------ Liste des patterns ------
	saPattern = r'^SA_TRIG_NAME_TYPE=.*$'
	appliPattern = r'^APPLICATION=.*$'
	nodePattern = r'^SERVER_NODES=.*$'
	createSa = r'^CREATE_SA=.*$'
	ressPattern = r'^(url|ds|ree)[1-9][0-9]?.*$'
	entryPropName = r'^REE_ENTRY_PROP_NAME.*$'
	entryPropValue = r'^REE_ENTRY_PROP_VALUE.*$'
	realNameAppli = None

	for line in fichier.readlines():
		line = _noendcar(line)

		#------ Verification existence du SA et application ------
		if re.match(saPattern, line):
			sa = re.sub(r"SA_TRIG_NAME_TYPE=",r"",line)
			print "Serveur d applications : %s" % sa
			saId,node,appli = checkIfSAexists(sa)
			
			if appli is not None:
				module_appli = re.sub(r"(SA_)?(sa-)?(_app)?(_pres)?",r"",sa)
				print "Application : %s" % appli
			else:
				print "Aucune application n est installee pour le moment (en attente primo-deploiement)."
				module_appli = None
				realNameAppli = re.sub(r"(SA_)?(sa-)?(_app)?(_pres)?",r"",sa)
			
		if re.match(nodePattern, line):
			#------ Si le SA existe, on recupere le noeud sur lequel il est installe ------
			if node is None:
				node = re.sub(r"SERVER_NODES=",r"",line)
			print "Noeud : %s" % node
			print ""

		if re.match(createSa, line):
			create_sa = re.sub(r"CREATE_SA=",r"",line)

		#------- Identification des ressources (url,ds et ree) eventuelles ------
		if re.match(ressPattern, line):
			liste = line.split('=', 1)
			cle = liste[0].split('.')
			
			if cle[0] not in t_Ress.keys():
				t_Ress[cle[0]]={}
			t_Ress[cle[0]][cle[1]]=liste[1]
	
	if saId is None:
		if create_sa == "yes":
			print "Serveur d applications : %s inexistant" % sa
			print "Celui ci va etre cree avec les infos fournies dans le fichier props."
		else:
			sys.exit(2)

	print ""
	print "Informations sur les ressources : "
	print "--------------------------------"
	print ""

	for nomRess, attributs in t_Ress.items():
		typeRess = re.sub(r"[1-9][0-9]?.*$",r"",nomRess)

		# Operations on URL resources
		if typeRess == "url":
			action = t_Ress[nomRess]['URL_TYPE_ACTION']
			ressJndiName = t_Ress[nomRess]['URL_JNDI_APPLI']
			ressJndiWebName,idRess = getUrlRessId(saId,ressJndiName,realNameAppli,module_appli,appli)
			
			# APPLI Jndi specified on props found, binding with WEB Jndi OK
			if idRess and ressJndiWebName:
				print ""
				print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,ressJndiWebName)
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateUrlAction(idRess, nomRess, t_Ress)
				elif action == "delete":
					deleteAction(typeRess, idRess)
				elif action == "create":
					if module_appli:
						createUrl(node,sa,ressJndiName,nomRess,t_Ress,module_appli)
					else:
						createUrl(node,sa,ressJndiName,nomRess,t_Ress,realNameAppli)
			elif idRess and ressJndiWebName is None: # APPLI Jndi specified on props found, but no binding
				print ""
				print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,t_Ress[nomRess]['URL_JNDI_APPLI'])
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateUrlAction(idRess, nomRess, t_Ress)
				elif action == "delete":
					deleteAction(typeRess, idRess)
			else: # No APPLI Jndi
				if action == "create":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,ressJndiName)
					if module_appli:
						createUrl(node,sa,ressJndiName,nomRess,t_Ress,module_appli)
					else:
						createUrl(node,sa,ressJndiName,nomRess,t_Ress,realNameAppli)
				elif action == "view":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,ressJndiName)
					print "WARNING : la ressource jndi (%s) n est pas definie dans l application." % ressJndiName
				elif action == "delete":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,ressJndiName)
					print "WARNING : la ressource jndi (%s: %s) n est pas definie dans l application. Suppression ignoree." % (nomRess, ressJndiName)
				else:
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['URL_TYPE_ACTION'],nomRess,ressJndiName)
					print "ERROR : la ressource jndi (%s: %s) n est pas definie dans l application." % (nomRess, ressJndiName)
					flagErreur = 1
		# Operations on DATASOURCE resources
		elif typeRess == "ds":
			action = t_Ress[nomRess]['JDBC_TYPE_ACTION']
			ressJndiName =  t_Ress[nomRess]['JDBC_JNDI_APPLI']
			ressJndiWebName,idRess = getDbRessId(saId,ressJndiName,realNameAppli,module_appli,appli)

			# APPLI Jndi specified on props found, binding with WEB Jndi OK
			if idRess and ressJndiWebName:
				print ""
				print "[%s] %s: %s" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,ressJndiWebName)
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateDsAction(idRess, nomRess, t_Ress)
				elif action == "delete":
					deleteAction(typeRess, idRess)
				elif action == "create":
					if module_appli:
						createDs(node, sa, ressJndiName, nomRess, t_Ress, module_appli)
					else:
						createDs(node, sa, ressJndiName, nomRess, t_Ress, realNameAppli)
			elif idRess and ressJndiWebName is None: # APPLI Jndi specified on props found, but no binding
				print "[%s] %s: %s (%s)" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,AdminConfig.showAttribute(idRess,'jndiName'),t_Ress[nomRess]['JDBC_JNDI_APPLI'])
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateDsAction(idRess, nomRess, t_Ress)
				elif action == "delete":
					deleteAction(typeRess, idRess)
			else: # No APPLI Jndi
				if action == "create":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,ressJndiName)
					if module_appli:
						createDs(node, sa, ressJndiName, nomRess, t_Ress, module_appli)
					else:
						createDs(node, sa, ressJndiName, nomRess, t_Ress, realNameAppli)
				elif action == "view":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,ressJndiName)
					print "WARNING : la ressource jndi (%s)  est pas definie dans l application." % ressJndiName
				elif action == "delete":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,ressJndiName)
					print "WARNING : la ressource jndi (%s: %s) n est pas definie dans l application. Suppression ignoree." % (nomRess, ressJndiName)
				else:
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['JDBC_TYPE_ACTION'],nomRess,ressJndiName)
					print "ERROR : la ressource jndi (%s: %s) n est pas definie dans l application." % (nomRess, ressJndiName)
					flagErreur = 1
		# Operations on REE resources
		elif typeRess == "ree":
			action = t_Ress[nomRess]['REE_TYPE_ACTION']
			ressJndiName = t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI']
			ressJndiWebName,idRess = getReeRessId(saId,ressJndiName,realNameAppli,module_appli,appli)
		
			allProperties = {}
			for propertyName, propertyValue in attributs.items():
				if re.match(entryPropName, propertyName):
					indice = re.sub(r"^[a-zA-Z_]*",r"",propertyName)
					allProperties[propertyName] = [attributs['REE_ENTRY_PROP_NAME%s' % indice],attributs['REE_ENTRY_PROP_VALUE%s' % indice]]

			# APPLI Jndi specified on props found, binding with WEB Jndi OK
			if idRess and ressJndiWebName:
				print ""
				print "[%s] %s: %s" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,ressJndiWebName)
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateReeAction(idRess,ressJndiName,nomRess,allProperties,node,sa)
				elif action == "delete":
					deleteAction(typeRess, idRess)
				elif action == "create":
					if module_appli:
						createRee(node,sa,t_Ress[nomRess]['REE_FACTORY_NAME'],t_Ress[nomRess]['REE_CLASS_NAME'],ressJndiName,nomRess,allProperties,module_appli)
					else:
						createRee(node,sa,t_Ress[nomRess]['REE_FACTORY_NAME'],t_Ress[nomRess]['REE_CLASS_NAME'],ressJndiName,nomRess,allProperties,realNameAppli)
			elif idRess and ressJndiWebName is None: # APPLI Jndi specified on props found, but no binding
				print ""
				print "[%s] %s: %s (%s)" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,AdminConfig.showAttribute(idRess,'jndiName'),t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI'])
				if action == "view":
					viewAction(typeRess, idRess)
				elif action == "update":
					updateReeAction(idRess, ressJndiName, nomRess, allProperties, node, sa)
				elif action == "delete":
					deleteAction(typeRess, idRess)
			else: # No APPLI Jndi
				if action == "create":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI'])
					if module_appli:
						createRee(node,sa,t_Ress[nomRess]['REE_FACTORY_NAME'],t_Ress[nomRess]['REE_CLASS_NAME'],ressJndiName,nomRess,allProperties,module_appli)
					else:
						createRee(node,sa,t_Ress[nomRess]['REE_FACTORY_NAME'],t_Ress[nomRess]['REE_CLASS_NAME'],ressJndiName,nomRess,allProperties,realNameAppli)
				elif action == "view":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI'])
					print "WARNING : la ressource jndi (%s) n est pas definie dans l application." % ressJndiName
				elif action == "delete":
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI'])
					print "WARNING : la ressource jndi (%s: %s) n est pas definie dans l application. Suppression ignoree." % (nomRess, ressJndiName)
				else:
					print ""
					print "[%s] %s: %s" % (t_Ress[nomRess]['REE_TYPE_ACTION'],nomRess,t_Ress[nomRess]['REE_ENTRY_JNDI_APPLI'])
					print "ERROR : la ressource jndi (%s: %s) n est pas definie dans l application." % (nomRess, ressJndiName)
					flagErreur = 1

	if flagErreur == 0:
		#-------- Sauvegarde des modifications -------
		print ""
		print "Debut de la sauvegarde..."
		AdminConfig.save()
		time.sleep( 5 )
		print "Sauvegarde des modifications OK."

	        #------- Synchronisation des noeuds -------

		print ""
	        print "Synchronisation du noeud en cours..."
		if SyncNode(node):
			time.sleep( 20 )
                	print "Synchronisation du noeud OK."

	                #------- Arret / relance du serveur d applications -------

	                #stopServer(node,sa)
	                #startServer(node,sa)
		else:
                	print "Probleme rencontre lors de la tentative de synchronisation : synchro KO"
			sys.exit(10)
	else:
		print ""
               	print "Des problemes au niveau de certaines ressources ont ete rencontrees : pas de sauvegarde effectuee."
		sys.exit(3)
	fichier.close()

loadFileContents(propsFile)
