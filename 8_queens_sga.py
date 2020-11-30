from random import random, randrange, uniform, choices, shuffle

N_REINAS = 8 # Numero de reinas
TABLERO_INVALIDO = 28 # Tablero invalido da fitness = 0
MAX_FITNESS = 28 	# Sin posiciones invalidas en tablero 8x8 con 8 reinas
GENERACION_LIMITE = 100000 # Parar si llega a esta generación sin encontrar solucion
NUM_TABLEROS = 1000 # Tamaño de poblacion
BANDERA_MUTACION = True # Si permitir mutacion o no
CRUZAR = uniform(0.6, 0.9) # probabilidad de cruzamiento entre 0.6 y 0.9
MUTACION = uniform(
	1/NUM_TABLEROS, 1/(N_REINAS*N_REINAS)
) # probabilidad de mutacion entre 1/population_size y 1/chromosomes_length


class Tablero:
	def __init__(self):
		self.genotipo: bytearray = []
		self.fitness: int = 0
	
	def set_genotipo(self, genotipo: bytearray):
		"""
		Secuencia de cromosomas / genotipo / posible solucion
		
		64 bits / 16 nibbles / 8 bytes
		"""
		self.genotipo = genotipo

	def set_fitness(self, fitness: int):
		"""
		fitness == 28, no hay ataques de reina
		
		fitness == 0, tablero invalido por mutacion
		"""
		self.fitness = fitness


def byte_to_position(byte: int, tipo: str = 'bstr'):
	'''
	Obtener posicion de una reina en el tablero expandiendo un byte del genotipo

	Primeros 4 bits = fila, Ultimos 4 bits = columna

	Parameters:
		byte(int): byte de posicion
		tipo(str): devolver posicion como tuple de enteros o cadena binaria
	
	Returns:
		posicion (fila, columna) de reina en un tablero

		tuple de enteros si tipo == 'int'
		tuple de cadenas binarias si tipo != 'int'
	'''
	bstr_posicion = int_to_bstr(byte, 8) # cadena binaria de longitud 8
	bstr_fila = bstr_posicion[0:4]
	bstr_columna = bstr_posicion[4:]

	if tipo == 'int': # tuple de enteros
		return int(bstr_fila, 2), int(bstr_columna, 2)
	
	return bstr_fila, bstr_columna # tuple de cadenas binarias


def mutar(tablero: Tablero):
	"""	
	Mutar cromosomas del genotipo (64 bits / 8 bytes) de un tablero al azar

	Cada byte del genotipo representa una posicion de reina en el tablero

	Primeros 4 bits = fila, Ultimos 4 bits = columna

	Parameters:
		hijo(Tablero): tablero con 8 reinas
	"""
	cromasomas = '' # para almacenar cromosomas de genotipo

	for byte in tablero.genotipo:
		# Obtener posición (fila, columna) de una reina como cadenas binarias
		bstr_fila, bstr_columna = byte_to_position(byte, "bstr")

		# Decidir si mutar fila de reina al azar
		cromasomas += bstr_fila if random() > MUTACION else generar_nibble_bstr()
		# Decidir si mutar columna de reina al azar
		cromasomas += bstr_columna if random() > MUTACION else generar_nibble_bstr()

	# Convertir representation de genotipo de cadena binaria a arreglo de bytes
	genotipo: bytearray = bstr_to_bytearray(cromasomas, N_REINAS)
	
	# Asignar nuevo genotipo de tablero
	tablero.genotipo = genotipo


def bytearray_to_bstr(byte_array: bytearray, num_bytes: int):
	"""
	Convertir bytearray (64 bits / 8 bytes) a cadena binaria
	
	Parameters:
		byte_array(bytearray): arreglo de bytes - posiciones de reinas 
		num_bytes(int): numero de posiciones de reinas

	Returns:
		cadena binario - posiciones de reinas
	"""
	return ''.join([int_to_bstr(byte, num_bytes) for byte in byte_array])


def cruzamiento_1_punto(padre_1: Tablero, padre_2: Tablero):
	"""
	Cruzar el genotipo de 2 tableros para generar 2 tableros nuevos

	Corte de cruzamiento es cada 4to bit porque cada 4 bits representan
	una fila o columna de una posición de reina

	Arguements:
		padre_1(Tablero): tablero
		padre_2(Tablero): tablero

	Returns:
		Tuple de tableros generados por cruzamiento
	"""
	num_nibbles = N_REINAS * 2 # 16 nibbles == 8 bytes
	corte = randrange(1, num_nibbles) * 4 # corte de genotipo cada 4to bit

	# obtener genotipo como cadena binaria
	bstr_genotipo_p1 = bytearray_to_bstr(padre_1.genotipo, N_REINAS)
	bstr_genotipo_p2 = bytearray_to_bstr(padre_2.genotipo, N_REINAS)

	# obtener genotipo de cruzamiento como cadena binaria
	bstr_genotipo_h1 = bstr_genotipo_p1[0:corte] + bstr_genotipo_p2[corte:]
	bstr_genotipo_h2 = bstr_genotipo_p2[0:corte] + bstr_genotipo_p1[corte:]
	
	# obtener genotipo como arreglo de bytes del cruzamiento
	# se alterna orden de los genotipos cruzados
	hijo_1_genotipo = bstr_to_bytearray(bstr_genotipo_h1, N_REINAS)
	hijo_2_genotipo = bstr_to_bytearray(bstr_genotipo_h2, N_REINAS)

	# Crear tableros usando genotipos del cruzamiento
	hijo_1 = Tablero()
	hijo_1.set_genotipo(hijo_1_genotipo)
	hijo_1.set_fitness(fitness(hijo_1.genotipo))

	hijo_2 = Tablero()
	hijo_2.set_genotipo(hijo_2_genotipo)
	hijo_2.set_fitness(fitness(hijo_2.genotipo))

	return hijo_1, hijo_2


def seleccionar_padres(populacion: list):
	"""
	Se seleccionan 2 tableros de una lista al azar dependiendo de su fitness

	Tablero tiene mas probabilidad de ser seleccionado si tiene buen fitness

	Arguments:
		populacion(list): lista de tableros

	Returns:
		lista con 2 tableros seleccionados de la lista al azar
	"""
	return choices(
		population = populacion,
		weights = [tablero.fitness for tablero in populacion],
		k = 2
	)


def generar_nueva_generacion(generacion: int, populacion: list):
	"""
	Generar nueva lista de tableros realizando cruzamientos y mutaciones
	de los genotipos de los tableros antiguos (pasada generación)

	Arguements:
		generacion(int): número de generación
		populacion(list): lista de tableros

	Returns:
		Lista de tableros
	"""
	nueva_populacion = []

	print(f'Ejecutando generacion genetica: {generacion}')

	for _ in range(int(NUM_TABLEROS/2)): # Dividir por 2 porque se generan 2 tableros a la vez
		padre_1, padre_2 = seleccionar_padres(populacion) # Seleccionar 2 tableros al azar

		# Usar tableros seleccionados o cruzarlos para generar 2 nuevos tableros al azar
		hijo_1, hijo_2 = [padre_1, padre_2] if random() < CRUZAR else cruzamiento_1_punto(padre_1, padre_2) 

		if(BANDERA_MUTACION): # Si se permiten mutaciones, mutar tableros
			mutar(hijo_1)
			mutar(hijo_2)

		# Almacenar tableros para nueva generación
		nueva_populacion.append(hijo_1)
		nueva_populacion.append(hijo_2)

	shuffle(nueva_populacion)

	return nueva_populacion # retornar nueva lista de tableros


def bstr_to_bytearray(bstr: str, num_bytes: int):
	'''
	Convierte una cadena binaria a un arreglo de 8 bytes
	
	Cada indice contiene 8 bits (una posicion de reina)
	
	Parameters:	
		bstr(str): cadena binario - posiciones de reinas
		num_bytes(int): numero de posiciones de reinas

	Returns:
		arreglo de bytes - posiciones de reinas 
	'''
	return int(bstr, 2).to_bytes(num_bytes, 'big')


def ataques_de_reinas(genotipo: bytearray):
	"""
	Consigue numero de ataques de reina en un tablero dado

	Arguments:
		genotipo(bytearray): posiciones de reina representados por bytes

	Returns:
		numero de ataques de reina
	"""
	# posiciones (fila, columna)
	posiciones_reina: list[tuple] = []
	
	for byte in genotipo: # cada byte de genotipo es una posicion
		# Obtener posicion (fila, columna) de una reina
		posicion = byte_to_position(byte, "int")

		# si posicion se repite, hubo mutacion que genero un tablero invalido
		if posicion in posiciones_reina:
			return TABLERO_INVALIDO # retorna 28, da fitness de 0 (28-28)
		
		posiciones_reina.append(posicion) # poner tuple de posicion de reina en lista

	# set dara longitud de 8 si no se repiten columnas
	ataques_horizontales = N_REINAS - len(set([columna for _, columna in posiciones_reina]))
	# set dara longitud de 8 si no se repiten filas
	ataques_verticales = N_REINAS - len(set([fila for fila, _ in posiciones_reina]))

	ataques_diagonales = 0

	for i in range(N_REINAS-1): # n-1 porque ultima posicion no se compara con otra posicion
		fila_i, columna_i = posiciones_reina[i]
	
		for j in range(i+1, N_REINAS): # i+1 para no repetir ataques (1,1 -> 2,2 y 2,2 -> 1,1)
			fila_j, columna_j = posiciones_reina[j]

			# si dx == dy, reinas pueden atacar diagonalmente
			if abs(fila_i - fila_j) == abs(columna_i - columna_j):
				ataques_diagonales += 1
	
	return ataques_horizontales + ataques_verticales + ataques_diagonales


def fitness(genotipo: bytearray):
	"""
	Revisar que cerca esta un tablero a ser una solución al problema de 8 reinas

	fitness == 28, un tablero sin posibles ataques de reina
	fitness == 0, un tablero invalido por causa de mutación 

	Se revisan ataques de reina: fila, columna, diagonal
	 
	Max fitness es 28 porque en peor de los casos todas las reinas se atacan:
	7 + 6 + 5 + 4 + 3 + 2 + 1 = 28

	Arguements:
		genotipo(bytearray): posiciones de reina en tablero

	Returns:
		Entero que representa cercania a tablero solucion (max 28)
	"""
	return MAX_FITNESS - ataques_de_reinas(genotipo)


def int_to_bstr(entero: int, num_bits: int):
	"""
	Convertir entero a cadena binaria de dada longitud

	Arguments:
		entero(int): entero
		num_bits(int): número de bits
	
	Returns:
		cadena binaria de dada longitud
	"""
	return f'{entero:b}'.zfill(num_bits)


def generar_nibble_bstr():
	"""
	Generar una cadena binaria de longitud 4 al azar

	Returns:
		cadena binaria de longitud 4
	"""
	return int_to_bstr(randrange(0, N_REINAS), 4)


def generar_posicion_int():
	"""
	Generar entero que representa una posición (fila, columna) de reina

	Arguments:
		posicion(tuple): posicion de reina

	Returns:
		Entero que representa una posición de reina
	"""
	# Generar 2 cadenas binarias, cada uno de longitud 4 
	bstr_fila = generar_nibble_bstr() # cadena binaria representa fila
	bstr_columna = generar_nibble_bstr() # cadena binaria representa columna
	
	return int(bstr_fila + bstr_columna, 2)


def generar_genotipo():
	"""
	Generar arreglo de bytes que representan posiciones de reina

	Returns:
		Arreglo de bytes
	"""
	posiciones_reina: list[int] = []
	num_posiciones = 0

	while(num_posiciones < N_REINAS): # Generar 8 posiciones
		# Obtener una posicion (tuple) al azar como entero
		posicion_int = generar_posicion_int()

		# almacena posicion si posicion generada es diferente
		if posicion_int not in posiciones_reina: 
			posiciones_reina.append(posicion_int)
			num_posiciones += 1

	return bytearray(posiciones_reina)


def generar_populacion(num_tableros: int = 100):
	'''
	Generar populacion de tableros con posibles soluciones

	Arguments:
		num_tableros(int): Número de tableros en populacion

	Returns:
		Lista de tableros
	'''
	# Lista de objetos Tablero
	populacion = [Tablero() for _ in range(num_tableros)]

	for tablero in populacion:
		tablero.set_genotipo(generar_genotipo()) # Secuencia de cromosomas / genotipo / posible solucion
		tablero.set_fitness(fitness(tablero.genotipo)) # cercania a solucion valida

	print("Tamaño de populacion: ", num_tableros)

	return populacion


def imprimir_solucion(genotipo: bytearray):
	"""
	Imprimir tablero solucion

	Arguments:
		genotipo(bytearray): posiciones de reina en tablero
	"""
	# índice = fila, valor = columna
	tablero = [0] * N_REINAS

	for byte_posicion in genotipo: # Obtener posiciones de reinas
		fila, columna = byte_to_position(byte_posicion, "int")	
		tablero[fila] = columna
		
	print(tablero, '\n') # Imprimir lista de tablero

	for fila in range(N_REINAS): # Imprimir tablero 8x8
		tablero_fila = ['0'] * N_REINAS
		columna = tablero[fila]
		tablero_fila[columna] = '1'
		
		print(' '.join(tablero_fila), '\n')


def parar_algoritmo(populacion: list, generacion: int):
	"""
	Revisar si se encontro un tablero solucion o se alcanzo generacion limite
	
	Arguments:
		populacion(list): lista de tableros
		generacion(int): generacion de populacion

	Returns:
		Boolean si se para de buscar solución o no
	"""
	parar = False
	indice_max_fitness: int = None

	# fitness = Max ataques de reina posibles (28) - ataques de reina en tablero
	# Max ataques en tablero 8x8 es 28
	# Si fitness == 28, no hubieron reinas atacadas
	valores_fitness = [tablero.fitness for tablero in populacion]	

	try: # Revisar si hay tablero solucion
		indice_max_fitness = valores_fitness.index(MAX_FITNESS)

		tablero_solucion = populacion[indice_max_fitness].genotipo
		imprimir_solucion(tablero_solucion)
		parar = True # parar si solucion encontrada

	except ValueError: # Si no se ha encontrado solucion
		if GENERACION_LIMITE == generacion: # parar si generacion limite
			parar = True
			print(f'Valor maximo de fitness fue: {max(valores_fitness)}')	

	return parar



if __name__ == "__main__":
	generacion = 0
	populacion = generar_populacion(NUM_TABLEROS) 	# Lista de objetos Tablero

	print(f'Ejecutando generacion genetica: {generacion}')

	# Mientras no se encuentre solucion o no llegue a generacion limite
	while not parar_algoritmo(populacion, generacion):
		generacion += 1 
		populacion = generar_nueva_generacion(generacion, populacion) # Lista de objetos Tablero