"""
Populacion: Lista de genomas
Generacion: Set de populaciones

"""

import random
import sys

N_REINAS = 8
MAX_FITNESS = 28 	# Sin posiciones invalidas en tablero 8x8 con 8 reinas
GENERACION_LIMITE = 100000
NUM_TABLEROS = 1000
BANDERA_MUTACION = True
MUTACION = 1/NUM_TABLEROS

class Tablero:
	def __init__(self):
		self.genotipo: bytearray = None
		self.fitness: float = None
		self.sobrevivencia: float = None

	# Secuencia de cromosomas / genotipo / posible solucion
	def set_genotipo(self, genotipo: bytearray):
		self.genotipo = genotipo

	# fitness == 28, no hay posiciones invalidas
	def set_fitness(self, fitness: float):
		self.fitness = fitness

	def set_sobrevivencia(self, sobrevivencia: float):
		self.sobrevivencia = sobrevivencia

	def get_tablero(self):
		return {
			'genotipo': genotipo, 
			'fitness': fitness, 
			'sobrevivencia': sobrevivencia
		}

def get_padres(sum_fitness: float, populacion: list):
	globals()	
	padre_1: Tablero = None
	padre_2: Tablero = None

	while True:
		random_sobrevivencia = random.random()
		random_populacion = [tablero for tablero in populacion if tablero.sobrevivencia <= random_sobrevivencia]

		try:
			padre_1 = random_populacion[0]
			break
		except:
			pass

	while True:
		random_sobrevivencia = random.random()
		random_populacion = [tablero for tablero in populacion if tablero.sobrevivencia <= random_sobrevivencia]

		try:
			random_indice = random.randrange(len(random_populacion))
			padre_2 = random_populacion[random_indice]

			if padre_2 != padre_1:
				break
			else:
				#print("Padres iguales")
				continue
		except:
			#print("Excepcion")
			continue

	if padre_1 is not None and padre_2 is not None:
		return padre_1, padre_2
	else:
		sys.exit(-1)

def cruzar(padre_1: Tablero, padre_2: Tablero):
	globals()
	num_cromosomas = len(padre_1.genotipo)
	corte = random.randrange(num_cromosomas)

	hijo = Tablero()
	hijo.genotipo.extend(padre_1.genotipo[0:corte])
	hijo.genotipo.extend(padre_2.genotipo[corte:])
	hijo.set_fitness(fitness(hijo.genotipo))
	hijo.set_sobrevivencia((padre_1.sobrevivencia + padre_2.sobrevivencia)/2)

	return hijo


def mutacion(hijo: Tablero):
	"""	
	- according to genetic theory, a mutation will take place
	when there is an anomaly during cross over state

	- since a computer cannot determine such anomaly, we can define 
	the probability of developing such a mutation 

	"""
	
	num_cromasomas = len(hijo.genotipo)
	cromasoma = random.randrange(num_cromasomas)
	hijo.genotipo[cromasoma] = random.randrange(num_cromasomas)

	return hijo

def seleccion_natural(generacion: int, populacion: list):
	globals()
	nueva_populacion = []

	# parent is decided by random probability of sobrevivencia.
	# since the fitness of each board position is an integer >0, 
	# we need to normaliza the fitness in order to find the solution
	sum_fitness: float = sum([tablero.fitness for tablero in populacion])

	for tablero in populacion:
		tablero.set_sobrevivencia(tablero.fitness/sum_fitness)

	print(f'Ejecutando generacion genetica: {generacion}')

	for _ in range(NUM_TABLEROS):
		padre_1, padre_2 = get_padres(sum_fitness, populacion)
		# print("Padres generados : ", padre_1, padre_2)

		hijo = cruzar(padre_1, padre_2)

		if(BANDERA_MUTACION and hijo.sobrevivencia < MUTACION):
			hijo = mutacion(hijo)

		nueva_populacion.append(hijo)
		
	return nueva_populacion

def expandir_byte(byte):
	return f'{byte:b}'.zfill(8)

def ataques_de_reinas(genotipo: bytearray):
	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	filas_con_reina = []
	columnas_con_reina = []

	for fila in range(N_REINAS):
		bits_en_fila = expandir_byte(genotipo[fila])

		for columna in range(N_REINAS):
			if(bits_en_fila[columna] == '1'):
				filas_con_reina.append(fila)
				columnas_con_reina.append(columna)

	ataques_horizontales = len(filas_con_reina) - len(set(filas_con_reina))
	ataques_verticales = len(columnas_con_reina) - len(set(columnas_con_reina))
	
	ataques_diagonales = 0

	for i in range(N_REINAS):
		fila_1 = filas_con_reina[i]
		columna_1 = columnas_con_reina[i]

		for j in range(i+1, N_REINAS):
			fila_2 = filas_con_reina[j]
			columna_2 = columnas_con_reina[j]

			if fila_2 - fila_1 == abs(columna_1 - columna_2):
				ataques_diagonales += 1

	return ataques_horizontales + ataques_verticales + ataques_diagonales


def fitness(genotipo: bytearray):
	"""
	returns 28 - <number of conflicts>
	to test for conflicts, we check for 
	 -> row conflicts
	 -> columnar conflicts
	 -> diagonal conflicts
	 
	The ideal case can yield upton 28 arrangements of non attacking pairs.
	for generacion 0 -> there are 7 non attacking queens
	for generacion 1 -> there are 6 no attacking queens ..... and so on 

	Therefore max fitness = 7 + 6+ 5+4 +3 +2 +1 = 28

	hence fitness val returned will be 28 - <number of clashes>

	"""
	global MAX_FITNESS

	posiciones_invalidas = ataques_de_reinas(genotipo)

	return MAX_FITNESS - posiciones_invalidas

def generar_posiciones_tablero(btsr_posiciones):
	num_bits = len(btsr_posiciones)
	return ''.join(random.sample(list(btsr_posiciones), num_bits))


def generar_genotipo():
	global N_REINAS

	num_filas_columnas = N_REINAS * N_REINAS
	bstr_posicion_reina = '1' * N_REINAS
	bstr_posicion_vacia = '0' * (num_filas_columnas - N_REINAS)
	
	bstr_posiciones_tablero = generar_posiciones_tablero(bstr_posicion_vacia + bstr_posicion_reina)

	cromosomas: bytearray = int(bstr_posiciones_tablero, 2).to_bytes(N_REINAS, 'big')

	return cromosomas

def generar_populacion(num_tableros: int = 100):
	'''
	Generar populacion con posibles soluciones
	'''
	# Lista de objetos Tablero
	populacion = [Tablero() for _ in range(num_tableros)]

	for tablero in populacion:
		tablero.set_genotipo(generar_genotipo()) # Secuencia de cromosomas / genotipo / posible solucion
		tablero.set_fitness(fitness(tablero.genotipo))

	print("Tamaño de populacion: ", num_tableros)

	return populacion

def parar_algoritmo(populacion: list):
	globals()
	parar = False

	# fitness = Maximo de posiciones invalidas (28) - posiciones invalidas en solucion
	valores_fitness = [tablero.fitness for tablero in populacion]

	# Maximo de posiciones invalidas en tablero 8x8 es 28
	# Si fitness == 28, no hubieron reinas en posiciones invalidas
	if MAX_FITNESS in valores_fitness: 
		parar = True
	elif GENERACION_LIMITE == generacion:
		parar = True

	return parar

def imprimir_soluciones(populacion: list):
	for tablero in populacion:
		if tablero.fitness == MAX_FITNESS: # Sin posiciones invalidos
			for cromosoma in tablero.genotipo:
				print(expandir_byte(cromosoma))

			print('\n')

if __name__ == "__main__":
	generacion = 0
	populacion = generar_populacion(NUM_TABLEROS) 	# Lista de objetos Tablero

	while not parar_algoritmo(populacion):
		populacion = seleccion_natural(generacion, populacion)
		generacion += 1 

	print("# de generacion: ", generacion)

	imprimir_soluciones(populacion)