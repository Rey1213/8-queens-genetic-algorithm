"""
Populacion: Lista de genomas
Generacion: Set de populaciones

"""

import random
import sys

N_REINAS = 8
MAX_POSICIONES_INVALIDAS = 28
MAX_FITNESS = 28 	# Sin posiciones invalidas en tablero 8x8 con 8 reinas
GENERACION_LIMITE = 100000
NUM_TABLEROS = 1000
BANDERA_MUTACION = True
CRUZAR = random.uniform(0.6, 0.9) # p_c entre 0.6 y 0.9
MUTACION = random.uniform(1/NUM_TABLEROS, 1/(N_REINAS*N_REINAS)) # p_m entre 1/pop_size y 1/chromosome_length

class Tablero:
	def __init__(self):
		self.genotipo: bytearray = []
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

def bit_flip(bit):
	return str(abs(int(bit) - 1))

def mutar(hijo: Tablero):
	"""	
	- according to genetic theory, a mutation will take place
	when there is an anomaly during cross over state

	- since a computer cannot determine such anomaly, we can define 
	the probability of developing such a mutation 

	"""
	cromasomas = ''

	bstr_genotipo = bytearray_to_bstr(hijo.genotipo)
	
	for bit in bstr_genotipo:
		cromasomas += bit if random.random() > MUTACION else bit_flip(bit)

	genotipo: bytearray = bstr_to_bytearray(cromasomas)
	
	hijo.genotipo = genotipo

def bytearray_to_bstr(bytearray):
	return ''.join([expandir_byte(byte) for byte in bytearray])

def cruzamiento_1_punto(padre_1: Tablero, padre_2: Tablero):
	globals()
	num_bits = N_REINAS * N_REINAS
	corte = random.randrange(num_bits)

	bstr_genotipo_p1 = bytearray_to_bstr(padre_1.genotipo)
	bstr_genotipo_p2 = bytearray_to_bstr(padre_2.genotipo)

	hijo_1_genotipo = bstr_to_bytearray(
		bstr_genotipo_p1[0:corte] +
		bstr_genotipo_p2[corte:]
	)

	hijo_2_genotipo = bstr_to_bytearray(
		bstr_genotipo_p2[0:corte] +
		bstr_genotipo_p1[corte:]
	)

	hijo_1 = Tablero()
	hijo_1.set_genotipo(hijo_1_genotipo)
	hijo_1.set_fitness(fitness(hijo_1.genotipo))

	hijo_2 = Tablero()
	hijo_2.set_genotipo(hijo_2_genotipo)
	hijo_2.set_fitness(fitness(hijo_2.genotipo))

	return hijo_1, hijo_2

def seleccionar_padres(populacion: list):
	return random.choices(
		population = populacion,
		weights = [tablero.fitness for tablero in populacion],
		k = 2
	)

def generar_nueva_generacion(generacion: int, populacion: list):
	globals()
	nueva_populacion = []

	# parent is decided by random probability of sobrevivencia.
	# since the fitness of each board position is an integer >0, 
	# we need to normaliza the fitness in order to find the solution
	#sum_fitness: float = sum([tablero.fitness for tablero in populacion])

	#for tablero in populacion:
	#	tablero.set_sobrevivencia(tablero.fitness/sum_fitness)

	print(f'Ejecutando generacion genetica: {generacion}')

	for _ in range(int(NUM_TABLEROS/2)):
		padre_1, padre_2 = seleccionar_padres(populacion)
		# print("Padres generados : ", padre_1, padre_2)

		hijo_1, hijo_2 = [padre_1, padre_2] if random.random() < CRUZAR else cruzamiento_1_punto(padre_1, padre_2) 

		if(BANDERA_MUTACION):
			mutar(hijo_1)
			mutar(hijo_2)

		nueva_populacion.append(hijo_1)
		nueva_populacion.append(hijo_2)
		
	return nueva_populacion

def expandir_byte(byte):
	return f'{byte:b}'.zfill(8)

def ataques_de_reinas(genotipo: bytearray):
	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	filas_con_reina = []
	columnas_con_reina = []
	reinas_en_tablero = 0

	for fila in range(N_REINAS):
		bits_en_fila = expandir_byte(genotipo[fila])
		
		for columna in range(N_REINAS):
			if(bits_en_fila[columna] == '1'):
				filas_con_reina.append(fila)
				columnas_con_reina.append(columna)
				reinas_en_tablero += 1

	if reinas_en_tablero != N_REINAS: # Si hay mutacion en genotipo
		return MAX_POSICIONES_INVALIDAS

	ataques_horizontales = len(filas_con_reina) - len(set(filas_con_reina))
	ataques_verticales = len(columnas_con_reina) - len(set(columnas_con_reina))
	
	ataques_diagonales = 0

	for i in range(N_REINAS-1): # n-1 porque ultima posicion no se compara con otra posicion
		fila_1 = filas_con_reina[i]
		columna_1 = columnas_con_reina[i]
	
		for j in range(i+1, N_REINAS):
			fila_2 = filas_con_reina[j]
			columna_2 = columnas_con_reina[j]

			if fila_2 - fila_1 == abs(columna_1 - columna_2):
				ataques_diagonales += 1
	print(filas_con_reina)
	print(columnas_con_reina)
	if ataques_horizontales + ataques_verticales + ataques_diagonales == 0:
		print('max')
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

def shuffle_bstr(num_bits, bstr):
	return ''.join(random.sample(list(bstr), num_bits))

def generar_posiciones_tablero(bstr_posiciones):
	num_bits = len(bstr_posiciones)
	return shuffle_bstr(num_bits, bstr_posiciones)

def bstr_to_bytearray(bstr):
	global N_REINAS
	return int(bstr, 2).to_bytes(N_REINAS, 'big')

def generar_genotipo():
	global N_REINAS

	num_filas_columnas = N_REINAS * N_REINAS
	bstr_posicion_reina = '1' * N_REINAS
	bstr_posicion_vacia = '0' * (num_filas_columnas - N_REINAS)
	
	bstr_posiciones_tablero = generar_posiciones_tablero(bstr_posicion_vacia + bstr_posicion_reina)
	
	cromosomas: bytearray = bstr_to_bytearray(bstr_posiciones_tablero)
	
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
	else:
		print(max(valores_fitness))
	
	if GENERACION_LIMITE == generacion:
		parar = True

	return parar

def imprimir_soluciones(populacion: list):
	for tablero in populacion:
		if tablero.fitness == MAX_FITNESS: # Sin posiciones invalidos
			print(tablero.genotipo)

			for cromosoma in tablero.genotipo:
				print(expandir_byte(cromosoma))

			print('\n')

if __name__ == "__main__":
	generacion = 0
	populacion = generar_populacion(NUM_TABLEROS) 	# Lista de objetos Tablero

	while not parar_algoritmo(populacion):
		populacion = generar_nueva_generacion(generacion, populacion)
		generacion += 1 

	print("# de generacion: ", generacion)

	imprimir_soluciones(populacion)