# Simulador de fila - Simulacao e Metodos Analiticos
# chegadas entre 3...5, atendimento entre 4...5, primeiro cliente em t=3.0

# gerador de numeros pseudoaleatorios (metodo congruente linear)
a = 1103515245
c = 12345
M = 2 ** 31
previous = 7  # seed

contador = 100000  # quantos aleatorios ainda podem ser usados

def NextRandom():
    global previous, contador
    contador = contador - 1
    previous = (a * previous + c) % M
    return previous / M

def uniforme(min, max):
    return min + NextRandom() * (max - min)


# variaveis globais da simulacao
clock = 0
fila = 0
servidores_ocupados = 0
escalonador = []
perdas = 0
tempos = []

K = 0
num_servidores = 0
ta_min, ta_max = 0, 0
ts_min, ts_max = 0, 0


def agenda(tempo, tipo):
    escalonador.append([tempo, tipo])

def NextEvent():
    # pega o evento com o menor tempo
    escalonador.sort(key=lambda e: e[0])
    return escalonador.pop(0)


def CHEGADA():
    global fila, servidores_ocupados, perdas

    if fila < K:
        fila = fila + 1
        if servidores_ocupados < num_servidores:
            servidores_ocupados = servidores_ocupados + 1
            ts = uniforme(ts_min, ts_max)
            agenda(clock + ts, "saida")
    else:
        perdas = perdas + 1

    ta = uniforme(ta_min, ta_max)
    agenda(clock + ta, "chegada")


def SAIDA():
    global fila, servidores_ocupados

    fila = fila - 1
    servidores_ocupados = servidores_ocupados - 1

    # se tiver alguem esperando, comeca o atendimento dele
    if fila > servidores_ocupados:
        servidores_ocupados = servidores_ocupados + 1
        ts = uniforme(ts_min, ts_max)
        agenda(clock + ts, "saida")


def roda_simulacao(nome, k, servidores):
    global clock, fila, servidores_ocupados, escalonador, perdas, tempos, contador
    global K, num_servidores, ta_min, ta_max, ts_min, ts_max, previous

    # reseta tudo para uma nova simulacao
    previous = 7
    clock = 0
    fila = 0
    servidores_ocupados = 0
    escalonador = []
    perdas = 0
    contador = 100000

    K = k
    num_servidores = servidores
    ta_min, ta_max = 3.0, 5.0
    ts_min, ts_max = 4.0, 5.0
    tempos = [0] * (K + 1)

    # primeiro cliente chega em t = 3.0 (fila comeca vazia)
    agenda(3.0, "chegada")

    while contador > 0:
        evento = NextEvent()
        tempo_evento = evento[0]
        tipo_evento = evento[1]

        tempos[fila] = tempos[fila] + (tempo_evento - clock)
        clock = tempo_evento

        if tipo_evento == "chegada":
            CHEGADA()
        elif tipo_evento == "saida":
            SAIDA()

    # print
    print("=====", nome, "=====")
    print("numeros aleatorios usados:", 100000 - contador)
    print("tempo global:", clock)
    print("clientes perdidos:", perdas)
    print()
    for i in range(K + 1):
        prob = tempos[i] / clock * 100
        print(i, ":", round(tempos[i], 4), "(", round(prob, 4), "%)")
    print()


roda_simulacao("fila G/G/1/5", 5, 1)
roda_simulacao("fila G/G/2/5", 5, 2)
