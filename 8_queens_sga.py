"""
Populacion: Lista de genomas
Generacion: Set de populaciones

"""

import random
import sys

NUM_REINAS = 8
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

def ataques_de_reinas(genotipo: list = []):
	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	tablero_fila_columna = len(genotipo)
	ataques_fila_columna = len(genotipo) - len(set(genotipo))


	# calculate diagonal clashes
	for fila_1 in range(tablero_fila_columna):
		for fila_2 in range(tablero_fila_columna):
			if (fila_1 != fila_2):
				columna_1 = genotipo[fila_1]
				columna_2 = genotipo[fila_2]

				dx = abs(columna_1 - columna_2)
				dy = abs(fila_1 - fila_2)

				if(dx == dy):

					ataques_diagonales += 1

	return ataques_fila_columna + ataques_diagonales

def fitness(genotipo: list = []):
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

def imprimir_soluciones(populacion: list = []):
	for tablero in populacion:
		if tablero.fitness == MAX_FITNESS: # Sin posiciones invalidos
			print(tablero.genotipo)

def generar_genotipo():
	global NUM_REINAS
	tablero_filas = NUM_REINAS
	tablero_columnas = NUM_REINAS

	# indice en bytearray = fila
	# indice de bit en byte = columna
	# bit {0,1} = si hay o no reina en posición del tablero
	cromosomas = bytearray([random.getrandbits(tablero_columnas) for _ in range(tablero_filas)])

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

if __name__ == "__main__":
	generacion = 0
	populacion = generar_populacion(NUM_TABLEROS) 	# Lista de objetos Tablero

	while not parar_algoritmo(populacion):
		populacion = seleccion_natural(generacion, populacion)
		generacion += 1 

	print("# de generacion: ", generacion)

	imprimir_soluciones(populacion)