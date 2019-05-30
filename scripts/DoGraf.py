""" 
Faz o parssing de um ficheiro "graf.conf e gera e guarda graficos de varios plots 
"""
import os
import copy
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from configobj import ConfigObj



def unirSpecs(especificacoes, confTipoGrafico):
	"""
	Une as Specs especificas do ficheiro com as Gerais (As especificações dos ficheiros tem + prioridade)
	"especificacoes" sao as Specs individuais dos files

	:type especificacoes: dict
	:param especificacoes: especificações individuais dos ficheiros

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:returns: ``especificacoes``, caso nao existam ``Specs`` em ``confTipoGrafico``.
		``aux``, sendo ``aux`` uma copia das Specs Gerais que foi atualizada com as especificações do grafico 

	"""

	if "Specs" in confTipoGrafico:
		aux = copy.deepcopy(confTipoGrafico["Specs"])
		aux.update(especificacoes)
	else:
		aux = especificacoes
	return aux




def	atualiza_value_tick(numero, yloc, yticks):
	"""
	Calculamos qual é o valor que escrevemos no topo da barra do ``plt.bar`` ou ``plt.hist``

	:type numero: float
	:param numero: numero a transformar 

	:type yloc: list of float
	:param yloc: localização dos ticks do axis-y

	:type yticks: list of float
	:param yticks: valores dos ticks do axis-y

	:returns: novo valor para o numero
	"""


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





def maior_precisao(lista):
	"""
	Auxilio para yicks...
	
	Devolve a maior precisao de entre o inicio dos yticks, e o step dos yticks
	
	:type lista: ``numpy arange()``
	:param lista:  lista de valores (x-axis ou y-axis)

	:return: Devolve maior precisao de entre o inicio dos yticks, e o step dos yticks
	"""

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
	#se for float
	if '.' in string:
			index = string.index('.')
			tam_start = len(string[index + 1:])
	#se for int
	else:
			tam_start = 0

	string = str(step)
	#se for float
	if '.' in string:		
			index = string.index('.')
			tam_step = len(string[index + 1:])
	#se for int
	else:
			tam_step = 0

	return max([tam_start, tam_step])




def resolve_precisao(lista, p):
	"""
	Resolucaoo para o problema de precisao dos floats
	
	:type lista: ``numpy arange()``
	:param lista:  lista de valores (x-axis ou y-axis)

	:tupe p: int
	:param p: representa a precisao com que todos os ticks vao ficar
	
	:return: novo array com a precisão arranjada
	"""

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
def devolvePropriedades(ficheiros, dirFiles, TemBoool, confTipoGrafico):
	"""
	Função Auxiliar que devolve varias propriedades

	:type ficheiros: list of str **OR** dict 
	:param ficheiros: Representa os ficheiros onde estamos a ir buscar valores. Se ``TemBoll == False`` *=>* ``ficheiros = ['timenewformulation2.txt', 'timenewformulation0.txt', 'timenewformulation1.txt']``. Se ``TemBool == False``
		*=>* ``ficheiros = {'foo1': {'bins': 'range(4)', 'Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}``
	
	:return minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 

	:return maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:param maxL: representa o tamnaho do maior ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:return Freqmax: valor que se repete mais vezes  em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria
	
	:return ListaDataFicheiros: os valores dos ficheiros numa matrix; Serve para usarmos na ``preparaArrayEmpilhado()``
	"""


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

		#valores e ocorencias d cada um
		values, counts = np.unique(data, return_counts = True)


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
			listaDataFicheiros.append(data)

		f.close()

	if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
		for i in range( len(ficheiros) ):
			listaDataFicheiros[i] = np.append(listaDataFicheiros[i], np.zeros( Lmax - len(listaDataFicheiros[i]) ) ) 

	return Ymin, Ymax + 0.10*Ymax, Lmax, Freqmax,listaDataFicheiros





def preparaArrayEmpilhado(maxL, numFiles, listaDataFicheiros):
	"""
	cria uma matrix de ints e floats

	:type maxL: int
	:param maxL: representa o tamnaho do maior ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria
	
	:type numFile: int
	:param numFiles: numero de ficheiros

	:type listaDataFicheiros: matrix of int and/or float
	:param listaDataFicheiros: valores nos ficheiros

	:return: matrix de valores. cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro
	"""
	# print("listaDataFicheirosta", listaDataFicheiros)
	# data = np.array(listaDataFicheiros)
	# print("data", data)

	# b = np.zeros( (numFiles,maxL) )
	# for i in range(maxL):



	# 	aux = np.sort(data[:,i])
		
	# 	for j in range(numFiles):

	# 		indice = list(aux).index(data[j,i])
	# 		if(indice == 0):
	# 			b[j,i] = 0
	# 		else:
	# 			b[j,i] = aux[indice -1]
	# print("b ",b)
	# return b

	data = np.array(listaDataFicheiros)

	b = np.zeros( (numFiles,maxL) )
	for i in range(maxL):



		aux = np.sort(data[:,i])
		
		for j in range(numFiles):

			indice = list(aux).index(data[j,i])
			if(indice == 0):
				b[j,i] = 0
			else:
				b[j,i] = aux[indice -1]
	return b


def guardaGrafico(confTipoGrafico, dirImagens, folder_name, name):
	"""
	guarda a plt.figure()

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``

	:type name: str
	:param name: nome com que o grafico vai ser guardado
	"""


	
	if not os.path.exists(os.path.join(dirImagens,folder_name[:-2])):
		os.makedirs(os.path.join(dirImagens,folder_name[:-2]))

	#nao é necessario
	#if ('separa' in confTipoGrafico and confTipoGrafico['separa'] == 'True'):



	if ("substitui" in confTipoGrafico and confTipoGrafico["substitui"] == "False"):
		name = fileNameRepetido(os.path.join(dirImagens,folder_name[:-2]),name,'.png')
		if not __debug__:
			print("Nao substitui*** e deixa com nome:"+name)
	plt.savefig(os.path.join(dirImagens,folder_name[:-2],name+".png"))




def fileNameRepetido(dire, name, ext):
	"""
	função de auxilio para descobrir um nome para um ficheiro de uma plt.figure() ja esta em uso
	
	:type dir: str
	:param dir: path onde vai ficar guardada a plt.figure() 
	
	:type name: str
	:param name: nome com que guardamos a plt.figure()

	:type ext: str
	:param ext: extenção em que guardamos a plt.figure() 
	"""

	if not name + ext in  next(os.walk(dire))[2]:
		return name
	j = 0
	while name+'-'+str(j)+ext in  next(os.walk(dire))[2]:
		j+=1
	return name+'-'+str(j)



#especificacoes : copia dos Specs do file(se "SEPARA" == True) ou do grupo intersetado com o do file ("separa" == False)
#tipoGrafico: "Barras","Linhas",etc..
#i: (SEPARA ==F)é o numero da figura ;(SEPARA==T) é um sufixo para o nome do file do grafico
def formatacaoSpecs(especificacoes, folder_name, fileName, tipoGrafico, confTipoGrafico, grafs, i, maxY, maxL, Freqmax, numPilares):
	"""
	funcao aplicada ao grafico de pois de sair da funcao ``desenho()``. Ela faz o parssing 
	da parte das especificacoes do "grafico e aplica - as.

 	:type especificacoes: dict
	:param especificacoes: especificações que vamos usar usar no grafico

	:type folder_name: str
	:param folder_name: nome da diretoria onde o ficheiro de dados esta
	
	:type fileName: str
	:param fileName: nome do ficheiro de valores, vamos, possivelmente, usar como nome da plt.figure() que vamos guardar

	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``
	
	:type grafs: list of str
	:param grafs: lista que contem os tipos de graficos que conseguimos criar Ex: ``grafs = ["Linhas", "Barras", "Hist"]``

	:type i: int 
	:param i: indice do grafico de entre de todos aqueles que selecionamos para fazer plot

	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type Freqmax: int
	:param Freqmax: valor que se repete mais vezes em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:type maxL: int
	:param maxL: representa o tamnaho do maior ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4


	:returns: nome com que o grafico vai ser guardado
	:returns: -1 caso existam erros

	"""

	if "legend" in especificacoes:
		try:
			l = especificacoes.pop("legend")
			eval("plt.legend(**l)")
		except:
			print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " legend pode estar mal formatada / ter parametros que nao existem\nEx: leggend = { loc = upper left, fontsize = 13} \nLeaving")
			return -1

	if "title" in especificacoes:
		try:
			tite = especificacoes.pop("title")
			eval("plt.title(**tite)")
		except:
			print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " title pode estar mal formatado / ter parametros que nao existem\nEx: title = { label = Titulo, fontsize = 13} \nLeaving")
			return -1

	if "fileName" in especificacoes:
		if("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True"):
			grafName = especificacoes.pop('fileName')
			grafName = grafName + "(" + str(i) +")" 
		else:
			grafName = especificacoes.pop('fileName')

	elif ("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True"):
		grafName = fileName
	else:
		grafName = folder_name
	

	#Retiramos se existir 
	if "pinta" in especificacoes:
		especificacoes.pop("pinta")
	if "simbolos" in especificacoes:
		especificacoes.pop("simbolos")
	if "offset" in especificacoes:
		especificacoes.pop("offset")
	if "linhas" in especificacoes:
		especificacoes.pop("linhas")
	if "value" in especificacoes:
		especificacoes.pop("value")
	if "bins" in especificacoes:
		especificacoes.pop("bins")
	if "gauss" in especificacoes:
		especificacoes.pop("gauss")
	if "ylim_colocado" in especificacoes:
		especificacoes.pop("ylim_colocado")
	if "yticks_colocado" in especificacoes:
		especificacoes.pop("yticks_colocado")



	if "figure_size" in especificacoes:
		try:
			plt.gcf().set_size_inches( float(especificacoes["figure_size"][0]) ,float(especificacoes["figure_size"][1]))
		except (ValueError, IndexError):
			print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " figure_size deve ser 2 floats/ints separados por ','\nEx: figure_size = 18, 10\nLeaving")
			return -1
		especificacoes.pop("figure_size")




	#Limite dos Y's
	if "ylim" in especificacoes:
		try:
			plt.ylim(float(especificacoes["ylim"][0]),float(especificacoes["ylim"][1]) * 1.05 )
		except (ValueError, IndexError):
			print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
			return -1
		especificacoes.pop("ylim")
		
		#assim, como podemos estar a chamar mais vezes a funcao "desenho" sabemos que ja atualizamos 
		# o ylim deste grafico 
		#especificacoes["ylim_colocado"] = "True"


	elif ("ylim_colocado" not in especificacoes) and ("ylim" not in especificacoes and ("separa" in confTipoGrafico) and (confTipoGrafico["separa"] == "True")) or "ylim" not in especificacoes and ("ladoAlado"  in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True"):
		#ylim igual para todos o files da mesma folder,quando fazemos separa == T (ou ladoAlado == T) e o user nao tinha dito nada a respeito
		if tipoGrafico == grafs[0] or tipoGrafico == grafs[1]:
			if "yscale" in especificacoes and (especificacoes["yscale"] == "log" or especificacoes["yscale"] == "symlog"):
				plt.ylim(0.1,maxY * 1.05)
			else:	
				plt.ylim(0,maxY * 1.05)
	




	#Linhas , Bar
	if tipoGrafico == grafs[1] or tipoGrafico == grafs[0]:

		#nao deixa meter ticks automaticos
		if "AutoxTicks" not in especificacoes or especificacoes["AutoxTicks"] == "True":

			#mete ticks automaticos
			if "xticks_custome" not in especificacoes:
				#especificacoes["xticks_custome"] = list(range( math.ceil(maxL) ))
				especificacoes["xticks_custome"] = "range("+ str(0) + "," + str( math.ceil(maxL) ) +")"


		if  "xticks_custome" in especificacoes:

			#transforma em lista
			if type(especificacoes["xticks_custome"]) != list:
				aux = []
				aux.append(especificacoes["xticks_custome"])
				especificacoes["xticks_custome"] = aux


			# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"]
			#["range(10)"] ou ["range(0","10"]  
			if especificacoes["xticks_custome"][0][:5] == "range":
				# especificacoes["xticks_custome"] = ["range(0","10","2)]
				especificacoes["xticks_custome"][0] = especificacoes["xticks_custome"][0][6:] 
				# especificacoes["xticks_custome"] = ["0","10","2)]
				especificacoes["xticks_custome"][-1] = especificacoes["xticks_custome"][-1][:-1]
				# especificacoes["xticks_custome"] = ["0","10","2]
				especificacoes["xticks_custome"] = eval( "np.arange(" + ",".join(especificacoes["xticks_custome"]) + ')' )

			
				p = maior_precisao(especificacoes["xticks_custome"])
				especificacoes["xticks_custome"] = resolve_precisao(especificacoes["xticks_custome"],p)


			#mete ticks grafico junto
			if "xticks_custome" in especificacoes and ("ladoAlado" not in confTipoGrafico or confTipoGrafico["ladoAlado"] == "False"): 
				plt.xticks(range(len(especificacoes["xticks_custome"])),especificacoes["xticks_custome"])			
				especificacoes.pop("xticks_custome")

			#mete ticks no graficos ladoAlado
			elif "xticks_custome" in especificacoes and ("ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True"): 
	
				# if len(especificacoes["xticks_custome"]) < ( (i + 1) * numPilares):
				# 	especificacoes["xticks_custome"] = especificacoes["xticks_custome"]+["","","",""]
				

				#mete os ticks aos poucos em cada janela 
				plt.xticks(range(i*numPilares,numPilares+ i*numPilares), especificacoes["xticks_custome"][i*numPilares : numPilares+ i*numPilares])							 		
				especificacoes.pop("xticks_custome")

	#Hist
	elif tipoGrafico == grafs[2]:

		#nao deixa meter ticks automaticos
		if "AutoxTicks" not in especificacoes or especificacoes["AutoxTicks"] == "True":

			if "bins_aux" in especificacoes:
				plt.xticks(especificacoes["bins_aux"])


		if ("xticks_custome" in list(especificacoes.keys())): 

			#transforma em lista
			if type(especificacoes["xticks_custome"]) != list:
				aux = []
				aux.append(especificacoes["xticks_custome"])
				especificacoes["xticks_custome"] = aux


			# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"] 
			#["range(10)"] ou ["range(0","10"]  
			if especificacoes["xticks_custome"][0][:5] == "range":
				# especificacoes["xticks_custome"] = ["range(0","10","2)]
				especificacoes["xticks_custome"][0] = especificacoes["xticks_custome"][0][6:] 
				# especificacoes["xticks_custome"] = ["0","10","2)]
				especificacoes["xticks_custome"][-1] = especificacoes["xticks_custome"][-1][:-1]
				# especificacoes["xticks_custome"] = ["0","10","2]
				especificacoes["xticks_custome"] = eval( "np.arange(" + ",".join(especificacoes["xticks_custome"]) + ')' )

				p = maior_precisao(especificacoes["xticks_custome"])
				especificacoes["xticks_custome"] = resolve_precisao(especificacoes["xticks_custome"],p)


			plt.xticks(especificacoes["bins_aux"],especificacoes["xticks_custome"])			
			especificacoes.pop("xticks_custome")



		if "bins_aux" in especificacoes:
			especificacoes.pop("bins_aux")





			# if "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False":
			# 	step = especificacoes["xticks_custome"][1] - especificacoes["xticks_custome"][0]
			# 	x["xticks_custome"]

			# # xticks = [2,3,4,5,6,7]
			# if type(especificacoes["xticks_custome"])  == list:
				
			# 	#dava problema estranho: os ticks vinham todos para a esquerda
			# 	mini = min(especificacoes["xticks_custome"])
			# 	plt.xticks(range( len(especificacoes["xticks_custome"]) ), [ t + mini for t in especificacoes["xticks_custome"] ] )			
			# # xticks = range(0,10)
			# else:
			# 	plt.xticks(range( len(especificacoes["xticks"]) ),especificacoes["xticks"])	




	#Limites do X's
	if "xlim" in especificacoes:
		if "ladoAlado" not in confTipoGrafico or confTipoGrafico["ladoAlado"] == "False":
			try:
				plt.xlim(float(especificacoes["xlim"][0]),float(especificacoes["xlim"][1]))
			except (ValueError, IndexError):
				print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " xlim deve ser 2 floats/ints separados por ','\nEx: xlim = 2, 5\nLeaving")
				return -1
		#print(float(especificacoes["xlim"][0]), "e tambem ",float(especificacoes["xlim"][1]))
		especificacoes.pop("xlim")



	if "xticks" in especificacoes:
		xt = especificacoes.pop("xticks")
		eval("plt.xticks(**xt)")

	if "yticks" in especificacoes:
		yt = especificacoes.pop("yticks")
		eval("plt.yticks(**yt)")


	if "AutoxTicks" in especificacoes:
		especificacoes.pop("AutoxTicks")

	#Deve aceitar grande parte dos parametros da decumentacao
	#Tentei fazer parametrizavel...
	for string in especificacoes:
		eval('plt.'+string+'("'+ especificacoes[string]+'")')
	

	return grafName






def desenho_Linhas(especificacoes, dicio, x, rgb, rgbMult, numFiles, m, i):
	"""
	funcao auxiliar para desenhar graficos de linhas

	:type especificacoes: dict
	:param especificacoes: especificações que vamos usar usar no grafico

	:type dicio: dict
	:param dicio: especificacoes para o grafico (que normalmente entram em plt.plot()/bar()/hist() ) Ex: ``d = {'color': 'g', 'linestyle': 'None', 'marker': 'h', 'label': 'teste legenda2'}``

	:type x: np array
	:param x: array com os valores que formam os graficos

	:type rgb: np.zeros(3) ou np.ones(3)
	:param rgb: array[3] quu contem valores rgb para pintar as linhas (valores de 0 - 1) 

	:type rgbMult: int
	:param rgbMult: diz no se vamos incrementar ou diminuir os valores do array rgb

 	:type numFiles: int 
	:param numFiles: numero do ficheiro de valores de entre de todos aqueles que selecionamos para fazer plot

	:type m: list of char
	:param m: lista que conte tipos de marcadores para os pontos do grafico.	Ex: ``m = [ 'x', '<', 'o', '.']``

	:type i: int 
	:param i: indice do grafico de entre de todos aqueles que selecionamos para fazer plot
	
	:returns: devolve 0 <=> numero das figuras que fizemos plot
	:returns: -1 caso existam erros
	"""	

	
	if "pinta" in especificacoes:
		sp = especificacoes["pinta"]
		#cor e simbolos andam ao mesmo tempo
		if (sp["f"] == "1"):

			dicio["color"] = rgb + (rgbMult)*( (i+1) * (1/(numFiles+1)) )  
			dicio["marker"] = m[ i% len(m)]

		#cor so muda quando acabam os simbolos
		elif sp["f"] == "2":


			# "j" é o numeor de vezes que usamos todos os simbolos
			dicio["marker"] = m[ i% len(m)]
			aux = 0
			j = i - len(m)
			while(j >= 0):
				j -= len(m)
				aux+=1
		        

			dicio["color"] = rgb + (rgbMult * ((aux + 1) * 1/(numFiles + 1)) ) 


	info = plt.plot(x,**dicio)

	# if "value" in especificacoes:
	# 	p = 1
	# 	fonts = 10
	# 	if "precisao" in especificacoes["value"]:
	# 		p = int(especificacoes["value"]["precisao"])

	# 	if "fontsize" in especificacoes["value"]:
	# 		fonts = int(especificacoes["value"]["fontsize"])


	# 	for j,valor in enumerate(x):
	# 		if valor == 0:
	# 			continue										  
	# 		plt.text( j, valor + (valor * 0.05), '%.{0}lf'.format(p) % float(valor), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))


	#so fizemos uma plt.figure
	return 0








def desenho_Barras(especificacoes, rgb, rgbMult, edg, edgMult, numFiles, numPilares, hat, confTipoGrafico, x, i, dicio, bar_empilha):

	"""
	funcao auxiliar para desenhar graficos de Barras

	:type especificacoes: dict
	:param especificacoes: especificações que vamos usar usar no grafico

	:type rgb: np.zeros(3) ou np.ones(3)
	:param rgb: array[3] que contem valores rgb para pintar as barras (valores de 0 - 1) 

	:type rgbMult: int
	:param rgbMult: diz no se vamos incrementar ou diminuir os valores do array rgb

	:type edg: np.zeros(3) ou np.ones(3)
	:param edg: array[3] que contem valores rgb para pintar as linhas das barras (valores de 0 - 1) 

	:type edgMult: int
	:param edgMult: diz no se vamos incrementar ou diminuir os valores do array edg

 	:type numFiles: int 
	:param numFiles: numero do ficheiro de valores de entre de todos aqueles que selecionamos para fazer plot

	:type hat: list of char
	:param hat: lista que contem tipos de marcadores para os desenhos nas barras Ex: ``	hat = ['/', '.','*','x', 'o','//', 'O' ]``

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``
	
	:type x: np array
	:param x: array com os valores que formam os graficos

	:type i: int 
	:param i: indice do grafico de entre de todos aqueles que selecionamos para fazer plot

	:type dicio: dict
	:param dicio: especificacoes para o grafico (que normalmente entram em plt.plot()/bar()/hist() ) Ex: ``d = {'color': 'g', 'linestyle': 'None', 'marker': 'h', 'label': 'teste legenda2'}``
	
	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:returns: devolve 0 se fizemos plot de uma figura OU numero das figuras que fizemos plot (se fizemos plot de mais do que uma)
	:returns: -1 caso existam erros
	"""	


	if "pinta" in especificacoes:
		sp = especificacoes["pinta"]
		#cor e simbolos andam ao mesmo tempo
		if sp["f"] == "1":

			if "edge" in sp and sp["edge"] == "solido":
				dicio["edgecolor"] = edg
			elif "edge" in sp and sp["edge"] == "gradiente":		
				dicio["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )
		
			dicio["color"] = rgb + (rgbMult)*(i * (1/numFiles) )  
			dicio["hatch"] = hat[ i% len(hat)]


		#cor so muda quando acabam os simbolos
		elif sp["f"] == "2":

			if "edge" in sp and sp["edge"] == "solido":
				dicio["edgecolor"] = edg
			elif "edge" in sp and sp["edge"] == "gradiente":		
				dicio["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )


			# "j" é o numeor de vezes que usamos todos os simbolos
			dicio["hatch"] = hat[ i% len(hat)]
			aux = 0
			j = i - len(hat)
			while(j >= 0):
				j -= len(hat)
				aux+=1
		        

			dicio["color"] = rgb + (rgbMult * (aux * 1/numFiles) ) 








	if "width" not in dicio and "ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True":
		w = 1/ numFiles - 0.1
		dicio["width"] = w
	elif "width" in dicio:
		try:
			dicio["width"] = float(dicio["width"])
		except (ValueError, IndexError):
			print("[ERRO] Problema nas Especificaçoes individuais\nEm ",folder_name, " width deve ser um int/float\nEx: width = 0.8\nLeaving")
			return -1
	#ladoA lado == False and width not in dicio
	else:
		dicio["width"] = 0.8


	#off set em relacao ao lado esquerdo das barras
	if "offset" in especificacoes:
		if especificacoes["offset"] == "center":
			if "ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True":
				offset = -1 * numFiles * dicio["width"] /2 
			else:
				offset = -1 * dicio["width"] /2 

		elif especificacoes["offset"] == "right":
			if "ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True":
				offset = -1 * numFiles * dicio["width"] 
			else:
				offset = -1 * dicio["width"] + (1- dicio["width"])

		else:
			try:
				offset = float(especificacoes["offset"]) * -1
			except (ValueError, IndexError):
				print("[ERRO] Problema nas Especificaçoes \nEm ",folder_name," offdet deve ser um int/float ou entao a key word 'center' ou right\nEx: offset = center\nLeaving")
				return -1
	else:
		offset = 0



	
	#plot junto lado a lado	
	if  "ladoAlado" in confTipoGrafico and confTipoGrafico["ladoAlado"] == "True":


		dicio["align"] = "edge"



		#if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
		#	x = x - b[i]			acho que nao devia estar aqui


		ini = 0 
		fim = numPilares
		for j in range(len(x)//numPilares) :
			#if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True" :
			#	plt.figure(i*j)
			#else:
			

			#for a in plt.yticks()[1]:
			#	print(a)


			if "yticks_colocado" in especificacoes:
				yl,yt = plt.yticks()
				plt.figure(j)
				plt.yticks(yl,yt)
			else:
				plt.figure(j)


			info = plt.bar(np.arange(ini,fim) + dicio["width"] * i + offset ,x[ini:fim],**dicio)
			ini += numPilares
			fim += numPilares
			
			#Mete linhas no bar
			# if "linhas" in especificacoes and especificacoes["linhas"] == "True":
			# 	dplot = {}
			# 	if "pinta" in especificacoes:
			# 		dplot["marker"] = m[ i% len(m) ]
			# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
			# 	plt.plot(x[ini:fim],**dplot)


			if "value" in especificacoes:
				p = 1
				fonts = 10
				if "precisao" in especificacoes["value"]:
					try:
						p = int(especificacoes["value"]["precisao"])
					except (ValueError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " precisao deve ser um int\nEx: precisao = 3\nLeaving")
						return -1


				if "fontsize" in especificacoes["value"]:
					try:
						fonts = int(especificacoes["value"]["fontsize"])
					except (ValueError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " fontsize deve ser um int/float\nEx: fontsize = 13\nLeaving")
						return -1


				ylim_max = plt.ylim()[1]
				ylim_min = plt.ylim()[0]
				if "ylim" in especificacoes:
					try:
						ylim_max = float(especificacoes["ylim"][1])
						ylim_min = float(especificacoes["ylim"][0])
					except (ValueError, IndexError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
						return -1


				#valores normais
				if "yticks_colocado" not in especificacoes:

					for rect in info:
						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height < ylim_min:
							continue	

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))

				#tem em consideracao os yloc e yticks
				else:
					yloc = plt.yticks()[0]
					# for u in plt.yticks()[1]:
					# 	print(u)


					yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

					for rect in info:
						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height < ylim_min:
							continue
	
						numero = atualiza_value_tick(height, yloc, yticks)

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))

		#ultima figura
		#verifica se tem de desenhar mais uma figura
		if  numPilares * (j + 1)  < len(x):
			j += 1		

			if "yticks_colocado" in especificacoes:
				yl,yt = plt.yticks()
				plt.figure(j)
				plt.yticks(yl,yt)
			else:
				plt.figure(j)

			aux = np.zeros( ((j+1) * numPilares) - len(x), dtype = int)
			x1 = np.concatenate((x,aux),axis = 0 )
			info = plt.bar(np.arange(ini,fim) + dicio["width"] *i + offset ,x1[ini:fim],**dicio)
			
			if "value" in especificacoes:
				p = 1
				fonts = 10
				if "precisao" in especificacoes["value"]:
					try:
						p = int(especificacoes["value"]["precisao"])
					except (ValueError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " precisao deve ser um int\nEx: precisao = 3\nLeaving")
						return -1

				if "fontsize" in especificacoes["value"]:
					try:
						fonts = int(especificacoes["value"]["fontsize"])
					except (ValueError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " fontsize deve ser um int/float\nEx: fontsize = 13\nLeaving")
						return -1

				ylim_max = plt.ylim()[1]
				ylim_min = plt.ylim()[0]
				if "ylim" in especificacoes:
					try:
						ylim_max = float(especificacoes["ylim"][1])
						ylim_min = float(especificacoes["ylim"][0])
					except (ValueError, IndexError):
						print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
						return -1


				#valores normais
				if "yticks_colocado" not in especificacoes:

					for k,rect in enumerate(info):
						if k > numPilares - len(aux) - 1:
							break 

						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height < ylim_min:
							continue	

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

				#tem em consideracao os yloc e yticks
				else:
					yloc = plt.yticks()[0]
					#for u in plt.yticks()[1]:
					#	print(u)
					yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

					for rect in info:

						if k > numPilares - len(aux) - 1:
							break 

						height = rect.get_height()
						#if height == 0:
						if  height > ylim_max or height < ylim_min:
							continue
	
						numero = atualiza_value_tick(height, yloc, yticks)

						plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))



			#Mete linhas no bar
			# if "linhas" in especificacoes and especificacoes["linhas"] == "True":
			# 	dplot = {}
			# 	if "pinta" in especificacoes:
			# 	#	dplot["pinta"] = especificacoes["pinta"]
			# 	#desenho("Linhas",x[ini:fim],dplot,{},i,numFiles,numPilares,minY,maxY,{})
			# 		dplot["marker"] = m[ i% len(m) ]
			# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
			# 	plt.plot(x[ini:fim],**dplot)


		#devolde numero de figuras para guardar
		return j+1 



	#plot junto overlaping ou empilhados
	elif "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False":

		if "alpha" not in confTipoGrafico:
			if "pinta" not in especificacoes:	
				dicio["alpha"] = 0.4
		


		if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
			x = x - bar_empilha[i][:len(x)]
			dicio["bottom"] = bar_empilha[i][:len(x)]

		info = plt.bar(np.arange(len(x)) + offset, x,**dicio)
	
		# if "linhas" in especificacoes and especificacoes["linhas"] == "True":
		# 	dplot = {}
		# 	if "pinta" in especificacoes:
		# 	#	dplot["pinta"] = especificacoes["pinta"]
		# 	#desenho("Linhas",x,dplot,{},i,numFiles,numPilares,minY,maxY,{})
		# 		dplot["marker"] = m[ i% len(m) ]
		# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
		# 	plt.plot(x,**dplot)	



		if "value" in especificacoes:
			p = 1
			fonts = 10
			if "precisao" in especificacoes["value"]:
				try:
					p = int(especificacoes["value"]["precisao"])
				except (ValueError):
					print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " precisao deve ser um int\nEx: precisao = 3\nLeaving")
					return -1



			if "fontsize" in especificacoes["value"]:
				try:
					fonts = int(especificacoes["value"]["fontsize"])
				except (ValueError):
					print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " fontsize deve ser um int/float\nEx: fontsize = 13\nLeaving")
					return -1




			ylim_max = plt.ylim()[1]
			ylim_min = plt.ylim()[0]
			if "ylim" in especificacoes:
				try:
					ylim_max = float(especificacoes["ylim"][1])
					ylim_min = float(especificacoes["ylim"][0])
				except (ValueError, IndexError):
					print("[ERRO] Problema nas Especificaçoes \nEm ",folder_name, "  ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
					return -1

			#valores normais
			if "yticks_colocado" not in especificacoes:
				for j,rect in enumerate(info):
					height = rect.get_height()

					#if height == 0:
					if  height > ylim_max or height < ylim_min:
						continue	

					if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
						height += bar_empilha[i][j]	

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
					if  height > ylim_max or height < ylim_min:
						continue	

					if "empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True":
						height += bar_empilha[i][j]	

					numero = atualiza_value_tick(height,yloc,yticks)

					plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))
	

		#so fizemos graficos numa plt.figuere()
		return 0 

	#plot grafs separados
	else:



		info = plt.bar(np.arange(len(x))  + offset, x,**dicio)


		# if "linhas" in especificacoes and especificacoes["linhas"] == "True":
		# 	dplot = {}
		# 	if "pinta" in especificacoes:
		# 	#	dplot["pinta"] = especificacoes["pinta"]
		# 	#desenho("Linhas",x,dplot,{},i,numFiles,numPilares,minY,maxY,{})
		# 		dplot["marker"] = m[ i% len(m) ]
		# 		dplot["color"] = np.zeros(3) + (i * (1/numFiles) )  
		# 	plt.plot(x,**dplot)	

		if "value" in especificacoes:
			p = 1
			fonts = 10
			if "precisao" in especificacoes["value"]:
				try:
					p = int(especificacoes["value"]["precisao"])
				except (ValueError):
					print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " precisao deve ser um int\nEx: precisao = 3\nLeaving")
					return -1



			if "fontsize" in especificacoes["value"]:
				try:
					fonts = int(especificacoes["value"]["fontsize"])
				except (ValueError):
					print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " fontsize deve ser um int/float\nEx: fontsize = 13\nLeaving")
					return -1



			ylim_max = plt.ylim()[1]
			ylim_min = plt.ylim()[0]
			if "ylim" in especificacoes:
				try:
					ylim_max = float(especificacoes["ylim"][1])
					ylim_min = float(especificacoes["ylim"][0])
				except (ValueError, IndexError):
					print("[ERRO] Problema nas Especificaçoes \nEm ",folder_name, "  ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
					return -1


			#valores normais
			if "yticks_colocado" not in especificacoes:

				for rect in info:
					height = rect.get_height()
					#if height == 0:
					if  height > ylim_max or height < ylim_min:
						continue										  
					plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(height), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))

			#tem em consideracao os yloc e yticks
			else:

				yloc = plt.yticks()[0]
				#for u in plt.yticks()[1]:
				#	print(u)
				yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

				for rect in info:
					height = rect.get_height()
					#if height == 0:
					if  height > ylim_max or height < ylim_min:
						continue

					numero = atualiza_value_tick(height,yloc,yticks)

					plt.text(rect.get_x() + rect.get_width()/2.0, height, '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))

		#so fizemos graficos numa plt.figuere()
		return 0 








def desenho_Hist(confTipoGrafico, dicio, especificacoes, x, rgb, rgbMult, edg, edgMult, hat, i, numFiles, minY, maxY ):

	"""
	funcao auxiliar para desenhar graficos de Histogramas


	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``
	

	:type dicio: dict
	:param dicio: especificacoes para o grafico (que normalmente entram em plt.plot()/bar()/hist() ) Ex: ``d = {'color': 'g', 'linestyle': 'None', 'marker': 'h', 'label': 'teste legenda2'}``
	
	:type especificacoes: dict
	:param especificacoes: especificações que vamos usar usar no grafico

	:type x: np array
	:param x: array com os valores que formam os graficos

	:type rgb: np.zeros(3) ou np.ones(3)
	:param rgb: array[3] que contem valores rgb para pintar as barras (valores de 0 - 1) 

	:type rgbMult: int
	:param rgbMult: diz no se vamos incrementar ou diminuir os valores do array rgb

	:type edg: np.zeros(3) ou np.ones(3)
	:param edg: array[3] que contem valores rgb para pintar as linhas das barras (valores de 0 - 1) 

	:type edgMult: int
	:param edgMult: diz no se vamos incrementar ou diminuir os valores do array edg

	:type hat: list of char
	:param hat: lista que contem tipos de marcadores para os desenhos nas barras Ex: ``	hat = ['/', '.','*','x', 'o','//', 'O' ]``

	:type i: int 
	:param i: indice do grafico de entre de todos aqueles que selecionamos para fazer plot
 	
 	:type numFiles: int 
	:param numFiles: numero do ficheiro de valores de entre de todos aqueles que selecionamos para fazer plot

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 

	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:returns: devolve 0 <=> numero das figuras que fizemos plot
	:returns: -1 caso existam erros
	"""



	if "alpha" not in confTipoGrafico:
		if "pinta" not in especificacoes:
			dicio["alpha"] = 0.5 



	if "width" in dicio:
		try:
			dicio["width"] = float(dicio["width"])
		except (ValueError, IndexError):
			print("[ERRO] Problema nas Especificaçoes individuais\nEm ",folder_name, " width deve ser um int/float\nEx: width = 0.8\nLeaving")
			return -1


	#Bins------
	if "separa" not in confTipoGrafico or confTipoGrafico["separa"] == "False" :

		if "bins" in dicio:
			bins = dicio["bins"]
		elif "bins" in especificacoes:
			bins = especificacoes["bins"]
		else:
			#maximo e minimo deste grafico
			#bins = "range("+ str(min(x) - 1) + "," + str(max(x) + 3) +")"
			bins = "range("+ str(min(x) ) + "," + str(max(x) + 2) +")"

	else:	
		if "bins" in dicio:
			bins = dicio["bins"]
		elif "bins" in especificacoes:
			bins = especificacoes["bins"]
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
		dicio["bins"] = eval( "np.arange(" + ",".join(bins) + ")" )
	else:
		try:
			dicio["bins"] = bins
			dicio["bins"] = [ float(aux) for aux in dicio["bins"] ]
		except (ValueError, IndexError):
			print("[ERRO] Problema nas Especificaçoes individuais\nEm ",folder_name, " bins deve ser um grupo de int/float separado por ','\nEx: bins = range(10)\nLeaving")
			return -1



	#assim sabemos que bins o hist tem e podemos meter xticks
	especificacoes["bins_aux"] = dicio["bins"]


	#Cor -------
	if "pinta" in especificacoes:
		sp = especificacoes["pinta"]
		#cor e simbolos andam ao mesmo tempo


		if sp["f"] == "1":

			if "edge" in sp and sp["edge"] == "solido":
				dicio["edgecolor"] = edg
			elif "edge" in sp and sp["edge"] == "gradiente":		
				dicio["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )
		
			dicio["color"] = rgb + (rgbMult)*(i * (1/numFiles) )  
			dicio["hatch"] = hat[ i% len(hat)]


		#cor so muda quando acabam os simbolos
		elif sp["f"] == "2":

			if "edge" in sp and sp["edge"] == "solido":
				dicio["edgecolor"] = edg

			elif "edge" in sp and sp["edge"] == "gradiente":		
				dicio["edgecolor"] = edg + (edgMult)*(i * (1/numFiles) )



			# "j" é o numeor de vezes que usamos todos os simbolos
			dicio["hatch"] = hat[ i% len(hat)]
			aux = 0
			j = i - len(hat)
			while(j >= 0):
				j -= len(hat)
				aux+=1
		        

			dicio["color"] = rgb + (rgbMult * (aux * 1/numFiles) ) 


	elif "edgecolor" not in dicio:
		dicio["edgecolor"] = "black"




	info = plt.hist(x,**dicio)



	if "gauss" in especificacoes:
	
		if especificacoes["gauss"] == "edge": 
			if "pinta" in especificacoes:
				gauss_color = edg
			else:
				gauss_color = especificacoes["gauss"]

		else:
			gauss_color = especificacoes["gauss"]

		dicio_aux = { "color" : gauss_color}

		mean = np.mean(x)
		variance = np.var(x)
		sigma = np.sqrt(variance)
		x = np.linspace(dicio["bins"][0], dicio["bins"][-1], len(x)  )

		#x = np.linspace(0, 11, len(x)  )
		dx = info[1][1] - info[1][0]
		scale = len(x)*dx
		plt.plot(x, scipy.stats.norm.pdf(x, mean, sigma)*scale, **dicio_aux)





	#Values-------

	#info[0] : frequencias
	#info[1] : bins
	if "value" in especificacoes:
		p = 1
		fonts = 10
		if "precisao" in especificacoes["value"]:
			try:
				p = int(especificacoes["value"]["precisao"])
			except (ValueError):
				print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " precisao deve ser um int\nEx: precisao = 3\nLeaving")
				return -1

		if "fontsize" in especificacoes["value"]:
			try:
				fonts = int(especificacoes["value"]["fontsize"])
			except (ValueError):
				print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " fontsize deve ser um int/float\nEx: precisao = 13\nLeaving")
				return -1




		ylim_max = plt.ylim()[1]
		ylim_min = plt.ylim()[0]
		if "ylim" in especificacoes:
			try:
				ylim_max = float(especificacoes["ylim"][1])
				ylim_min = float(especificacoes["ylim"][0])
			except (ValueError, IndexError):
				print("[ERRO] Problema nas Especificaçoes\nEm ",folder_name, " ylim deve ser 2 floats/ints separados por ','\nEx: ylim = 2, 5\nLeaving")
				return -1

		offset_centro = info[1][1] - info[1][0]

		#mete values normalmente
		if "yticks_colocado" not in especificacoes:

			for j,valor in enumerate(info[0]):
				#se for "0" ou sair da figura nao desenhamos
				if valor == 0 or valor > ylim_max:
					continue										  
				plt.text( info[1][j] + offset_centro/2, (valor + 0.005), '%.{0}lf'.format(p) % float(valor), fontsize = fonts , ha = 'center', va = 'bottom', color = (0,0,0))

		#Toma em consideracao os yticks
		else:

			yloc = plt.yticks()[0]
			#for u in plt.yticks()[1]:
			#	print(u)
			yticks = [ float(str(tick).split(",")[2][2:-2])  for tick in plt.yticks()[1]]

			for j,valor in enumerate(info[0]):
				#se for "0" ou sair da figura nao desenhamos
				if valor == 0 or valor > ylim_max or valor < ylim_min :
					continue			

				numero = atualiza_value_tick(valor, yloc, yticks)

				plt.text( info[1][j] + offset_centro/2, (valor + 0.005), '%.{0}lf'.format(p) % float(numero), fontsize = fonts , ha = 'center', va = 'bottom',color = (0,0,0))

	#fizemos so uma plt.figure()
	return 0











#especificacoes : copia dos Specs do file(se "SEPARA" == True) ou do grupo intersetado com o do file ("separa" == False)

def desenho(tipoGrafico, x, dicio, confTipoGrafico, i, numFiles, numPilares, especificacoes, fileName, minY, maxY, bar_empilha):
	"""
	Vai tratar dos aspetos do "desenho" do grafico (cor, edgecolor, valores no topo das Barras, Hist-bins) ; tambem colocamos aqui os yticks para ficarmos com os valores que vao
	aparecer no y-axis e podermos ajustar os valores que poderam aparecer no topo das tabelas dos plt.bar e plt.hist() 


	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type x: np array
	:param x: array com os valores que formam os graficos

	:type dicio: dict
	:param dicio: especificacoes para o grafico (que normalmente entram em plt.plot()/bar()/hist() ) Ex: ``dicio = {'color': 'g', 'linestyle': 'None', 'marker': 'h', 'label': 'teste legenda2'}``

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``
	
	:type i: int 
	:param i: indice do grafico de entre de todos aqueles que selecionamos para fazer plot

	:type numFiles: int 
	:param numFiles: numero do ficheiro de valores de entre de todos aqueles que selecionamos para fazer plot

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4

	:type especificacoes: dict
	:param especificacoes: especificações que vamos usar usar no grafico

	:type fileName: str
	:param fileName: nome do ficheiro de valores, vamos, possivelmente, usar como nome da plt.figure() que vamos guardar

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 

	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:returns: numero de figuras os fizemos plot <=> numero de figuras que tem de ser guardadas
	:returns: -1 caso existam erros
	"""



	m = [ 'x', '<', 'o', '.']
	hat = ['/', '.','*','x', 'o','//', 'O' ]

	#---------Todos

	#autoLegendas
	if "legend" in especificacoes and "label" not in dicio:
		dicio["label"] = fileName


	rgb = 0
	rgbMult = 0
	edg = 0
	edgMult = 0
	# Escala de Cinza
	if "pinta" in especificacoes:
		sp = especificacoes["pinta"]
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
	#se o utilizador os tiver metido temos de fazer especificacoes.pop para nao dar erro na parte 
	# do codigo que esta a aceitar plt.[strings] genericas  
	if "yscale" in especificacoes and (especificacoes["yscale"] == "log" or especificacoes["yscale"] == "symlog"):
		if "yticks_custome" in especificacoes:
			print("[NOTA]Com scale != linear, yticks nao é aceite")
			especificacoes.pop("yticks_custome")
		if "yloc" in especificacoes:
			print("[NOTA]Com scale != linear, yloc nao é aceite")
			especificacoes.pop("yloc")

	elif "yloc" in especificacoes and "yticks_custome" not in especificacoes:
			print("[NOTA]Sem yticks, yloc nao é aceite")
			especificacoes.pop("yloc")

	#metemos yticks
	elif "yticks_custome" in  especificacoes  and ("yscale" not in especificacoes or especificacoes["yscale"] == "linear"): 


		#transforma em lista
		if type(especificacoes["yticks_custome"]) != list:
			aux = []
			aux.append(especificacoes["yticks_custome"])
			especificacoes["yticks_custome"] = aux


		# ["1","t,"3","e","4"] ou ["range(10)"] ou ["range(0","10"]  
		# Se ["range(10)"] ou ["range(0","10"]  
		if especificacoes["yticks_custome"][0][:5] == "range":
			# especificacoes["yticks_custome"] = ["range(0","10","2)]
			especificacoes["yticks_custome"][0] = especificacoes["yticks_custome"][0][6:] 
			# especificacoes["yticks_custome"] = ["0","10","2)]
			especificacoes["yticks_custome"][-1] = especificacoes["yticks_custome"][-1][:-1]
			# especificacoes["yticks_custome"] = ["0","10","2]
			especificacoes["yticks_custome"] = eval( "np.arange(" + ",".join(especificacoes["yticks_custome"]) + ')' )
			

			p = maior_precisao(especificacoes["yticks_custome"])

			especificacoes["yticks_custome"] = resolve_precisao(especificacoes["yticks_custome"],p)



		#yloc diz nos as localizacoes dos ticks
		#loc automatica
		if "yloc" not in especificacoes:
			plt.yticks(range(len(especificacoes["yticks_custome"])),especificacoes["yticks_custome"])			
			especificacoes.pop("yticks_custome")
			
			especificacoes["yticks_colocado"] = "True"

			#for u in plt.yticks()[1]:
			#	print(u)

		#loc do user
		else:

			#transforma em lista
			if type(especificacoes["yloc"]) != list:
				aux = []
				aux.append(especificacoes["yloc"])
				especificacoes["yloc"] = aux

			
			# ["1","2,"3","5","10"] ou ["range(10)"] ou ["range(0","10"]  
			if especificacoes["yloc"][0][:5] == "range":
				# especificacoes["yloc"] = ["range(0","10","2)]
				especificacoes["yloc"][0] = especificacoes["yloc"][0][6:] 
				# especificacoes["yloc"] = ["0","10","2)]
				especificacoes["yloc"][-1] = especificacoes["yloc"][-1][:-1]
				# especificacoes["yloc"] = ["0","10","2]
				especificacoes["yloc"] = eval( "np.arange(" + ",".join(especificacoes["yloc"]) + ')' )

			try:
				especificacoes["yloc"] = [ float(aux)  for aux in especificacoes["yloc"]] 
			except (ValueError):
				print("[ERRO] Problema nas Especificaçoes \nEm ",folder_name, " yloc deve ser um grupo de int/float separados por ','\nEx: yloc = 0,1,2,3,4\nLeaving")
				return -1

			#
			if len(especificacoes["yloc"]) != len(especificacoes["yticks_custome"]):
				print("[ERRO] Problema nas Especificaçoes \nEm ",folder_name, " yloc (tamanho = ",len(especificacoes["yloc"]),") e yticks_custome (tamanho = ",len(especificacoes["yticks_custome"]),") tem de ter o mesmo tamanho\nEx: yloc = 0,1,2,3,4 yticks_custome = a,b,c,d,e\nLeaving")
				return -1 


			plt.yticks(especificacoes["yloc"], especificacoes["yticks_custome"])			
			
			especificacoes.pop("yticks_custome")
			especificacoes.pop("yloc")
			especificacoes["yticks_colocado"] = "True"




	#-----------Linhas
	if tipoGrafico == grafs[0]:

		num_figuras = desenho_Linhas(especificacoes, dicio, x, rgb, rgbMult, numFiles, m, i)

	#-----------Barras
	elif tipoGrafico == grafs[1]:
		
		num_figuras = desenho_Barras(especificacoes, rgb, rgbMult, edg, edgMult, numFiles, numPilares, hat, confTipoGrafico, x, i, dicio, bar_empilha)

	#------------Hist
	elif tipoGrafico == grafs[2] :

		num_figuras = desenho_Hist(confTipoGrafico, dicio, especificacoes, x, rgb, rgbMult, edg, edgMult, hat, i, numFiles, minY, maxY)

	#Verifica se terminou mal
	if num_figuras == -1:
		return -1

	return num_figuras






def ficheiros_separados(dirImagens, folder_name, tipoGrafico, dicio, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax):
	"""
	Le os ficheiros comos valores. Chama ``desenho()`` para fazer o plot. Aplica as especifiçaões do grafico presentes no .conf em ``Specs = {}``.
	Guarda os graficos gerados chamaando ``guardaGrafico()``   

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``
	
	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type dicio: dict
	:param dicio: especificções do ficheiro. Ex: ``dicio = {'foo1': {'bins': 'range(4)', 'Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}``

	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 


	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type Freqmax: int
	:param Freqmax: valor que se repete mais vezes em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:returns: -1 caso existam erros, 0 caso contrario
	"""

	if not __debug__:
		print("FICHEIROS SEPARADOS")

	for i,fileName in enumerate(dicio):
		dirF = os.path.join(dirFiles,fileName+'.txt')
		f = open(dirF,'r')
		data =  np.array( list(map( lambda x:float(x),f.read().split() )) )

		if not __debug__:
			print('fmt :',dicio[fileName])
		

		if "Specs" in dicio[fileName]:
			#retiramos os specs, fazemos plot e fazemos formatacao deste grafico
			especificacoes = dicio[fileName].pop("Specs")
			especificacoes = unirSpecs(especificacoes,confTipoGrafico)
			terminou_bem = desenho(tipoGrafico, data, dicio[fileName], confTipoGrafico, i, len(dicio), numPilares, especificacoes, fileName, minY, maxY, bar_empilha)
			grafName = formatacaoSpecs(especificacoes, folder_name, fileName, tipoGrafico, confTipoGrafico, grafs, i, maxY, len(data), Freqmax, numPilares)
		elif "Specs" in confTipoGrafico:
			#fazemos a formataçao geral para todos
			#copia necessaria pois alterarmos os Specs na formatacaoSpecs
			especificacoes = copy.deepcopy(confTipoGrafico["Specs"])
			terminou_bem = desenho(tipoGrafico, data, dicio[fileName], confTipoGrafico, i, len(dicio), numPilares, especificacoes, fileName, minY, maxY, bar_empilha)
			grafName = formatacaoSpecs(especificacoes, folder_name, fileName, tipoGrafico, confTipoGrafico, grafs, i, maxY, len(data), Freqmax, numPilares)		
		else:
			#plot sem Specs
			grafName = folder_name
			terminou_bem = desenho(tipoGrafico, data, dicio[fileName], confTipoGrafico, i, len(dicio), numPilares, {}, fileName, minY, maxY, bar_empilha)

		f.close()

		#Verifica se terminou mal
		if grafName == -1 or terminou_bem == -1:
			plt.close()
			return -1

		guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)
		plt.close()

	return 0




def ficheiros_juntos(dirImagens, folder_name, tipoGrafico, dicio, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, maxL, fig):
	"""
	Le os ficheiros comos valores. Chama ``desenho()`` para fazer o plot. Aplica as especifiçaões do grafico presentes no .conf em ``Specs = {}``.
	Guarda os graficos gerados chamaando ``guardaGrafico()``   

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``
	
	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type dicio: dict
	:param dicio: especificções do ficheiro. Ex: ``dicio = {'foo1': {'bins': 'range(4)', 'Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}``

	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 


	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type Freqmax: int
	:param Freqmax: valor que se repete mais vezes em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:type maxL: int
	:param maxL: representa o tamnaho do maior ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria
	
	:type fig: int
	:param fig: numero - 1 das ``plt.figure()`` que vamos criar e consequentemente guardar 

	:returns: -1 caso existam erros, 0 caso contrario

	"""


	if not __debug__:
		print("FICHEIROS JUNTOS")

	for i,fileName in enumerate(dicio):
		dirF = os.path.join(dirFiles,fileName+'.txt')
		f = open(dirF,'r')
		data =  np.array( list(map( lambda x:float(x),f.read().split() )) )

		if not __debug__:
			print("Data :",data)
			print('fmt :',dicio[fileName])

		if "Specs" in dicio[fileName]:
			#ignoramos Specs especificos se formos fazer plot dos files juntos
			dicio[fileName].pop("Specs")


		#copia necessaria pk s é alterado no desenho e naformataçao e 
		# o especificacoes que vai para o desenho tem de ser o mesmo que vai para a formatacao
		if "Specs" in confTipoGrafico:
			#especificacoes = confTipoGrafico["Specs"]
			especificacoes =  copy.deepcopy(confTipoGrafico["Specs"])
		else:
			especificacoes = {}

		faux = desenho(tipoGrafico, data, dicio[fileName], confTipoGrafico, i, len(dicio), numPilares, especificacoes, fileName, minY, maxY, bar_empilha)
		
		#Verifica se terminou mal
		if faux == -1:

			#antes de sair fecha todas as janelas
			for j in range(fig):
				plt.close()
				
			plt.close()
			return -1


		#ficheiros maiores fazem mais figuras (queremos guardar todas)
		if faux > fig :
			fig = faux


		f.close()

	#se no plot do Bar foi gerados + de 1 fig 
	#Barras LadoALado
	if fig != 0:
		
		for j in range(fig):


			plt.figure(j)
			if "Specs" in confTipoGrafico:
				grafName = formatacaoSpecs(copy.deepcopy(especificacoes), folder_name, "", tipoGrafico, confTipoGrafico, grafs, j, maxY, maxL, Freqmax, numPilares)
			
				#Verifica se terminou mal
				if grafName == -1:

					#antes de sair fecha todas as janelas
					for j in range(j,fig):
						plt.close()
						
					plt.close()
					return -1


				grafName = grafName + "[fig "+ str(j) +"]"
			else:
				grafName = folder_name + "[fig "+ str(j)+"]"


			guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)
			#plt.clf()
			plt.close()

	else:
		if "Specs" in confTipoGrafico:
			grafName = formatacaoSpecs(especificacoes, folder_name, "", tipoGrafico, confTipoGrafico, grafs, 0, maxY, maxL, Freqmax, numPilares)
			
			#Verifica se terminou mal
			if grafName == -1:
				plt.close()
				return -1

		else:
			grafName = folder_name
		

		guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)					
		plt.close()

	return 0





def tudo_separados(dirImagens, folder_name, tipoGrafico, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, files):
	"""
	Le os ficheiros comos valores. Chama ``desenho()`` para fazer o plot. Aplica as especifiçaões do grafico presentes no .conf em ``Specs = {}``.
	Guarda os graficos gerados chamaando ``guardaGrafico()``   

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``
	
	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 

	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type Freqmax: int
	:param Freqmax: valor que se repete mais vezes em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:type files: list
	:param files:  lista dos ficheiros com valores para criar os graficos. Ex: ``files = ['timenewformulation2.txt', 'timenewformulation0.txt', 'timenewformulation1.txt']``

	:returns: -1 caso existam erros, 0 caso contrario

	"""


	if not __debug__:
		print("TUDO SEPARADOS")


	for i,fileName in enumerate(files):
		dirF = os.path.join(dirFiles,fileName)
		f = open(dirF,'r')
		data =  np.array( list(map( lambda x:float(x),f.read().split() )) )


		#copia necessaria pk s é alterado no desenho e na formataçao e 
		# o especificacoes que vai para o desenho tem de ser o mesmo que vai para a formatacao
		if "Specs" in confTipoGrafico:
			#especificacoes = confTipoGrafico["Specs"]
			especificacoes =  copy.deepcopy(confTipoGrafico["Specs"])
		else:
			especificacoes = {}


		terminou_bem = desenho(tipoGrafico, data, {}, confTipoGrafico, i, len(files), numPilares, especificacoes, fileName[:-4], minY, maxY, bar_empilha)

		f.close()
		
		#Verifica se terminou mal
		if terminou_bem == -1:
			plt.close()
			return -1

		if "Specs" in confTipoGrafico:
			#grafName = formatacaoSpecs(copy.deepcopy(especificacoes),folder_name,fileName[:-4],tipoGrafico,confTipoGrafico,grafs,i,maxY,len(data),Freqmax,numPilares)
			grafName = formatacaoSpecs(especificacoes, folder_name, fileName[:-4], tipoGrafico, confTipoGrafico, grafs, i, maxY, len(data), Freqmax, numPilares)

			#Verifica se terminou mal
			if grafName == -1:

				plt.close()
				return -1

		else:
			grafName = fileName[:-4]

		guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)

		plt.close()

	return 0

def tudo_juntos(dirImagens, folder_name, tipoGrafico, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, maxL, fig, files):
	"""
	Le os ficheiros comos valores. Chama ``desenho()`` para fazer o plot. Aplica as especifiçaões do grafico presentes no .conf em ``Specs = {}``.
	Guarda os graficos gerados chamaando ``guardaGrafico()``   

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``
	
	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type bar_empilha: list of list of int
	:param bar_empilha: cada linha representa um ficheiro; cada coluna representa uma barra do plot.bar(); os valores é o y começamos a fazer plot das barras de um ficheiro

	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type confTipoGrafico: dict
	:param confTipoGrafico: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``confTipoGrafico = {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 'range(4)', 'Specs': {}}, 
		'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}, 'Specs': {'value': {'precisao': 
		'3', 'fontsize': '7'}, 'legend': {'loc': 'upper left'}}}``

	:type numPilares: int
	:param numPilares: em ``plt.bar()`` é o numero de barras que aparecem numa figura. Default é 4

	:type minY: float
	:param minY: menor valor dos y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria 

	:type maxY: float
	:param maxY: maior valor do y de entre todos os ficheiros que vamos fazer plot dentro de uma  diretoria

	:type Freqmax: int
	:param Freqmax: valor que se repete mais vezes em um ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria

	:type maxL: int
	:param maxL: representa o tamnaho do maior ficheiro de entre todos os ficheiros que vamos fazer plot dentro de uma diretoria
	
	:type fig: int
	:param fig: numero - 1 das ``plt.figure()`` que vamos criar e consequentemente guardar 

	:type files: list
	:param files:  lista dos ficheiros com valores para criar os graficos. Ex: ``files = ['timenewformulation2.txt', 'timenewformulation0.txt', 'timenewformulation1.txt']``

	:returns: -1 caso existam erros, 0 caso contrario

	"""



	if not __debug__:
		print("TUDO JUNTOS")
			
	for i,fileName in enumerate(files):
		dirF = os.path.join(dirFiles,fileName)
		f = open(dirF,'r')
		data =  np.array( list(map( lambda x:float(x),f.read().split() )) )


		#copia necessaria pk especificacoes é alterado no desenho e naformataçao e 
		# o especificacoes que vai para o desenho tem de ser o mesmo que vai para a formatacao
		if "Specs" in confTipoGrafico:
			#especificacoes = confTipoGrafico["Specs"]
			especificacoes =  copy.deepcopy(confTipoGrafico["Specs"])
		else:
			especificacoes = {}


		faux = desenho(tipoGrafico, data, {}, confTipoGrafico, i, len(files), numPilares, especificacoes, fileName[:-4], minY, maxY, bar_empilha)
		
		#Verifica se terminou mal
		if faux == -1:
			plt.close()
			return -1


		#ficheiros maiores farem mais figuras (queremos guardar todas elas)
		if faux > fig :
			fig = faux


		f.close()


	if fig != 0:
		for j in range(fig):
			plt.figure(j)

			if "Specs" in confTipoGrafico:
				grafName = formatacaoSpecs(copy.deepcopy(especificacoes), folder_name, "", tipoGrafico, confTipoGrafico, grafs, j, maxY, maxL, Freqmax, numPilares)

				#Verifica se terminou mal
				if grafName == -1:

					#antes de sair fecha todas as janelas
					for j in range(j,fig):
						plt.close()
					
					plt.close()
					return -1


				grafName = grafName + "[fig "+str(j)+"]"
			else:
				grafName = folder_name + "[fig "+str(j)+"]"

			guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)
			plt.close()
	else:
		if "Specs" in confTipoGrafico:
			grafName = formatacaoSpecs(especificacoes, folder_name, "", tipoGrafico, confTipoGrafico, grafs, 0, maxY, maxL, Freqmax, numPilares)

			#Verifica se terminou mal
			if grafName == -1:

				plt.close()
				return -1

		else:
			grafName = folder_name

		guardaGrafico(confTipoGrafico, dirImagens, folder_name, grafName)
		plt.close()

	return 0






#files: lista do nome de fixheiros (contem  a extensão .txt) na diretoria folder_name
#tipoGrafico: tipoGrafico a executar
# c é a parte do .conf que corresponde à pasta folder_name 
#folder name é o nome da diretoria dos ficheios (tem a extensao do .conf)
def customAuxiliar(files, tipoGrafico, c, folder_name, dirFiles, dirImagens, grafs):
	"""
	vai verificar se nao temos combinações invalidas de especificaçoes nos .conf Ex:"separa" = True e "ladoAlado" = True

	vai correr funçoes auxiliares (``devolvePropriedades()``) enquanto temos acesso aos valores de todos os ficheiros

	vai averiguar se foi especificado fazer plot dos graficos todos ou só de alguns e se estes vao aparecer na mesma ``plt.figura()`` 
	ou em ``plt.figura()`` diferentes. 
	Chamamos assim uma destas funçoes ``ficheiros_separados(), ficheiros_juntos(), tudo_separado(), tudo_juntos()`` 


	:type files: list of str
	:param files: nomes dos ficheiros que vamos usar para criar graficos. Ex: ``files = ['timenewformulation2.txt', 'timenewformulation0.txt', 'timenewformulation1.txt']``

	:type tipoGrafico: str
	:param tipoGrafico: ajudanos a saber que tipo de grafico vamos criar. Ex: `` tipoGrafico = "Linhas"``

	:type c: dict
	:param c: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``c = {'Hist': {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 
		'range(4)','Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3':etc``

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``
	
	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type grafs: list of str
	:param grafs: lista que contem os tipos de graficos que conseguimos criar Ex: ``grafs = ["Linhas", "Barras", "Hist"]``

	:returns: -1 caso existam erros, 0 caso contrario

	"""
	

	
	confTipoGrafico = c[tipoGrafico]

	if tipoGrafico == grafs[1] and "numPilares" in confTipoGrafico: 
		try:
			numPilares = int(confTipoGrafico["numPilares"])
		except (ValueError):
			print("[ERRO] Problema nas Especificaçoes de Cabecalho\nEm ",folder_name, " numPilares deve ser um int\nEx: numPilares = 5\nLeaving")
			return -1


	else:
		numPilares = 4

	#Linhas
	if tipoGrafico == grafs[0]:
		if  "ladoAlado" in confTipoGrafico or "empilha" in confTipoGrafico or "numPilares" in confTipoGrafico:
			print("[ERRO] Conflito nas Especificaçoes\nTem especificacoes de Cabecalho que nao pertencem a um grafico de Linhas em : ",folder_name, "\nLeaving")
			return -1

	#Barras
	elif tipoGrafico == grafs[1]:

		if("separa" in confTipoGrafico and confTipoGrafico["separa"] == "True" ) and "ladoAlado" in confTipoGrafico and confTipoGrafico['ladoAlado'] == 'True':
			print("[ERRO] Conflito nas Especificaçoes\nTem 'separa' e 'ladoAlado' no memsmo plot de Barras:",folder_name, "\nLeaving")
			return -1

		elif ("empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True")  and "ladoAlado" in confTipoGrafico and confTipoGrafico['ladoAlado'] == 'True':
			print("[ERRO] Conflito nas Especificaçoes\nTem 'empilha' e 'ladoAlado' no memsmo plot de Barras:",folder_name, "\nLeaving")
			return -1

		elif ("empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True")  and "separa" in confTipoGrafico and confTipoGrafico["separa"] == 'True':
			print("[ERRO] Conflito nas Especificaçoes\nTem 'empilha' e 'separa' no memsmo plot de Barras:" + folder_name+"\nLeaving")
			return -1

	#Hist
	elif tipoGrafico == grafs[2]:
		if  "ladoAlado" in confTipoGrafico or "empilha" in confTipoGrafico or "numPilares" in confTipoGrafico:
			print("[ERRO] Conflito nas Especificaçoes\nTem especificacoes de Cabecalho que nao pertencem a um grafico de Histograma em : ",folder_name, "\nLeaving")
			return -1




	#indicador do numero de plt.figuras() que famos ter de guardar 
	#	nos graficos LadoAlado (fora disso e sempre == 0)
	fig = 0


	#ALGUNS FICHEIROS
	if "Ficheiros" in confTipoGrafico:

		#configuraçoes particulares dos ficheiro. dicio = {'foo1': {'bins': 'range(4)', 'Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3': {'Specs': {}}}
		dicio = confTipoGrafico["Ficheiros"]


		#obtemos alguns valores para nos auxiliar
		minY,maxY,maxL,Freqmax,listaDataFicheiros = devolvePropriedades(dicio, dirFiles, False, confTipoGrafico)

		# matriz de auxiliu quando fazemos plot.bar de graficos empilhados 
		# cada linha representa um ficheiro; cada coluna representa uma barra; os valores é onde começamos a fazer plot das barras de um ficheiro
		bar_empilha = []
		if tipoGrafico == "Barras" and ("empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True"):
			bar_empilha = preparaArrayEmpilhado(maxL, len(dicio), listaDataFicheiros)

		#ficheiros separados------------------------------
		if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True":
			terminou_bem = ficheiros_separados(dirImagens, folder_name, tipoGrafico, dicio, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax)

		#ficheiros juntos------------------------------
		else:
			terminou_bem = ficheiros_juntos(dirImagens, folder_name, tipoGrafico, dicio, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, maxL, fig)



    #TODOS FICHEIROS
	else:

		#obtemos alguns valores para nos auxiliar
		minY,maxY,maxL,Freqmax,listaDataFicheiros = devolvePropriedades(files, dirFiles, True, confTipoGrafico)
	
		# matriz de auxiliu quando fazemos plot.bar de graficos empilhados 
		# cada linha representa um ficheiro; cada coluna representa uma barra; os valores é onde começamos a fazer plot das barras de um ficheiro
		bar_empilha = []
		if tipoGrafico == "Bar" and ("empilha" in confTipoGrafico and confTipoGrafico["empilha"] == "True"):
			bar_empilha = preparaArrayEmpilhado(maxL,len(files),listaDataFicheiros)
		


		#Total separados-----------------------------------------
		if "separa" in confTipoGrafico and confTipoGrafico["separa"] == "True":
			terminou_bem = tudo_separados(dirImagens, folder_name, tipoGrafico, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, files)
			

		#Total juntos -------------------------------------------
		else:
			terminou_bem = tudo_juntos(dirImagens, folder_name, tipoGrafico, bar_empilha, dirFiles, confTipoGrafico, numPilares, minY, maxY, Freqmax, maxL, fig, files)

	if terminou_bem == 0:
		return 0		
	else:
		return -1








# c é a parte do .conf que corresponde à pasta folder_name 
#dirFiles é a diretoria que contêm ficheiros .txt
#dirImagens é a diretoria com os folder com o mesmo nome que dirFiles
#folder_name é o nome da diretoria no .conf
#grafs é a lista que contem o tipo de graficos
def custom(c, folder_name, dirFiles, dirImagens, grafs):
	"""
	Função vai ser chamada para cada diretoria que existe no .conf .
	Vai verificar que tipo de graficos temos para criar e chama a função ``customAuxiliar`` 
	

	:type c: dict
	:param c: secçao do .conf que corresponde uma das nossas diretorias que 
		tem informaçao para gerar graficos. Ex: ``c = {'Hist': {'separa': 'True', 'Ficheiros': {'foo1': {'bins': 
		'range(4)','Specs': {}}, 'foo2': {'Specs': {'bins': ['range(4', '12)']}}, 'foo3':etc``

	:type folder_name: str
	:param folder_name: Nome do diretoria que vamos fazer os graficos Ex: ``folder_name = barrasTeste.2``

	:type dirFiles: str
	:param dirFiles: Path para a diretoria do ficheiros que tem valores dos graficos

	:type dirImages: str
	:param dirImages: Path para a diretoria onde as pastas dos graficos vao ser guardados

	:type grafs: list of str
	:param grafs: lista que contem os tipos de graficos que conseguimos criar Ex: ``grafs = ["Linhas", "Barras", "Hist"]``
	"""


	#Lista de ficheiros .txt com os valores para os graficos
	files = next(os.walk(dirFiles))[2]



	if not __debug__:
		print("Files in "+folder_name[:-2]+" :",files)

	#verifica se existem ficheiros de dados na diretoria
	if len(files) != 0:
		#plot do grafico de--------Linhas
		if grafs[0] in c:
			if not __debug__:
				print("fez linhas")
			terminou_bem = customAuxiliar(files, grafs[0], c, folder_name, dirFiles, dirImagens, grafs)
			if terminou_bem == 0:
				print("Terminou com sucesso Linhas ", folder_name)

		#plot do grafico de-------- Barras
		elif grafs[1] in c:
			if not __debug__:
				print("fez bar")
			terminou_bem = customAuxiliar(files, grafs[1], c, folder_name, dirFiles, dirImagens, grafs)
			if terminou_bem == 0:
				print("Terminou com sucesso Barras ", folder_name)

		#plot do grafico de ---------Histograma
		elif grafs[2] in c:
			if not __debug__:
				print("fez hist")
			terminou_bem = customAuxiliar(files, grafs[2], c, folder_name, dirFiles, dirImagens, grafs)
			if terminou_bem == 0:
				print("Terminou com sucesso Hist ", folder_name)







    
if __name__ == "__main__":
    
	dirData = os.path.join('..',"data")
	dirImagens = os.path.join('..',"imagens")
	grafs = ["Linhas","Barras","Hist"]

	#Lista de todas as diretoriasque contem ficheiros de dados que vamos fazer plot
	#Ex: dataFolderList = ['barrasTeste', 'grafNoe', 'Nova pasta0', 'Nova pasta22', 'Time']
	dataFolderList = next(os.walk(dirData))[1]
	if not __debug__:
		print("DataFolderList:",dataFolderList)
    
	#Faz o parssing do ficheiro de configuracao 
	#Ex: config = {'Time.1': {'Linhas': {'substitui': 'False', 'Ficheiros': {'timenewformulation0': 
	# {'color': '#0000ff', etc...
	config = ConfigObj(os.path.join('..',"graf.conf"))    


	#So faz plot das folder que estiveres assinaladas no .conf
	for folder_name in config:
		#Ao nome do folder retimamos os caracteres adicionais da chave
		#Ex: Time.1 -> Time  
		if folder_name[:-2] in dataFolderList:
			custom(config[folder_name],folder_name,os.path.join(dirData,folder_name[:-2]),dirImagens,grafs)





