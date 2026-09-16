# Simulador de filas em tandem - Simulacao e Metodos Analiticos

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
escalonador = []

# fila 1 (recebe as chegadas externas)
fila1 = 0
servidores_ocupados1 = 0
perdas1 = 0
tempos1 = []
K1 = 0
num_servidores1 = 0
ta_min, ta_max = 0, 0
ts1_min, ts1_max = 0, 0

# fila 2 (recebe a passagem da fila 1 e manda os clientes para fora do sistema)
fila2 = 0
servidores_ocupados2 = 0
perdas2 = 0
tempos2 = []
K2 = 0
num_servidores2 = 0
ts2_min, ts2_max = 0, 0


def agenda(tempo, tipo):
    escalonador.append([tempo, tipo])

def NextEvent():
    # pega o evento com o menor tempo
    escalonador.sort(key=lambda e: e[0])
    return escalonador.pop(0)


def AcumulaTempo(tempo_evento):
    global clock
    # atualiza o tempo acumulado das duas filas, nao so da que sofreu o evento
    tempos1[fila1] = tempos1[fila1] + (tempo_evento - clock)
    tempos2[fila2] = tempos2[fila2] + (tempo_evento - clock)
    clock = tempo_evento


def CHEGADA():
    global fila1, servidores_ocupados1, perdas1

    if fila1 < K1:
        fila1 = fila1 + 1
        if servidores_ocupados1 < num_servidores1:
            servidores_ocupados1 = servidores_ocupados1 + 1
            ts1 = uniforme(ts1_min, ts1_max)
            agenda(clock + ts1, "passagem")
    else:
        perdas1 = perdas1 + 1

    ta = uniforme(ta_min, ta_max)
    agenda(clock + ta, "chegada")


def PASSAGEM():
    global fila1, servidores_ocupados1
    global fila2, servidores_ocupados2, perdas2

    # sai um cliente da fila 1
    fila1 = fila1 - 1
    servidores_ocupados1 = servidores_ocupados1 - 1

    if fila1 > servidores_ocupados1:
        servidores_ocupados1 = servidores_ocupados1 + 1
        ts1 = uniforme(ts1_min, ts1_max)
        agenda(clock + ts1, "passagem")

    # esse mesmo cliente chega na fila 2
    if fila2 < K2:
        fila2 = fila2 + 1
        if servidores_ocupados2 < num_servidores2:
            servidores_ocupados2 = servidores_ocupados2 + 1
            ts2 = uniforme(ts2_min, ts2_max)
            agenda(clock + ts2, "saida")
    else:
        perdas2 = perdas2 + 1


def SAIDA():
    global fila2, servidores_ocupados2

    fila2 = fila2 - 1
    servidores_ocupados2 = servidores_ocupados2 - 1

    # se tiver alguem esperando na fila 2 comeca o atendimento dele
    if fila2 > servidores_ocupados2:
        servidores_ocupados2 = servidores_ocupados2 + 1
        ts2 = uniforme(ts2_min, ts2_max)
        agenda(clock + ts2, "saida")


def roda_simulacao():
    global clock, escalonador, contador, previous
    global fila1, servidores_ocupados1, perdas1, tempos1, K1, num_servidores1
    global fila2, servidores_ocupados2, perdas2, tempos2, K2, num_servidores2
    global ta_min, ta_max, ts1_min, ts1_max, ts2_min, ts2_max

    # reseta tudo para uma nova simulacao
    previous = 7
    clock = 0
    escalonador = []
    contador = 100000

    fila1 = 0
    servidores_ocupados1 = 0
    perdas1 = 0
    K1 = 3
    num_servidores1 = 2
    ta_min, ta_max = 1.0, 5.0
    ts1_min, ts1_max = 4.0, 5.0
    tempos1 = [0] * (K1 + 1)

    fila2 = 0
    servidores_ocupados2 = 0
    perdas2 = 0
    K2 = 5
    num_servidores2 = 1
    ts2_min, ts2_max = 1.0, 3.0
    tempos2 = [0] * (K2 + 1)

    # primeiro cliente chega na fila 1 em t = 2.5
    agenda(2.5, "chegada")

    while contador > 0:
        evento = NextEvent()
        tempo_evento = evento[0]
        tipo_evento = evento[1]

        AcumulaTempo(tempo_evento)

        if tipo_evento == "chegada":
            CHEGADA()
        elif tipo_evento == "passagem":
            PASSAGEM()
        elif tipo_evento == "saida":
            SAIDA()

    # print
    print("===== fila 1 (G/G/2/3) =====")
    print("numeros aleatorios usados:", 100000 - contador)
    print("tempo global:", clock)
    print("clientes perdidos:", perdas1)
    print()
    for i in range(K1 + 1):
        prob = tempos1[i] / clock * 100
        print(i, ":", round(tempos1[i], 4), "(", round(prob, 4), "%)")
    print()

    print("===== fila 2 (G/G/1/5) =====")
    print("clientes perdidos:", perdas2)
    print()
    for i in range(K2 + 1):
        prob = tempos2[i] / clock * 100
        print(i, ":", round(tempos2[i], 4), "(", round(prob, 4), "%)")
    print()


roda_simulacao()
