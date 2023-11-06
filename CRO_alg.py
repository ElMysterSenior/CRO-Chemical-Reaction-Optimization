import random

# Parámetros del algoritmo
num_moleculas = 500
num_colisiones = 1000
KE_LOSS_RATE = 0.2
BUFFER_PERCENT = 0.1
buffer = 0
CALORIAS_MINIMAS = 2000
PESO_MAXIMO = 2.7

# Leer los datos del archivo
with open("lista_productos.txt", "r") as archivo:
    lineas = archivo.readlines()

valores = []
for linea in lineas:
    partes = linea.strip().split(',')
    nombre_producto = partes[0]
    valor1 = float(partes[1])
    valor2 = int(partes[2])
    array_valores = [nombre_producto, valor1, valor2]
    valores.append(array_valores)

def crear_solucion():
    return [random.randint(0, 1) for _ in range(len(valores))]

def evaluar_solucion(solucion):
    peso_total, calorias_totales = 0, 0
    for i in range(len(solucion)):
        if solucion[i] == 1:
            peso_total += valores[i][1]
            calorias_totales += valores[i][2]
            #print(solucion, peso_total, calorias_totales)
    if peso_total > PESO_MAXIMO or calorias_totales < CALORIAS_MINIMAS:
        return peso_total, 0
    return peso_total, calorias_totales



def neighbor(solucion):
    # Devuelve una solución vecina de la solución dada
    solucion_vecina = solucion.copy()
    indice_gen_a_mutar = random.randint(0, len(solucion_vecina) - 1)
    solucion_vecina[indice_gen_a_mutar] = 1 - solucion_vecina[indice_gen_a_mutar]
    return solucion_vecina

def ineff_col_on_wall(M):#Puse el buffer en global para que no solo afecte en local (funcion), si no que sea la variable global
    global buffer  
    w_prime = neighbor(M['w'])
    PE_w_prime = evaluar_solucion(w_prime)[1]
    if M['PE'] + M['KE'] >= PE_w_prime:
        q = random.uniform(KE_LOSS_RATE, 1)
        KE_w_prime = (M['PE'] + M['KE'] - PE_w_prime) * q
        buffer += (M['PE'] + M['KE'] - PE_w_prime) * (1 - q)
        M['w'] = w_prime
        M['PE'] = PE_w_prime
        M['KE'] = KE_w_prime


def descompose(M): #Puse el buffer en global para que no solo afecte en local (funcion), si no que sea la variable global
    global buffer 
    w1_prime, w2_prime = neighbor(M['w']), neighbor(M['w'])
    PE_w1_prime, PE_w2_prime = evaluar_solucion(w1_prime)[1], evaluar_solucion(w2_prime)[1]
    temp1 = M['PE'] + M['KE'] - PE_w1_prime - PE_w2_prime
    success = False
    if temp1 >= 0 or temp1 + buffer >= 0:
        if temp1 < 0:
            temp1 += buffer
            buffer = 0  # Restablece el buffer si se usa
        k = random.random()
        KE_w1_prime = temp1 * k
        KE_w2_prime = temp1 * (1 - k)
        new_molecule1 = {'w': w1_prime, 'PE': PE_w1_prime, 'KE': KE_w1_prime}
        new_molecule2 = {'w': w2_prime, 'PE': PE_w2_prime, 'KE': KE_w2_prime}
        moleculas.append(new_molecule1) 
        moleculas.append(new_molecule2)
        success = True
    return success


def synthesis(M1, M2):
    global moleculas  
    w_prime = neighbor(M1['w'])  
    PE_w_prime = evaluar_solucion(w_prime)[1]
    success = False
    if M1['PE'] + M2['PE'] + M1['KE'] + M2['KE'] >= PE_w_prime:
        KE_w_prime = M1['PE'] + M2['PE'] + M1['KE'] + M2['KE'] - PE_w_prime
        new_molecule = {'w': w_prime, 'PE': PE_w_prime, 'KE': KE_w_prime}
        moleculas.append(new_molecule)
        moleculas.remove(M1)  # Elimina M1 de la lista
        moleculas.remove(M2)  # Elimina M2 de la lista
        success = True
    return success

def inter_ineff_coll(M1, M2):
    w1_prime, w2_prime = neighbor(M1['w']), neighbor(M2['w'])
    PE_w1_prime, PE_w2_prime = evaluar_solucion(w1_prime)[1], evaluar_solucion(w2_prime)[1]
    temp2 = (M1['PE'] + M2['PE'] + M1['KE'] + M2['KE']) - (PE_w1_prime + PE_w2_prime)
    if temp2 >= 0:
        p = random.random()
        KE_w1_prime = temp2 * p
        KE_w2_prime = temp2 * (1 - p)
        M1['w'], M1['PE'], M1['KE'] = w1_prime, PE_w1_prime, KE_w1_prime
        M2['w'], M2['PE'], M2['KE'] = w2_prime, PE_w2_prime, KE_w2_prime



# Inicializar las moléculas
moleculas = [{'w': crear_solucion(), 'PE': 0, 'KE': 0} for _ in range(num_moleculas)]
for molecula in moleculas:
    molecula['PE'] = evaluar_solucion(molecula['w'])[1]

moleculas_creadas = 0
moleculas_destruidas = 0

contador_colisiones = {
    'ineff_col_on_wall': 0,
    'descompose': 0,
    'inter_ineff_coll': 0,
    'synthesis': 0
}
# Proceso de colisión
for colision in range(num_colisiones):

    tipo_colision = random.randint(1, 4)

    if tipo_colision == 1:
        # Colisión ineficaz contra la pared
        contador_colisiones['ineff_col_on_wall'] += 1
        molecula_seleccionada = random.choice(moleculas)
        ineff_col_on_wall(molecula_seleccionada)
    elif tipo_colision == 2:
        # Descomposición
        contador_colisiones['descompose'] += 1
        molecula_seleccionada = random.choice(moleculas)
        if descompose(molecula_seleccionada):
            moleculas_creadas+=2
    elif tipo_colision == 3:
        # Colisión intermolecular ineficaz
        contador_colisiones['inter_ineff_coll'] += 1
        molecula1, molecula2 = random.sample(moleculas, 2)
        inter_ineff_coll(molecula1, molecula2)
    elif tipo_colision == 4:
        # Síntesis
        contador_colisiones['synthesis'] += 1
        molecula1, molecula2 = random.sample(moleculas, 2)
        if synthesis(molecula1, molecula2):
            moleculas_creadas += 1  # Una nueva molécula se creó
            moleculas_destruidas += 2  # Dos moléculas se combinaron en una

    #print(f"Iteración {colision + 1}: {len(moleculas)} moléculas (Creadas: {moléculas_creadas}, Destruidas: {moléculas_destruidas})")

# Encontrar la mejor solución
mejores_moleculas = [molecula for molecula in moleculas if molecula['PE'] > 0]
if mejores_moleculas:
    mejor_molecula = max(mejores_moleculas, key=lambda x: x['PE'])
    peso_mejor_molecula, _ = evaluar_solucion(mejor_molecula['w'])
    print("La mejor molécula es:", mejor_molecula, "con un peso de:", peso_mejor_molecula)
else:
    print("No se encontró ninguna solución que cumpla con las restricciones.")


print(f"Final: {len(moleculas)} moléculas (Creadas: {moleculas_creadas}, Destruidas: {moleculas_destruidas})")
for tipo, contador in contador_colisiones.items():
    print(f"{tipo}: {contador} veces")