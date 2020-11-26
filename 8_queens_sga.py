from random import random, randrange, uniform, choices, sample
import sys

N_REINAS = 8 # Numero de reinas
TABLERO_INVALIDO = 28 # Tablero invalido da fitness = 0
MAX_FITNESS = 28 	# Sin posiciones invalidas en tablero 8x8 con 8 reinas
GENERACION_LIMITE = 100000
NUM_TABLEROS = 1000 # Tamaño de poblacion
BANDERA_MUTACION = True # Si permitir mutacion o no
CRUZAR = uniform(0.6, 0.9) # probabilidad de cruzamiento entre 0.6 y 0.9
MUTACION = uniform(
	1/NUM_TABLEROS, 1/(N_REINAS*N_REINAS)
) # probabilidad de mutacion entre 1/population_size y 1/chromosome_length

class Tablero:
	def __init__(self):
		self.genotipo: bytearray = []
		self.fitness: int = 0
	
	# Secuencia de cromosomas / genotipo / posible solucion
	# 64 bits / 16 nibbles / 8 bytes
	def set_genotipo(self, genotipo: bytearray):
		self.genotipo = genotipo

	# fitness == 28, no hay ataques de reina
	# fitness == 0, tablero invalido por mutacion
	def set_fitness(self, fitness: int):
		self.fitness = fitness

def expandir_posicion(byte_posicion, tipo: str):
	'''
	Obtener posicion de una reina en el tablero expandiendo un byte del genotipo

	Primeros 4 bits = fila, Ultimos 4 bits = columna

	Parameters:
		byte_posicion(): byte de posicion
		tipo(str): devolver posicion como tuple de enteros o cadena binaria
	'''
	bstr_posicion = expandir_byte(byte_posicion)
	bstr_fila = bstr_posicion[0:4]
	bstr_columna = bstr_posicion[4:]

	if tipo == 'int':
		return int(bstr_fila, 2), int(bstr_columna, 2)
	
	return bstr_fila, bstr_columna


def mutar(hijo: Tablero):
	"""	
	- according to genetic theory, a mutation will take place
	when there is an anomaly during cross over state

	- since a computer cannot determine such anomaly, we can define 
	the probability of developing such a mutation 

	"""
	cromasomas = ''

	for posicion_byte in hijo.genotipo:
		bstr_fila, bstr_columna = expandir_posicion(posicion_byte, "bstr")

		cromasomas += bstr_fila if random() > MUTACION else generar_nibble_bstr()

		cromasomas += bstr_columna if random() > MUTACION else generar_nibble_bstr()

	genotipo: bytearray = bstr_to_bytes(cromasomas)
	
	hijo.genotipo = genotipo

def bytearray_to_bstr(bytearray):
	return ''.join([expandir_byte(byte) for byte in bytearray])

def cruzamiento_1_punto(padre_1: Tablero, padre_2: Tablero):
	globals()
	num_nibbles = N_REINAS * 2
	corte = randrange(1, num_nibbles) * 4

	bstr_genotipo_p1 = bytearray_to_bstr(padre_1.genotipo)
	bstr_genotipo_p2 = bytearray_to_bstr(padre_2.genotipo)

	hijo_1_genotipo = bstr_to_bytes(
		bstr_genotipo_p1[0:corte] +
		bstr_genotipo_p2[corte:]
	)

	hijo_2_genotipo = bstr_to_bytes(
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
	return choices(
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
	#sum_fitness: int = sum([tablero.fitness for tablero in populacion])

	#for tablero in populacion:
	#	tablero.set_sobrevivencia(tablero.fitness/sum_fitness)

	print(f'Ejecutando generacion genetica: {generacion}')

	for _ in range(int(NUM_TABLEROS/2)):
		padre_1, padre_2 = seleccionar_padres(populacion)
		# print("Padres generados : ", padre_1, padre_2)

		hijo_1, hijo_2 = [padre_1, padre_2] if random() < CRUZAR else cruzamiento_1_punto(padre_1, padre_2) 

		if(BANDERA_MUTACION):
			mutar(hijo_1)
			mutar(hijo_2)

		nueva_populacion.append(hijo_1)
		nueva_populacion.append(hijo_2)
		
	return nueva_populacion

def shuffle_bstr(num_bits, bstr):
	return ''.join(sample(list(bstr), num_bits))

def bstr_to_bytes(bstr: str):
	'''
	Convierte una cadena binaria a un arreglo de 8 bytes
	
	Cada indice contiene 8 bits (una posicion de reina)
	'''
	return int(bstr, 2).to_bytes(N_REINAS, 'big')

def expandir_byte(byte):
	return f'{byte:b}'.zfill(8)

def ataques_de_reinas(genotipo: bytearray):
	# calculate row and column clashes
	# just subtract the unique length of array from total length of array
	# [1,1,1,2,2,2] - [1,2] => 4 clashes
	posiciones_reina: list[tuple] = []
	
	for posicion_byte in genotipo:
		posicion = expandir_posicion(posicion_byte, "int")

		if posicion in posiciones_reina:
			return TABLERO_INVALIDO
		
		posiciones_reina.append(posicion)

	ataques_horizontales = N_REINAS - len(set([columna for _, columna in posiciones_reina]))
	ataques_verticales = N_REINAS - len(set([fila for fila, _ in posiciones_reina]))

	ataques_diagonales = 0

	for i in range(N_REINAS-1): # n-1 porque ultima posicion no se compara con otra posicion
		fila_1, columna_1 = posiciones_reina[i]
	
		for j in range(i+1, N_REINAS):
			fila_2, columna_2 = posiciones_reina[j]

			if abs(fila_1 - fila_2) == abs(columna_1 - columna_2):
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

def int_to_bstr(entero: int):
	return f'{entero:b}'

def generar_nibble_bstr():
	return int_to_bstr(randrange(0, N_REINAS)).zfill(4)

def generar_posicion_int(posicion: tuple = None):
	bstr_fila = generar_nibble_bstr()
	bstr_columna = generar_nibble_bstr()
	
	return int(bstr_fila + bstr_columna, 2)

def generar_posiciones_bytearray(num_posiciones: int):
	posiciones: list[int] = []
	p = 1

	while(p <= num_posiciones):
		posicion_int = generar_posicion_int()

		if posicion_int not in posiciones:
			posiciones.append(posicion_int)
			p += 1

	return bytearray(posiciones)

def generar_genotipo():
	global N_REINAS

	posiciones_reina: bytearray = generar_posiciones_bytearray(N_REINAS)
	
	return posiciones_reina

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

def imprimir_solucion(genotipo: bytearray):
	tablero = [0] * N_REINAS

	for byte_posicion in genotipo:
		fila, columna = expandir_posicion(byte_posicion, "int")	
		tablero[fila] = columna
		
	print(tablero, '\n')

	for fila in range(N_REINAS):
		tablero_fila = ['0'] * N_REINAS
		columna = tablero[fila]
		tablero_fila[columna] = '1'
		
		print(' '.join(tablero_fila), '\n')

def parar_algoritmo(populacion: list, generacion: int):
	globals()
	parar = False
	indice_max_fitness: int = None

	# fitness = Maximo de posiciones invalidas (28) - posiciones invalidas en solucion
	# Maximo de posiciones invalidas en tablero 8x8 es 28
	# Si fitness == 28, no hubieron reinas en posiciones invalidas
	# 
	valores_fitness = [tablero.fitness for tablero in populacion]	

	try:
		indice_max_fitness = valores_fitness.index(MAX_FITNESS)

		tablero_solucion = populacion[indice_max_fitness].genotipo
		imprimir_solucion(tablero_solucion)
		parar = True

	except ValueError:
		if GENERACION_LIMITE == generacion:
			parar = True
			print(f'Valor maximo de fitness fue: {max(valores_fitness)}')	

	return parar

if __name__ == "__main__":
	generacion = 0
	populacion = generar_populacion(NUM_TABLEROS) 	# Lista de objetos Tablero

	print(f'Ejecutando generacion genetica: {generacion}')

	while not parar_algoritmo(populacion, generacion):
		populacion = generar_nueva_generacion(generacion, populacion)
		generacion += 1 