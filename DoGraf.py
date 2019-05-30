import os
import copy
import math
import numpy as np
import matplotlib.pyplot as plt
from configobj import ConfigObj

#from matplotlib.ticker import FormatStrFormatter

#Une as Specs no file com as Gerais (As dos files tem + prioridade)
#"s" sao as Specs individuais dos files
def unirSpecs(s,confTipoGrafico):
	""""Teste doc"""

	if "Specs" in confTipoGrafico:
		aux = copy.deepcopy(confTipoGrafico["Specs"])
		aux.update(s)
	else:
		aux = s
	return aux



#Calculamos qual é o valor que escrevemos no topo da tabela
# Para isso utilizamos os ticks do axis y
def	atualiza_value_tick(numero,yloc,yticks):

	for k in range(len(yloc) - 1):
		if (numero >= yloc[k]) and (numero < yloc[k + 1]):
			break
	#print(numero,"-> k : ",k, " yloc[k]: ", yloc[k],"e yloc[k + 1]: ", yloc[ k+1 ])
	#print(yloc[k + 1] == numero)
	
	#yticks[k] vai ser a base do valor

	#decimal = numero % 1

	#percentagem de barra no novo axis acima da base yloc[k]
	percentagem = (numero - yloc[k]) / (yloc[k+1] - yloc[k]) 

	# transformar a parte deciaml do nosso numero : 
	# (decimal * step entre o tick superior e inferior) + nosso novo valor = valor final

	numero = yticks[k] + (percentagem * (yticks[k+1] - yticks[k]) )

	#numero = yticks[k] + (percentagem * (yloc[k+1] - yloc[k]) )

	return numero




#Auxilio para yicks...
#Devolve a maior precisao de entre 2 numeros
# esses dois numeros sao o inicio dos yticks, e o step dos yticks
def maior_precisao(lista):

		if len(lista) == 0:
			start = 0
			step = 1
		elif len(lista) == 1:
			start = lista[0]
			step = 1
		else:
			start = lista[0]
			step = lista[2]


		string = str(start)
		if '.' in string:
				index = string.index('.')
				tam_start = len(string[index + 1:])
		else:
				tam_start = 0

		string = str(step)
		if '.' in string:		
				index = string.index('.')
				tam_step = len(string[index + 1:])
		else:
				tam_step = 0

		return max([tam_start, tam_step])


def resolve_precisao(lista,p):
	#Resolucaoo para o problema de precisao dos floats
	array = []
	for num in lista:

		#se o numero for decimal
		string = str(num)
		if '.' in string:
			index = string.index('.')
			tam = len(string[index + 1:])
			#vemos o tamanho da parte decimal
			#se o nosso numero tiver menor precisao, mantemo-la
			if tam < p: 
				num_trabalhado = "%.{0}lf".format(tam) % num
			else:
				num_trabalhado = "%.{0}lf".format(p) % num

			array.append( num_trabalhado )
		#é um inteiro
		else:
			array.append( num )

	return array



#TemBoool == False metemos +.txt (estamos a percorrer os ficheiros todos)
#TemBoool == True o file ja la tem .txt (estamos a percorrer o "Ficheiros")
def devolvePropriedades(ficheiros,dirFiles,TemBoool,confTipoGrafico):


	#Inicializamos
	if TemBoool == True:
		dirF = os.path.join(dirFiles,ficheiros[0])
	else:
		dirF = os.path.join(dirFiles,list(ficheiros.keys())[0] + ".txt")

	f = open(dirF,'r')
	data =  list(map( lambda x:float(x),f.read().split() )) 


	Ymax = max(data)
	Lmax = len(data)
	Freqmax = 0
	Ymin = min(data)

	listaDataFicheiros = []


	for fileName in ficheiros:
		if TemBoool == True:
			dirF = os.path.join(dirFiles,fileName)
		else:
			dirF = os.path.join(dirFiles,fileName + ".txt")

		f = open(dirF,'r')
		data =  list(map( lambda x:float(x),f.read().split() )) 

		values, counts = np.unique(data, return_counts = True)
		#print("values:",values)
		#print("counts:",counts)

		auxFreqmax = max(counts)
		auxYmax  = max(data)
		auxYmin  = min(data)
		auxL = len(data) 


		if auxFreqmax > Freqmax:
			Freqmax = auxFreqmax

		if auxYmin < Ymin:
			Ymin = auxYmin

		if auxYmax > Ymax:
			Ymax = auxYmax

		if auxL > Lmax:
			Lmax = auxL

		if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
			#Copia necessaria porque vamos mexer nesteta nova matriz
			listaDataFicheiros.append(data)

		f.close()


	return Ymin, Ymax + 0.10*Ymax, Lmax, Freqmax,listaDataFicheiros


#data: matriz de todos os ficheiros
def preparaArrayEmpilhado(maxL,numFiles,listaDataFicheiros):
	data = np.array(listaDataFicheiros)

	b = np.zeros( (numFiles,maxL) )
	for i in range(maxL):
		aux = np.sort(data[:,i])
		for j in range(numFiles):
			indice = list(aux).index(data[j,i])
			if(indice == 0):
				b[j,i] = 0
			else :
				b[j,i] = aux[indice -1]
	return b




def guardaGrafico(confTipoGrafico,dirImagens,folder_name,name):
	if not os.path.exists(os.path.join(dirImagens,folder_name[:-2])):
		os.makedirs(os.path.join(dirImagens,folder_name[:-2]))

	#nao é necessario
	#if ('separa' in confTipoGrafico and confTipoGrafico['separa'] == 'True'):



	#if ('substitui' in confTipoGrafico and confTipoGrafico['substitui'] == 'False'):
	if ('substitui' in confTipoGrafico and confTipoGrafico['substitui'] == 'False'):
		name = fileNameRepetido(os.path.join(dirImagens,folder_name[:-2]),name,'.png')
		if __debug__:
			print("Nao substitui*** e deixa com nome:"+name)
	plt.savefig(os.path.join(dirImagens,folder_name[:-2],name+'.png'))


def fileNameRepetido(Dir,name,ext):
	if not name+ext in  next(os.walk(Dir))[2]:
		return name
	j = 0
	while name+'-'+str(j)+ext in  next(os.walk(Dir))[2]:
		j+=1
	return name+'-'+str(j)



#s : copia dos Specs do file(se "SEPARA" == True) ou do grupo intersetado com o do file ("separa" == False)
#tipoGrafico: "Barras","Linhas",etc..
#i: (SEPARA ==F)é o numero da figura ;(SEPARA==T) é um sufixo para o nome do file do grafico
def formatacaoSpecs(s,folder_name,fileName,tipoGrafico,confTipoGrafico,grafs,i,maxY,maxL,Freqmax,numPilares):

	if __debug__:
		print('Formataçao de'+folder_name +':',s)
	
	if 'legend' in s:
		l = s.pop('legend')
		eval("plt.legend(**l)")


	
	if 'fileName' in s:
		if("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True"):
			grafName = s.pop('fileName')
			grafName = grafName + "(" + str(i) +")" 
		else:
			grafName = s.pop('fileName')

	elif ("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True"):
		grafName = fileName
	else:
		grafName = folder_name
	

	#Retiramos se existir 
	if "pinta" in s:
		s.pop("pinta")
	if "simbolos" in s:
		s.pop("simbolos")
	if "offset" in s:
		s.pop("offset")
	if "linhas" in s:
		s.pop("linhas")
	if "value" in s:
		s.pop("value")
	if "bins" in s:
		s.pop("bins")
	if "ylim_colocado" in s:
		s.pop("ylim_colocado")
	if "yticks_colocado" in s:
		s.pop("yticks_colocado")



	if "figure_size" in s:
		plt.gcf().set_size_inches( float(s["figure_size"][0]) ,float(s["figure_size"][1]) )
		s.pop("figure_size")




	#Limite dos Y's
	if "ylim" in s:
		plt.ylim(float(s["ylim"][0]),float(s["ylim"][1]) * 1.05 )
		s.pop("ylim")
		
		#assim, como podemos estar a chamar mais vezes a funcao "desenho" sabemos que ja atualizamos 
		# o ylim deste grafico 
		#s["ylim_colocado"] = "True"


	elif ("ylim_colocado" not in s) and ("ylim" not in s and ("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True")) or "ylim" not in s and ("ladoAlado"  in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True"):
		#ylim igual para todos o files da mesma folder,quando fazemos separa == T (ou ladoAlado == T) e o user nao tinha dito nada a respeito
		if tipoGrafico == grafs[0] or tipoGrafico == grafs[1] :
			if "yscale" in s and (s["yscale"] == "log" or s["yscale"] == "symlog"):
				plt.ylim(0.1,maxY * 1.05)
				print("CERTO")
			else:	
				plt.ylim(0,maxY * 1.05)
	




	#Linhas , Bar
	if tipoGrafico == grafs[1] or tipoGrafico == grafs[0]:

		#nao deixa meter ticks automaticos
		if "AutoxTicks" not in s or s["AutoxTicks"] == "True":

			#mete ticks automaticos
			if "xticks_custome" not in s:
				#s["xticks_custome"] = list(range( math.ceil(maxL) ))
				s["xticks_custome"] = "range("+ str(0) + "," + str( math.ceil(maxL) ) +")"

			#transforma em lista
			if type(s["xticks_custome"]) != list:
				aux = []
				aux.append(s["xticks_custome"])
				s["xticks_custome"] = aux


			# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"]
			#["range(10)"] ou ["range(0","10"]  
			if s["xticks_custome"][0][:5] == "range":
				# s["xticks_custome"] = ["range(0","10","2)]
				s["xticks_custome"][0] = s["xticks_custome"][0][6:] 
				# s["xticks_custome"] = ["0","10","2)]
				s["xticks_custome"][-1] = s["xticks_custome"][-1][:-1]
				# s["xticks_custome"] = ["0","10","2]
				s["xticks_custome"] = eval( "np.arange(" + ",".join(s["xticks_custome"]) + ')' )

			
				p = maior_precisao(s["xticks_custome"])
				s["xticks_custome"] = resolve_precisao(s["xticks_custome"],p)


			#mete ticks grafico junto
			if "xticks_custome" in s and ("ladoAlado" not in confTipoGrafico or confTipoGrafico["ladoAlado"] == "False"): 
				plt.xticks(range(len(s["xticks_custome"])),s["xticks_custome"])			
				s.pop("xticks_custome")

			#mete ticks no graficos ladoAlado
			elif "xticks_custome" in s and ("ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True"): 
	
				# if len(s["xticks_custome"]) < ( (i + 1) * numPilares):
				# 	s["xticks_custome"] = s["xticks_custome"]+["","","",""]
				

				#mete os ticks aos poucos em cada janela 
				plt.xticks(range(i*numPilares,numPilares+ i*numPilares),s["xticks_custome"][i*numPilares : numPilares+ i*numPilares])							 		
				s.pop("xticks_custome")

	#Hist
	elif tipoGrafico == grafs[2]:

		#nao deixa meter ticks automaticos
		if "AutoxTicks" not in s or s["AutoxTicks"] == "True":

			if "bins_aux" in s:
				plt.xticks(s["bins_aux"])


		if ("xticks_custome" in list(s.keys())): 

			#transforma em lista
			if type(s["xticks_custome"]) != list:
				aux = []
				aux.append(s["xticks_custome"])
				s["xticks_custome"] = aux


			# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"] 
			#["range(10)"] ou ["range(0","10"]  
			if s["xticks_custome"][0][:5] == "range":
				# s["xticks_custome"] = ["range(0","10","2)]
				s["xticks_custome"][0] = s["xticks_custome"][0][6:] 
				# s["xticks_custome"] = ["0","10","2)]
				s["xticks_custome"][-1] = s["xticks_custome"][-1][:-1]
				# s["xticks_custome"] = ["0","10","2]
				s["xticks_custome"] = eval( "np.arange(" + ",".join(s["xticks_custome"]) + ')' )

				p = maior_precisao(s["xticks_custome"])
				s["xticks_custome"] = resolve_precisao(s["xticks_custome"],p)


			plt.xticks(s["bins_aux"],s["xticks_custome"])			
			s.pop("xticks_custome")



		if "bins_aux" in s:
			s.pop("bins_aux")





			# if "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False":
			# 	step = s["xticks_custome"][1] - s["xticks_custome"][0]
			# 	x["xticks_custome"]

			# # xticks = [2,3,4,5,6,7]
			# if type(s["xticks_custome"])  == list:
				
			# 	#dava problema estranho: os ticks vinham todos para a esquerda
			# 	mini = min(s["xticks_custome"])
			# 	plt.xticks(range( len(s["xticks_custome"]) ), [ t + mini for t in s["xticks_custome"] ] )			
			# # xticks = range(0,10)
			# else:
			# 	plt.xticks(range( len(s["xticks"]) ),s["xticks"])	




	#Limites do X's
	if "xlim" in s:
		if "ladoAlado" not in confTipoGrafico or confTipoGrafico["ladoAlado"] == "False":
			plt.xlim(float(s["xlim"][0]),float(s["xlim"][1]))
			#print(float(s["xlim"][0]), "e tambem ",float(s["xlim"][1]))
		s.pop("xlim")



	if "xticks" in s:
		xt = s.pop("xticks")
		eval("plt.xticks(**xt)")

	if "yticks" in s:
		yt = s.pop("yticks")
		eval("plt.yticks(**yt)")


	#Deve aceitar grande parte dos parametros da decomentacao
	#Tentei fazer parametrizavel...
	for string in s:
		eval('plt.'+string+'("'+ s[string]+'")')
	

	return grafName



#s : copia dos Specs do file(se "SEPARA" == True) ou do grupo intersetado com o do file ("separa" == False)

def desenho(tipoGrafico,x,d,confTipoGrafico,i,numFiles,numPilares,s,fileName,minY,maxY,b):
	m = [ 'x', '<', 'o', '.']
	hat = ['/', '.','*','x', 'o','//', 'O' ]

	#---------Todos

	#autoLegendas
	if "legend" in s and "lable" not in d:
		d["label"] = fileName



	# Escala de Cinza
	if "pinta" in s:
		sp = s["pinta"]
		#Simbolos
		if "simbolos" in sp:
			if tipoGrafico == grafs[0]:
				m = sp["simbolos"]
			else:
				hat = sp["simbolos"]
		
		#cor
		if "fillColor" in sp:
			
			if sp["fillColor"] == "Black":
				rgb = np.zeros(3)
				rgbMult = 1
			else:
				rgb = np.ones(3)	
				rgbMult = -1

		#Simboloscor
		if "edgeColor" in sp:
			
			if sp["edgeColor"] == "Black":
				edg = np.zeros(3)
				edgMult = 1

			else:
				edg = np.ones(3)	
				edgMult = -1





	#Fazemos aqui ja o parse sobre a yscale e o yticks/yloc  para termos essa informacao
	# e a podermos usar caso sejam preciso colocar "values" no grafico

	#quando scale == Log ou symLog nao metemos yticks;
	#se o utilizador os tiver metido temos de fazer s.pop para nao dar erro na parte 
	# do codigo que esta a aceitar plt.[strings] genericas  
	if "yscale" in s and (s["yscale"] == "log" or s["yscale"] == "symlog"):
		if "yticks_custome" in s:
			print("[NOTA]Com scale != linear, yticks nao é aceite")
			s.pop("yticks_custome")
		if "yloc" in s:
			print("[NOTA]Com scale != linear, yloc nao é aceite")
			s.pop("yloc")

	elif "yloc" in s and "yticks_custome" not in s:
			print("[NOTA]Sem yticks, yloc nao é aceite")
			s.pop("yloc")

	#metemos yticks
	elif "yticks_custome" in  s  and ("yscale" not in s or s["yscale"] == "linear"): 


		#transforma em lista
		if type(s["yticks_custome"]) != list:
			aux = []
			aux.append(s["yticks_custome"])
			s["yticks_custome"] = aux


		# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"]  
		# Se ["range(10)"] ou ["range(0","10"]  
		if s["yticks_custome"][0][:5] == "range":
			# s["yticks_custome"] = ["range(0","10","2)]
			s["yticks_custome"][0] = s["yticks_custome"][0][6:] 
			# s["yticks_custome"] = ["0","10","2)]
			s["yticks_custome"][-1] = s["yticks_custome"][-1][:-1]
			# s["yticks_custome"] = ["0","10","2]
			s["yticks_custome"] = eval( "np.arange(" + ",".join(s["yticks_custome"]) + ')' )
			

			p = maior_precisao(s["yticks_custome"])

			s["yticks_custome"] = resolve_precisao(s["yticks_custome"],p)



		#yloc diz nos as localizacoes dos ticks
		#loc automatica
		if "yloc" not in s:
			plt.yticks(range(len(s["yticks_custome"])),s["yticks_custome"])			
			s.pop("yticks_custome")
			
			s["yticks_colocado"] = "True"

			#for u in plt.yticks()[1]:
			#	print(u)

		#loc do user
		else:
			#transforma em lista
			if type(s["yloc"]) != list:
				aux = []
				aux.append(s["yloc"])
				s["yloc"] = aux

			
			# ["1","2,"3","5","10"] ou ["range(10)"] ou ["range(0","10"]  
			if s["yloc"][0][:5] == "range":
				# s["yloc"] = ["range(0","10","2)]
				s["yloc"][0] = s["yloc"][0][6:] 
				# s["yloc"] = ["0","10","2)]
				s["yloc"][-1] = s["yloc"][-1][:-1]
				# s["yloc"] = ["0","10","2]
				s["yloc"] = eval( "np.arange(" + ",".join(s["yloc"]) + ')' )

			s["yloc"] = [ float(aux)  for aux in s["yloc"]] 
	

			plt.yticks(s["yloc"],s["yticks_custome"])			
			
			s.pop("yticks_custome")
			s.pop("yloc")
			s["yticks_colocado"] = "True"




	#-----------Linhas
	if tipoGrafico == grafs[0]:

		if "pinta" in s:
			sp = s["pinta"]
			#cor e simbolos andam ao mesmo tempo
			if sp["f"] == "1":

				d["color"] = rgb + (rgbMult)*( (i+1) * (1/(numFiles+1)) )  
				d["marker"] = m[ i% len(m)]


			#cor so muda quando acabam os simbolos
			elif sp["f"] == "2":


				# "j" é o numeor de vezes que usamos todos os simbolos
				d["marker"] = m[ i% len(m)]
				aux = 0
				j = i - len(m)
				while(j >= 0):
					j -= len(m)
					aux+=1
			        

				d["color"] = rgb + (rgbMult * ((aux + 1) * 1/(numFiles + 1)) ) 


		info = plt.plot(x,**d)

		# if "value" in s:
		# 	p = 1
		# 	fonts = 10
		# 	if "precisao" in s["value"]:
		# 		p = int(s["value"]["precisao"])

		# 	if "fontsize" in s["value"]:
		# 		fonts = int(s["value"]["fontsize"])


		# 	for j,valor in enumerate(x):
		# 		if valor == 0:
		# 			continue										  
		# 		plt.text( j, valor + (valor * 0.05), '%.{0}lf'.format(p) % float(valor), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))



	#-----------Barras
	elif tipoGrafico == grafs[1]:
		


		if "pinta" in s:
			sp = s["pinta"]
			#cor e simbolos andam ao mesmo tempo
			if sp["f"] == "1":

				if "edge" in sp and sp["edge"] == "solido":
					d["edgecolor"] = edg
				elif "edge" in sp and sp["edge"] == "gradiente":		
					d["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )
			
				d["color"] = rgb + (rgbMult)*(i * (1/numFiles) )  
				d["hatch"] = hat[ i% len(hat)]


			#cor so muda quando acabam os simbolos
			elif sp["f"] == "2":

				if "edge" in sp and sp["edge"] == "solido":
					d["edgecolor"] = edg
				elif "edge" in sp and sp["edge"] == "gradiente":		
					d["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )


				# "j" é o numeor de vezes que usamos todos os simbolos
				d["hatch"] = hat[ i% len(hat)]
				aux = 0
				j = i - len(hat)
				while(j >= 0):
					j -= len(hat)
					aux+=1
			        

				d["color"] = rgb + (rgbMult * (aux * 1/numFiles) ) 



		
		#plot junto lado a lado	
		if  "ladoAlado" in confTipoGrafico and confTipoGrafico['ladoAlado'] == 'True':


			if "width" not in d :
				w = 1/ numFiles - 0.1
				d["width"] = w
			else:
				d["width"] = float(d["width"])
			
			d["align"] = "edge"

			#off set em relacao ao lado esquerdo das barras
			if "offset" in s:
				if s["offset"] == "center": 
					offset = -1 * numFiles * d["width"] /2 
				elif s["offset"] == "right":
					offset = -1 * numFiles * d["width"]
				else:
					offset = float(s["offset"]) * -1
			else:
				offset = 0


			if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
				x = x - b[i]


			ini = 0 
			fim = numPilares
			for j in range(len(x)//numPilares) :
				#if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True" :
				#	plt.figure(i*j)
				#else:
				

				#for a in plt.yticks()[1]:
				#	print(a)


				if "yticks_colocado" in s:
					yl,yt = plt.yticks()
					plt.figure(j)
					plt.yticks(yl,yt)
				else:
					plt.figure(j)


				info = plt.bar(np.arange(ini,fim) + d["width"] * i + offset ,x[ini:fim],**d)
				ini += numPilares
				fim += numPilares
				
				#Mete linhas no bar
				# if "linhas" in s and s["linhas"] == "True":
				# 	dplot = {}
				# 	if "pinta" in s:
				# 		dplot["marker"] = m[ i% len(m) ]
				# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
				# 	plt.plot(x[ini:fim],**dplot)


				if "value" in s:
					p = 1
					fonts = 10
					if "precisao" in s["value"]:
						p = int(s["value"]["precisao"])

					if "fontsize" in s["value"]:
						fonts = int(s["value"]["fontsize"])


					ylim_max = plt.ylim()[1]
					ylim_min = plt.ylim()[0]
					if "ylim" in s:
						ylim_max = float(s[ylim[1]])
						ylim_min = float(s[ylim[0]])



					#valores normais
					if "yticks_colocado" not in s:

						for rect in info:
							height = rect.get_height()
							#if height == 0:
							if  height > ylim_max or height <= ylim_min:
								continue	

							plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

					#tem em consideracao os yloc e yticks
					else:
						yloc = plt.yticks()[0]
						# for u in plt.yticks()[1]:
						# 	print(u)


						yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

						for rect in info:
							height = rect.get_height()
							#if height == 0:
							if  height > ylim_max or height <= ylim_min:
								continue
		
							numero = atualiza_value_tick(height,yloc,yticks)

							plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))


			#ultima figura
			#verifica se tem de desenhar mais uma figura
			if  numPilares * (j + 1)  < len(x):
				j += 1		

				if "yticks_colocado" in s:
					yl,yt = plt.yticks()
					plt.figure(j)
					plt.yticks(yl,yt)
				else:
					plt.figure(j)

				aux = np.zeros( ((j+1) * numPilares) - len(x), dtype = int)
				x1 = np.concatenate((x,aux),axis = 0 )
				info = plt.bar(np.arange(ini,fim) + d["width"] *i + offset ,x1[ini:fim],**d)
				
				if "value" in s:
					p = 1
					fonts = 10
					if "precisao" in s["value"]:
						p = int(s["value"]["precisao"])

					if "fontsize" in s["value"]:
						fonts = int(s["value"]["fontsize"])

					ylim_max = plt.ylim()[1]
					ylim_min = plt.ylim()[0]
					if "ylim" in s:
						ylim_max = float(s[ylim[1]])
						ylim_min = float(s[ylim[0]])


					#valores normais
					if "yticks_colocado" not in s:

						for rect in info:
							height = rect.get_height()
							#if height == 0:
							if  height > ylim_max or height <= ylim_min:
								continue	

							plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

					#tem em consideracao os yloc e yticks
					else:
						yloc = plt.yticks()[0]
						#for u in plt.yticks()[1]:
						#	print(u)
						yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

						for rect in info:
							height = rect.get_height()
							#if height == 0:
							if  height > ylim_max or height <= ylim_min:
								continue
		
							numero = atualiza_value_tick(height,yloc,yticks)

							plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))



				#Mete linhas no bar
				# if "linhas" in s and s["linhas"] == "True":
				# 	dplot = {}
				# 	if "pinta" in s:
				# 	#	dplot["pinta"] = s["pinta"]
				# 	#desenho("Linhas",x[ini:fim],dplot,{},i,numFiles,numPilares,minY,maxY,{})
				# 		dplot["marker"] = m[ i% len(m) ]
				# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
				# 	plt.plot(x[ini:fim],**dplot)


			#devolde numero de figuras para guardar
			return j+1 



		#plot junto overlaping ou empilhados
		elif "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False" :

			if "alpha" not in confTipoGrafico:
				if "pinta" not in s:	
					d["alpha"] = 0.4
			
			if "width" in d:
				d["width"] = float(d["width"])

			if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
				x = x - b[i]
				d["bottom"] = b[i]

			info = plt.bar(np.arange(len(x)),x,**d)
		
			# if "linhas" in s and s["linhas"] == "True":
			# 	dplot = {}
			# 	if "pinta" in s:
			# 	#	dplot["pinta"] = s["pinta"]
			# 	#desenho("Linhas",x,dplot,{},i,numFiles,numPilares,minY,maxY,{})
			# 		dplot["marker"] = m[ i% len(m) ]
			# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
			# 	plt.plot(x,**dplot)	



			if "value" in s:
				p = 1
				fonts = 10
				if "precisao" in s["value"]:
					p = int(s["value"]["precisao"])

				if "fontsize" in s["value"]:
					fonts = int(s["value"]["fontsize"])
				
				ylim_max = plt.ylim()[1]
				ylim_min = plt.ylim()[0]
				if "ylim" in s:
					ylim_max = float(s[ylim[1]])
					ylim_min = float(s[ylim[0]])

				#valores normais
				if "yticks_colocado" not in s:
					for j,rect in enumerate(info):
						height = rect.get_height()

						#if height == 0:
						if  height > ylim_max or height <= ylim_min:
							continue	

						if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
							height += b[i][j]	

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

				#tem em consideracao os yloc e yticks
				else:
					yloc = plt.yticks()[0]
					#for u in plt.yticks()[1]:
					#	print(u)
					yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

					for j,rect in enumerate(info):
						height = rect.get_height()

						#if height == 0:
						if  height > ylim_max or height <= ylim_min:
							continue	

						if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
							height += b[i][j]	

						numero = atualiza_value_tick(height,yloc,yticks)

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))


		#plot grafs separados
		else:


			if "width" in d:
				d["width"] = float(d["width"])


			info = plt.bar(np.arange(len(x)),x,**d)

			# if "linhas" in s and s["linhas"] == "True":
			# 	dplot = {}
			# 	if "pinta" in s:
			# 	#	dplot["pinta"] = s["pinta"]
			# 	#desenho("Linhas",x,dplot,{},i,numFiles,numPilares,minY,maxY,{})
			# 		dplot["marker"] = m[ i% len(m) ]
			# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
			# 	plt.plot(x,**dplot)	

			if "value" in s:
				p = 1
				fonts = 10
				if "precisao" in s["value"]:
					p = int(s["value"]["precisao"])

				if "fontsize" in s["value"]:
					fonts = int(s["value"]["fontsize"])

				ylim_max = plt.ylim()[1]
				ylim_min = plt.ylim()[0]
				if "ylim" in s:
					ylim_max = float(s[ylim[1]])
					ylim_min = float(s[ylim[0]])

				#valores normais
				if "yticks_colocado" not in s:

					for rect in info:
						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height <= ylim_min:
							continue										  
						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

				#tem em consideracao os yloc e yticks
				else:

					yloc = plt.yticks()[0]
					#for u in plt.yticks()[1]:
					#	print(u)
					yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

					for rect in info:
						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height <= ylim_min:
							continue
	
						numero = atualiza_value_tick(height,yloc,yticks)

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))




	#------------Hist
	elif tipoGrafico == grafs[2] :

		if "alpha" not in confTipoGrafico:
			if "pinta" not in s:
				d["alpha"] = 0.5 
	


		if "width" in d:
			d["width"] = float(d["width"])


		#Bins------
		if "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False" :

			if "bins" in d:
				bins = d["bins"]
			elif "bins" in s:
				bins = s["bins"]
			else:
				#maximo e minimo deste grafico
				#bins = "range("+ str(min(x) - 1) + "," + str(max(x) + 3) +")"
				bins = "range("+ str(min(x) ) + "," + str(max(x) + 2) +")"

		else:	
			if "bins" in d:
				bins = d["bins"]
			elif "bins" in s:
				bins = s["bins"]
			else:
				#maximo e minimo de todos os graficos
				#bins =  "range("+ str(minY - 1) + "," + str(maxY + 2) +")"
				bins =  "range("+ str(minY ) + "," + str(maxY + 1) +")"


		#String -> list (bins = "range(10)" --> bins = ["range(10)"])
		if type(bins) != list:
			aux = []
			aux.append(bins)
			bins = aux


		
		if bins[0][:5] == "range":
			bins = bins.copy()

			# bins = ["range(0","10","2)]
			bins[0] = bins[0][6:] 
			# bins = ["0","10","2)]
			bins[-1] = bins[-1][:-1]
			# bins = ["0","10","2]
			d["bins"] = eval( "np.arange(" + ",".join(bins) + ")" )
		else:
			d["bins"] = bins
			print(d["bins"])
			d["bins"] = [ float(aux) for aux in d["bins"] ]

		#assim sabemos que bins o hist tem e podemos meter xticks
		s["bins_aux"] = d["bins"]



		#Cor -------
		if "pinta" in s:
			sp = s["pinta"]
			#cor e simbolos andam ao mesmo tempo
			if sp["f"] == "1":

				if "edge" in sp and sp["edge"] == "solido":
					d["edgecolor"] = edg
				elif "edge" in sp and sp["edge"] == "gradiente":		
					d["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )
			
				d["color"] = rgb + (rgbMult)*(i * (1/numFiles) )  
				d["hatch"] = hat[ i% len(hat)]


			#cor so muda quando acabam os simbolos
			elif sp["f"] == "2":

				if "edge" in sp and sp["edge"] == "solido":
					d["edgecolor"] = edg

				elif "edge" in sp and sp["edge"] == "gradiente":		
					d["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )



				# "j" é o numeor de vezes que usamos todos os simbolos
				d["hatch"] = hat[ i% len(hat)]
				aux = 0
				j = i - len(hat)
				while(j >= 0):
					j -= len(hat)
					aux+=1
			        

				d["color"] = rgb + (rgbMult * (aux * 1/numFiles) ) 


		elif "edgecolor" not in d:
			d["edgecolor"] = "black"




		info = plt.hist(x,**d)



		#Values-------

		#info[0] : frequencias
		#info[1] : bins
		if "value" in s:
			p = 1
			fonts = 10
			if "precisao" in s["value"]:
				p = int(s["value"]["precisao"])

			if "fontsize" in s["value"]:
				fonts = int(s["value"]["fontsize"])


			ylim_max = plt.ylim()[1]
			ylim_min = plt.ylim()[0]
			if "ylim" in s:
				ylim_max = float(s[ylim[1]])
				ylim_min = float(s[ylim[0]])


			offset_centro = info[1][1] - info[1][0]

			#mete values normalmente
			if "yticks_colocado" not in s:

				for j,valor in enumerate(info[0]):
					#se for "0" ou sair da figura nao desenhamos
					if valor == 0 or valor > ylim_max:
						continue										  
					plt.text( info[1][j] + offset_centro/2, (valor + 0.005), '%.{0}lf'.format(p) % float(valor), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

			#Toma em consideracao os yticks
			else:

				yloc = plt.yticks()[0]
				#for u in plt.yticks()[1]:
				#	print(u)
				yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

				for j,valor in enumerate(info[0]):
					#se for "0" ou sair da figura nao desenhamos
					if valor == 0 or valor > ylim_max or valor <= ylim_min :
						continue			

					numero = atualiza_value_tick(valor,yloc,yticks)

					plt.text( info[1][j] + offset_centro/2, (valor + 0.005), '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))


	#significa que so desenhamos uma figura
	return 0





#files: lista do nome de fixheiros (contem  a extensão .txt) na diretoria folder_name
#tipoGrafico: tipoGrafico a executar
# c é a parte do .conf que corresponde à pasta folder_name 
#folder name é o nome da diretoria dos ficheios (tem a extensao do .conf)
#nf numero da figura (queremos mai sque um graficos na ,mesma figura) (se for so para te rum unico
#	grafico o valor é 0)
def customAuxiliar(files,tipoGrafico,c,folder_name,dirFiles,dirImagens,grafs,nf):
	
	#util se nao tiver feito plt.close da janela que vinha antes
	#se fizer ladoAlado a janelas nao estao a ser fechadas
	#plt.figure()
	
	confTipoGrafico = c[tipoGrafico]

	if tipoGrafico == grafs[1] and 'numPilares' in confTipoGrafico: 
		numPilares = int(confTipoGrafico['numPilares'])
	else:
		numPilares = 4

	if("separa" in confTipoGrafico and confTipoGrafico["separa"] == "True" ) and "ladoAlado" in confTipoGrafico and confTipoGrafico['ladoAlado'] == 'True':
		print("[ERRO]Conflito nas Especificaçoes\nTem 'separa' e 'ladoAlado' no memsmo plot de Barras:"+folder_name+"\nLeaving")
		return

	elif ("empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True")  and "ladoAlado" in confTipoGrafico and confTipoGrafico['ladoAlado'] == 'True':
		print("[ERRO]Conflito nas Especificaçoes\nTem 'empilha' e 'ladoAlado' no memsmo plot de Barras:"+folder_name+"\nLeaving")
		return


	#indicador do numero de figuras que famos ter de guardar 
	#	nos LadoAlado (fora disso e sempre == 0)
	fig = 0

	#plot so de alguns ficheiros na diretoria
	if "Ficheiros" in confTipoGrafico:
		print("Ficheiros")
		d = confTipoGrafico["Ficheiros"]
	
		if __debug__:
			print("Files para o plot:",d.keys())

		minY,maxY,maxL,Freqmax,listaDataFicheiros = devolvePropriedades(d,dirFiles,False,confTipoGrafico)

		b = []
		if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
			b = preparaArrayEmpilhado(maxL,len(d),listaDataFicheiros)



		#ficheiros separados------------------------------

		if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True":
			if __debug__:
				print("SEPARADOS")
			for i,fileName in enumerate(d):
				dirF = os.path.join(dirFiles,fileName+'.txt')
				f = open(dirF,'r')
				data =  np.array( list(map( lambda x:float(x),f.read().split() )) )

				if __debug__:
					print("Data :",data)
					print('fmt :',d[fileName])
				
				if "Specs" in d[fileName]:
					#retiramos os specs, fazemos plot e fazemos formatacao deste grafico

					s = d[fileName].pop("Specs")
					s = unirSpecs(s,confTipoGrafico)
					desenho(tipoGrafico,data,d[fileName],confTipoGrafico,i,len(d),numPilares,s,fileName,minY,maxY,b)
					grafName = formatacaoSpecs(s,folder_name,fileName,tipoGrafico,confTipoGrafico,grafs,i,maxY,len(data),Freqmax,numPilares)
				elif "Specs" in confTipoGrafico:
					#fazemos a formataçao geral para todos
					#copia necessaria pois alterarmos os Specs na formatacaoSpecs
					s = copy.deepcopy(confTipoGrafico["Specs"])
					desenho(tipoGrafico,data,d[fileName],confTipoGrafico,i,len(d),numPilares,s,fileName,minY,maxY,b)
					grafName = formatacaoSpecs(s,folder_name,fileName,tipoGrafico,confTipoGrafico,grafs,i,maxY,len(data),Freqmax,numPilares)		
				else:
					#plot sem Specs
					grafName = folder_name
					desenho(tipoGrafico,data,d[fileName],confTipoGrafico,i,len(d),numPilares,{},fileName,minY,maxY,b)

				f.close()

				guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)
				plt.close()



		#ficheiros juntos------------------------------

		else:
			if __debug__:
				print("JUNTOS")



			for i,fileName in enumerate(d):
				dirF = os.path.join(dirFiles,fileName+'.txt')
				f = open(dirF,'r')
				data =  np.array( list(map( lambda x:float(x),f.read().split() )) )

				if __debug__:
					print("Data :",data)
					print('fmt :',d[fileName])

				if "Specs" in d[fileName]:
					#ignoramos Specs especificos se formos fazer plot dos files juntos
					d[fileName].pop("Specs")


				#copia necessaria pk s é alterado no desenho e naformataçao e 
				# o s que vai para o desenho tem de ser o mesmo que vai para a formatacao
				if "Specs" in confTipoGrafico:
					#s = confTipoGrafico["Specs"]
					s =  copy.deepcopy(confTipoGrafico["Specs"])
				else:
					s = {}

				faux = desenho(tipoGrafico,data,d[fileName],confTipoGrafico,i,len(d),numPilares,s,fileName,minY,maxY,b)
				#ficheiros maiores farem mais figuras (queremos guardar todas elas :) )
				if faux > fig :
					fig = faux


				f.close()

			#se no plot do Bar foi gerados + de 1 fig 

			#Barras LadoALado
			if fig != 0:
				
				for j in range(fig):


					plt.figure(j)
					if "Specs" in confTipoGrafico:
						grafName = formatacaoSpecs(copy.deepcopy(s),folder_name,"",tipoGrafico,confTipoGrafico,grafs,j,maxY,maxL,Freqmax,numPilares)
					
						grafName = grafName + "["+ str(j) +"]"
					else:
						grafName = folder_name + "["+ str(j)+"]"

					guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)
					#plt.clf()
					plt.close()

			else:
				if "Specs" in confTipoGrafico:
					grafName = formatacaoSpecs(s,folder_name,"",tipoGrafico,confTipoGrafico,grafs,0,maxY,maxL,Freqmax,numPilares)
				else:
					grafName = folder_name
				guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)					
				plt.close()


    #plot automatico de todos os files .txt ------------------------
	else:

		print("Total")

		minY,maxY,maxL,Freqmax,listaDataFicheiros = devolvePropriedades(files,dirFiles,True,confTipoGrafico)
	
		b = []
		if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
			b = preparaArrayEmpilhado(maxL,len(files),listaDataFicheiros)
		


		#Total separados
		if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True":

			if __debug__:
				print("SEPARADOS")
			

			for i,fileName in enumerate(files):
				dirF = os.path.join(dirFiles,fileName)
				f = open(dirF,'r')
				data =  np.array( list(map( lambda x:float(x),f.read().split() )) )


				#copia necessaria pk s é alterado no desenho e naformataçao e 
				# o s que vai para o desenho tem de ser o mesmo que vai para a formatacao
				if "Specs" in confTipoGrafico:
					#s = confTipoGrafico["Specs"]
					s =  copy.deepcopy(confTipoGrafico["Specs"])
				else:
					s = {}


				desenho(tipoGrafico,data,{},confTipoGrafico,i,len(files),numPilares,s,fileName[:-4],minY,maxY,b)

				f.close()

				if "Specs" in confTipoGrafico:
					#grafName = formatacaoSpecs(copy.deepcopy(s),folder_name,fileName[:-4],tipoGrafico,confTipoGrafico,grafs,i,maxY,len(data),Freqmax,numPilares)
					grafName = formatacaoSpecs(s,folder_name,fileName[:-4],tipoGrafico,confTipoGrafico,grafs,i,maxY,len(data),Freqmax,numPilares)
				else:
					grafName = fileName[:-4]

				guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)

				#importante para quando fazesmo graficos separados
				plt.close()


		#Total juntos -------------------------------------------
		else:
			if __debug__:
				print("JUNTOS")
					
			for i,fileName in enumerate(files):
				dirF = os.path.join(dirFiles,fileName)
				f = open(dirF,'r')
				data =  np.array( list(map( lambda x:float(x),f.read().split() )) )


				#copia necessaria pk s é alterado no desenho e naformataçao e 
				# o s que vai para o desenho tem de ser o mesmo que vai para a formatacao
				if "Specs" in confTipoGrafico:
					#s = confTipoGrafico["Specs"]
					s =  copy.deepcopy(confTipoGrafico["Specs"])
				else:
					s = {}


				faux = desenho(tipoGrafico,data,{},confTipoGrafico,i,len(files),numPilares,s,fileName[:-4],minY,maxY,b)
				#ficheiros maiores farem mais figuras (queremos guardar todas elas :) )
				if faux > fig :
					fig = faux


				f.close()


			if fig != 0:
				for j in range(fig):
					plt.figure(j)

					if "Specs" in confTipoGrafico:
						grafName = formatacaoSpecs(copy.deepcopy(s), folder_name,"",tipoGrafico,confTipoGrafico,grafs,j,maxY,maxL,Freqmax,numPilares)
						grafName = grafName + "["+str(j)+"]"
					else:
						grafName = folder_name + "["+str(j)+"]"

					guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)
					plt.close()
			else:
				if "Specs" in confTipoGrafico:
					grafName = formatacaoSpecs(s,folder_name,"",tipoGrafico,confTipoGrafico,grafs,0,maxY,maxL,Freqmax,numPilares)
				else:
					grafName = folder_name

				guardaGrafico(confTipoGrafico,dirImagens,folder_name,grafName)
				plt.close()











# c é a parte do .conf que corresponde à pasta folder_name 
#dirFiles é a diretoria que contêm ficheiros .txt
#dirImagens é a diretoria com os folder com o mesmo nome que dirFiles
#folder_name é o nome da diretoria no .conf
#grafs é a lista que contem o tipo de graficos
def custom(c,folder_name,dirFiles,dirImagens,grafs):
	'''
	Parameters
	----------
	----------


	:param str c: Description of parameter `c`.

	:type c: str
	:param c: `descricao doc`

	'''


	#Lista de ficheiros .txt no
	files = next(os.walk(dirFiles))[2]
	"""Docstring for class_variable."""


	if __debug__:
		print("Files in "+folder_name[:-2]+" :",files)

	#verifica se existem ficheiros de dados na diretoria
	if len(files) != 0:
		#plt.close nu final é para quando fazemso +1 que um grafico com files do mesmo folder ([Time.1] e [Time.2])
		#plot do grafico de--------Linhas
		if grafs[0] in c:
			print("fez linhas")
			customAuxiliar(files,grafs[0],c,folder_name,dirFiles,dirImagens,grafs,0)
			#plt.close()
		#plot do grafico de-------- Barras
		elif grafs[1] in c:
			print("fez bar")
			customAuxiliar(files,grafs[1],c,folder_name,dirFiles,dirImagens,grafs,0)
			#plt.close()
		#plot do grafico de ---------Histograma
		elif grafs[2] in c:
			print("fez hist")
			customAuxiliar(files,grafs[2],c,folder_name,dirFiles,dirImagens,grafs,0)
			#plt.close()
		#plot do grafico de--------Barras com Linhas
		# if grafs[3] in c:
		# 	print("fez Barras com linhas")
		# 	if "barras"  not in 
		# 	customAuxiliar(files,grafs[0],c,folder_name,dirFiles,dirImagens,grafs,1)
		# 	customAuxiliar(files,grafs[1],c,folder_name,dirFiles,dirImagens,grafs,1)
		# 	plt.close()








    
if __name__ =="__main__":
    
	dirData = os.path.join('..','data')
	dirImagens = os.path.join('..','imagens')
	grafs = ['Linhas','Barras','Hist']

	#Lista de todas as diretoriasque contem ficheiros de dados que vamos fazer plot
	#Ex: dataFolderList = ['barrasTeste', 'grafNoe', 'Nova pasta0', 'Nova pasta22', 'Time']
	dataFolderList = next(os.walk(dirData))[1]
	if not __debug__:
		print("DataFolderList:",dataFolderList)
    
	#Faz o parssing do ficheiro de configuracao 
	#Ex: C = {'Time.1': {'Linhas': {'Autoxticks': 'False', 'Ficheiros': {'timenewformulation0': 
	# {'color': '#0000ff', etc...
	c = ConfigObj(os.path.join('..',"graf.conf"))    


	#So faz plot das folder que estiveres assinaladas no .conf
	for folder_name in c:
		#Ao nome do folder retimamos os caracteres adicionais da chave
		#Ex: Time.1 -> Time  
		if folder_name[:-2] in dataFolderList:
			custom(c[folder_name],folder_name,os.path.join(dirData,folder_name[:-2]),dirImagens,grafs)





