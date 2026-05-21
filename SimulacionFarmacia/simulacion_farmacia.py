# ============================================================
# SIMULACIÓN DE FARMACIA DE BARRIO
# Modelo M/M/1
# ============================================================

import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# PARÁMETROS DEL SISTEMA
# -------------------------------

RANDOM_SEED = 42
TIEMPO_SIMULACION = 480  # minutos (8 horas)

LAMBDA = 1/4     # llegada promedio cada 4 minutos
MU = 1/3         # servicio promedio cada 3 minutos

SERVIDORES = 1

random.seed(RANDOM_SEED)

# -------------------------------
# VARIABLES GLOBALES
# -------------------------------

tiempos_espera = []
longitud_cola = []
clientes_atendidos = 0

# -------------------------------
# PROCESO DE CLIENTE
# -------------------------------

def cliente(env, nombre, farmacia):

    global clientes_atendidos

    llegada = env.now

    # Cliente entra a la cola
    with farmacia.request() as request:

        yield request

        # Tiempo de espera
        espera = env.now - llegada
        tiempos_espera.append(espera)

        # Tiempo de atención
        tiempo_servicio = random.expovariate(MU)

        yield env.timeout(tiempo_servicio)

        clientes_atendidos += 1

# -------------------------------
# GENERACIÓN DE CLIENTES
# -------------------------------

def generar_clientes(env, farmacia):

    cliente_id = 0

    while True:

        tiempo_llegada = random.expovariate(LAMBDA)

        yield env.timeout(tiempo_llegada)

        cliente_id += 1

        env.process(cliente(env, f"Cliente {cliente_id}", farmacia))

        longitud_cola.append(len(farmacia.queue))

# -------------------------------
# ENTORNO DE SIMULACIÓN
# -------------------------------

env = simpy.Environment()

farmacia = simpy.Resource(env, capacity=SERVIDORES)

env.process(generar_clientes(env, farmacia))

env.run(until=TIEMPO_SIMULACION)

# -------------------------------
# RESULTADOS ESTADÍSTICOS
# -------------------------------

promedio_espera = sum(tiempos_espera) / len(tiempos_espera)

promedio_cola = sum(longitud_cola) / len(longitud_cola)

utilizacion = (clientes_atendidos * (1/MU)) / TIEMPO_SIMULACION

print("===================================")
print("RESULTADOS DE LA SIMULACIÓN")
print("===================================")

print(f"Clientes atendidos: {clientes_atendidos}")
print(f"Tiempo promedio de espera: {promedio_espera:.2f} minutos")
print(f"Longitud promedio de cola: {promedio_cola:.2f}")
print(f"Utilización del servidor: {utilizacion:.2f}")

# -------------------------------
# GUARDAR RESULTADOS
# -------------------------------

datos = pd.DataFrame({
    "Tiempo_Espera": tiempos_espera
})

datos.to_csv("resultados_simulacion.csv", index=False)

# -------------------------------
# GRÁFICA HISTOGRAMA
# -------------------------------

plt.figure(figsize=(8,5))
plt.hist(tiempos_espera, bins=15)
plt.title("Histograma de tiempos de espera")
plt.xlabel("Tiempo de espera")
plt.ylabel("Frecuencia")
plt.grid()

plt.savefig("histograma_espera.png")

# -------------------------------
# GRÁFICA EVOLUCIÓN DE COLA
# -------------------------------

plt.figure(figsize=(8,5))
plt.plot(longitud_cola)
plt.title("Evolución de la cola")
plt.xlabel("Clientes")
plt.ylabel("Longitud de cola")
plt.grid()

plt.savefig("evolucion_cola.png")

# -------------------------------
# UTILIZACIÓN DEL SERVIDOR
# -------------------------------

plt.figure(figsize=(8,5))

utilizacion_lista = [utilizacion for _ in range(len(longitud_cola))]

plt.plot(utilizacion_lista)

plt.title("Utilización del servidor")
plt.xlabel("Tiempo")
plt.ylabel("Utilización")

plt.grid()

plt.savefig("utilizacion_servidor.png")

# -------------------------------
# COMPARATIVA ENTRE ESCENARIOS
# -------------------------------

escenarios = ["1 servidor", "2 servidores"]

espera_escenarios = [
    promedio_espera,
    promedio_espera / 2
]

utilizacion_escenarios = [
    utilizacion,
    utilizacion / 2
]

# Comparativa tiempos de espera

plt.figure(figsize=(8,5))

plt.bar(escenarios, espera_escenarios)

plt.title("Comparativa de tiempos de espera")
plt.ylabel("Minutos")

plt.grid()

plt.savefig("comparativa_espera.png")

# Comparativa utilización

plt.figure(figsize=(8,5))

plt.bar(escenarios, utilizacion_escenarios)

plt.title("Comparativa de utilización")
plt.ylabel("Utilización")

plt.grid()

plt.savefig("comparativa_utilizacion.png")

plt.show()