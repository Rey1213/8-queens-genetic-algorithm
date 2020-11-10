"""
Populacion: Lista de genomas
Generacion: Set de populaciones

"""

import random
import sys

NUM_REINAS = 8
MAX_FITNESS = 28 	# Sin posiciones invalidas en tablero 8x8 con 8 reinas
GENERACION_LIMITE = 100000
NUM_POPULACIONES = 1000
BANDERA_MUTACION = True
MUTACION = 1/NUM_POPULACIONES

class Tablero:
	def __init__(self):
		self.genoma = []
		self.fitness = 0.0
		self.sobrevivencia = 0.0

	# Secuencia de cromosomas / genoma / posible solucion
	def set_genoma(self, genoma: list):
		self.genoma = genoma

	# fitness == 28, no hay posiciones invalidas
	def set_fitness(self, fitness: float):
		self.fitness = fitness

	def set_sobrevivencia(self, sobrevivencia: float):
		self.sobrevivencia = sobrevivencia

	def get_tablero(self):
		return {
			'genoma': genoma, 
			'fitness': fitness, 
			'sobrevivencia': sobrevivencia
		}

def ataques_de_reinas(genoma: list = []):
	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	tablero_fila_columna = len(genoma)
	ataques_fila_columna = len(genoma) - len(set(genoma))


	# calculate diagonal clashes
	for fila_1 in range(tablero_fila_columna):
		for fila_2 in range(tablero_fila_columna):
			if (fila_1 != fila_2):
				columna_1 = genoma[fila_1]
				columna_2 = genoma[fila_2]

				dx = abs(columna_1 - columna_2)
				dy = abs(fila_1 - fila_2)

				if(dx == dy):

					ataques_diagonales += 1

	return ataques_fila_columna + ataques_diagonales

def fitness(genoma: list = []):
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

	posiciones_invalidas = ataques_de_reinas(genoma)

	return MAX_FITNESS - posiciones_invalidas	


def generar_genoma():
	global NUM_REINAS

	# Estados de tablero generados al azar [0,7]
	cromosomas = [random.randrange(NUM_REINAS) for _ in range(NUM_REINAS)]

	return cromosomas

# Generar populacion de posibles soluciones
def generar_populaciones(num_populaciones: int = 100):
	# Lista de objetos Tablero
	populaciones = [Tablero() for _ in range(num_populaciones)]

	for populacion in populaciones:
		populacion.set_genoma(generar_genoma()) # Secuencia de cromosomas / genoma / posible solucion
		populacion.set_fitness(fitness(populacion.genoma))

	print("# de populaciones: ", num_populaciones)

	return populaciones


def get_padres(sum_fitness: float, populaciones: list):
	globals()	
	padre_1: Tablero = None
	padre_2: Tablero = None

	while True:
		random_sobrevivencia = random.random()
		random_populaciones = [populacion for populacion in populaciones if populacion.sobrevivencia <= random_sobrevivencia]

		try:
			padre_1 = random_populaciones[0]
			break
		except:
			pass

	while True:
		random_sobrevivencia = random.random()
		random_populaciones = [populacion for populacion in populaciones if populacion.sobrevivencia <= random_sobrevivencia]

		try:
			random_indice = random.randrange(len(random_populaciones))
			padre_2 = random_populaciones[random_indice]

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
	num_cromosomas = len(padre_1.genoma)
	corte = random.randrange(num_cromosomas)

	hijo = Tablero()
	hijo.genoma.extend(padre_1.genoma[0:corte])
	hijo.genoma.extend(padre_2.genoma[corte:])
	hijo.set_fitness(fitness(hijo.genoma))
	hijo.set_sobrevivencia((padre_1.sobrevivencia + padre_2.sobrevivencia)/2)

	return hijo


def mutacion(hijo: Tablero):
	"""	
	- according to genetic theory, a mutation will take place
	when there is an anomaly during cross over state

	- since a computer cannot determine such anomaly, we can define 
	the probability of developing such a mutation 

	"""
	
	num_cromasomas = len(hijo.genoma)
	cromasoma = random.randrange(num_cromasomas)
	hijo.genoma[cromasoma] = random.randrange(num_cromasomas)

	return hijo

def seleccion_natural(generacion: int, populaciones: list):
	globals()
	nueva_populacion = []

	# parent is decided by random probability of sobrevivencia.
	# since the fitness of each board position is an integer >0, 
	# we need to normaliza the fitness in order to find the solution
	sum_fitness: float = sum([populacion.fitness for populacion in populaciones])

	for populacion in populaciones:
		populacion.set_sobrevivencia(populacion.fitness/sum_fitness)

	print(f'Ejecutando generacion genetica: {generacion}')

	for _ in range(NUM_POPULACIONES):
		padre_1, padre_2 = get_padres(sum_fitness, populaciones)
		# print("Padres generados : ", padre_1, padre_2)

		hijo = cruzar(padre_1, padre_2)

		if(BANDERA_MUTACION and hijo.sobrevivencia < MUTACION):
			hijo = mutacion(hijo)

		nueva_populacion.append(hijo)
		
	return nueva_populacion


def parar_algoritmo(populaciones: list):
	globals()
	parar = False

	# fitness = Maximo de posiciones invalidas (28) - posiciones invalidas en solucion
	valores_fitness = [populacion.fitness for populacion in populaciones]

	# Maximo de posiciones invalidas en tablero 8x8 es 28
	# Si fitness == 28, no hubieron reinas en posiciones invalidas
	if MAX_FITNESS in valores_fitness: 
		parar = True
	elif GENERACION_LIMITE == generacion:
		parar = True

	return parar

def imprimir_soluciones(populaciones: list = []):
	for populacion in populaciones:
		if populacion.fitness == MAX_FITNESS: # Sin posiciones invalidos
			print(populacion.genoma)

if __name__ == "__main__":
	generacion = 0
	populaciones = generar_populaciones(NUM_POPULACIONES) 	# Lista de objetos Tablero

	while not parar_algoritmo(populaciones):
		populaciones = seleccion_natural(generacion, populaciones)
		generacion += 1 

	print("# de generacion: ", generacion)

	imprimir_soluciones(populaciones)