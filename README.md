# Simulador-de-fila-Simulacao-e-Metodos-Analiticos

Trabalho de Simulação e Métodos Analíticos (PUCRS).

- `simulador_fila.py`: fila simples (M4)
- `simulador_fila_tandem.py`: duas filas em tandem (M6)
- `simulador_rede.py`: rede de filas (T1)
- `modelo_t1.yml`: modelo usado no T1

## Rodando

Precisa de Python 3 e do pyyaml.

```
pip install pyyaml
python simulador_rede.py modelo_t1.yml
```

Para cada fila aparece o tempo acumulado e a probabilidade de cada estado e o número de perdas. No fim aparece o tempo global.

## Modelo

O arquivo segue o formato do simulator.jar do Moodle. Não apagar a linha `!PARAMETERS`.

```yaml
!PARAMETERS
arrivals:
   Q1: 2.0

queues:
   Q1:
      servers: 1
      minArrival: 2.0
      maxArrival: 4.0
      minService: 1.0
      maxService: 2.0
   Q2:
      servers: 2
      capacity: 5
      minService: 4.0
      maxService: 6.0

network:
-  source: Q1
   target: Q2
   probability: 0.2

rndnumbersPerSeed: 100000
seeds:
- 7
```

`arrivals` diz em quais filas chegam clientes de fora e o tempo da primeira chegada. Só essas filas precisam de `minArrival` e `maxArrival`. Fila sem `capacity` tem capacidade infinita.

Em `network` vão as probabilidades de roteamento. O que faltar para 100% é a chance do cliente sair da rede (no exemplo, 80% sai depois da Q1).

Com `seeds` o simulador usa o nosso gerador congruente linear (a = 1103515245, c = 12345, M = 2^31), roda uma vez para cada semente e mostra a média. Sem `seeds` ele usa a lista de `rndnumbers` na ordem.

## Detalhes

Quando um cliente começa a ser atendido sorteamos primeiro o destino dele e depois o tempo de atendimento. Se a fila não tem rota ou só tem uma rota com probabilidade 1, não gasta aleatório no destino.

No sorteio do destino as rotas ficam em ordem crescente de probabilidade e a saída da rede fica por último.

A simulação para quando acabam os aleatórios. Se um evento precisar de um e não tiver mais, para ali mesmo.

Seguimos a mesma ordem do simulator.jar. Testamos rodando os dois com a mesma lista em `rndnumbers` e os resultados deram iguais.
