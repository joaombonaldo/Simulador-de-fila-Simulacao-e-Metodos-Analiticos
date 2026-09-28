# Simulador de rede de filas - Simulacao e Metodos Analiticos
# uso: python simulador_rede.py modelo.yml

import sys
import yaml

# gerador de numeros pseudoaleatorios - metodo congruente linear
a = 1103515245
c = 12345
M = 2 ** 31
previous = 7  # seed

contador = 0  # quantos aleatorios ainda podem ser usados
aleatorios = None  # lista fixa de aleatorios (rndnumbers), se o modelo tiver


class AcabouAleatorios(Exception):
    pass


def NextRandom():
    global previous, contador
    if contador == 0:
        # pediu aleatorio e nao tem mais: a simulacao para no meio desse evento
        raise AcabouAleatorios()
    contador = contador - 1
    if aleatorios is not None:
        # pega o proximo da lista (o contador comeca no tamanho da lista)
        return aleatorios[len(aleatorios) - contador - 1]
    previous = (a * previous + c) % M
    return previous / M

def uniforme(min, max):
    return min + NextRandom() * (max - min)


class Fila:
    def __init__(self, nome, dados):
        self.nome = nome
        self.servidores = dados["servers"]
        self.capacidade = dados.get("capacity")  # sem capacity = fila infinita
        self.min_chegada = dados.get("minArrival")
        self.max_chegada = dados.get("maxArrival")
        self.min_atendimento = dados["minService"]
        self.max_atendimento = dados["maxService"]
        self.rotas = []  # [destino, probabilidade], o que sobrar sai da rede
        self.clientes = 0
        self.perdas = 0
        if self.capacidade is None:
            self.tempos = [0]  # vai crescendo conforme a fila aumenta
        else:
            self.tempos = [0] * (self.capacidade + 1)

    def Status(self):
        return self.clientes

    def Servers(self):
        return self.servidores

    def cabe(self):
        return self.capacidade is None or self.clientes < self.capacidade

    def In(self):
        self.clientes = self.clientes + 1
        if self.clientes == len(self.tempos):
            self.tempos.append(0)

    def Out(self):
        self.clientes = self.clientes - 1

    def Loss(self):
        self.perdas = self.perdas + 1

    def kendall(self):
        if self.capacidade is None:
            return "G/G/" + str(self.servidores)
        return "G/G/" + str(self.servidores) + "/" + str(self.capacidade)


# variaveis globais da simulacao
clock = 0
escalonador = []
filas = {}


def agenda(tempo, tipo, origem, destino):
    escalonador.append([tempo, tipo, origem, destino])

def NextEvent():
    # pega o evento com o menor tempo
    escalonador.sort(key=lambda e: e[0])
    return escalonador.pop(0)


def AcumulaTempo(tempo_evento):
    global clock
    for fila in filas.values():
        fila.tempos[fila.Status()] = fila.tempos[fila.Status()] + (tempo_evento - clock)
    clock = tempo_evento


def sorteia_destino(fila):
    # as rotas ficam em ordem crescente de probabilidade e a saida da rede e sempre a ultima
    if len(fila.rotas) == 0:
        return None
    if len(fila.rotas) == 1 and fila.rotas[0][1] >= 1.0:
        return fila.rotas[0][0]
    r = NextRandom()
    acumulado = 0
    for destino, probabilidade in fila.rotas:
        acumulado = acumulado + probabilidade
        if r <= acumulado:
            return destino
    return None


def agenda_chegada(fila):
    agenda(clock + uniforme(fila.min_chegada, fila.max_chegada), "chegada", None, fila.nome)


def agenda_atendimento(fila):
    # primeiro sorteia para onde o cliente vai depois, depois o tempo de atendimento
    destino = sorteia_destino(fila)
    tempo = clock + uniforme(fila.min_atendimento, fila.max_atendimento)
    if destino is None:
        agenda(tempo, "saida", fila.nome, None)
    else:
        agenda(tempo, "passagem", fila.nome, destino)


def entra(fila):
    if fila.cabe():
        fila.In()
        if fila.Status() <= fila.Servers():
            agenda_atendimento(fila)
    else:
        fila.Loss()


def sai(fila):
    fila.Out()
    if fila.Status() >= fila.Servers():
        agenda_atendimento(fila)


def CHEGADA(evento):
    fila = filas[evento[3]]
    entra(fila)
    agenda_chegada(fila)


def SAIDA(evento):
    sai(filas[evento[2]])


def PASSAGEM(evento):
    sai(filas[evento[2]])
    entra(filas[evento[3]])


def carrega_modelo(arquivo):
    with open(arquivo) as f:
        linhas = [l for l in f if not l.startswith("!")]
    return yaml.safe_load("".join(linhas))


def roda_simulacao(modelo, semente, quantidade):
    global clock, escalonador, filas, contador, previous, aleatorios

    clock = 0
    escalonador = []
    filas = {}
    for nome, dados in modelo["queues"].items():
        filas[nome] = Fila(nome, dados)
    for rota in modelo.get("network") or []:
        filas[rota["source"]].rotas.append([rota["target"], rota["probability"]])
    for fila in filas.values():
        fila.rotas.sort(key=lambda r: r[1])

    if semente is None:
        aleatorios = list(modelo["rndnumbers"])
        contador = len(aleatorios)
    else:
        aleatorios = None
        previous = semente
        contador = quantidade

    # primeiros clientes chegando de fora da rede
    for nome, tempo in modelo["arrivals"].items():
        agenda(tempo, "chegada", None, nome)

    while contador > 0 and len(escalonador) > 0:
        evento = NextEvent()
        AcumulaTempo(evento[0])

        try:
            if evento[1] == "chegada":
                CHEGADA(evento)
            elif evento[1] == "saida":
                SAIDA(evento)
            elif evento[1] == "passagem":
                PASSAGEM(evento)
        except AcabouAleatorios:
            break

    return clock, filas


def main():
    if len(sys.argv) < 2:
        print("uso: python simulador_rede.py modelo.yml")
        return

    modelo = carrega_modelo(sys.argv[1])

    # se tiver seeds usa o gerador, senao usa a lista rndnumbers
    if modelo.get("seeds"):
        sementes = modelo["seeds"]
        quantidade = modelo.get("rndnumbersPerSeed", 100000)
    else:
        sementes = [None]
        quantidade = len(modelo["rndnumbers"])

    # soma os resultados de todas as simulacoes para depois tirar a media
    tempo_total = 0
    tempos = {}
    perdas = {}
    for semente in sementes:
        if semente is None:
            print("simulacao com a lista de aleatorios do modelo (" + str(quantidade) + " aleatorios)")
        else:
            print("simulacao com semente " + str(semente) + " (" + str(quantidade) + " aleatorios)")
        tempo, resultado = roda_simulacao(modelo, semente, quantidade)
        tempo_total = tempo_total + tempo
        for nome, fila in resultado.items():
            if nome not in tempos:
                tempos[nome] = []
                perdas[nome] = 0
            while len(tempos[nome]) < len(fila.tempos):
                tempos[nome].append(0)
            for i in range(len(fila.tempos)):
                tempos[nome][i] = tempos[nome][i] + fila.tempos[i]
            perdas[nome] = perdas[nome] + fila.perdas

    n = len(sementes)
    tempo_medio = tempo_total / n
    print()

    for nome, fila in resultado.items():
        print("==========", nome, "(" + fila.kendall() + ") ==========")
        if fila.min_chegada is not None:
            print("chegadas:", fila.min_chegada, "...", fila.max_chegada)
        print("atendimento:", fila.min_atendimento, "...", fila.max_atendimento)
        print()
        for i in range(len(tempos[nome])):
            t = tempos[nome][i] / n
            prob = t / tempo_medio * 100
            print(i, ":", round(t, 4), "(", round(prob, 4), "%)")
        print()
        print("perdas:", perdas[nome] / n if n > 1 else perdas[nome])
        print()

    print("tempo global da simulacao:", round(tempo_medio, 4))
    if n > 1:
        print("(media de", n, "simulacoes)")


main()
