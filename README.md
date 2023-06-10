# OC-Quantum

La tesina implementativa per l'esame di Ottimizzazione Combinatoria verterà sull'analisi e la relativa implementazione dell'algoritmo per trovare il flusso massimo in una rete di flusso.

Il lavoro deve comprendere:

- Un riassunto del teorema MaxFlow-MinCut (che garantisce la validità di quello che stiamo facendo)
- Un mini-riassunto sulla computazione quantistica (per comprendere il formalismo adottato)
- La formalizzazione matematica del problema in forma QUBO (Quadratic unconstrained binary optimization)
- Implementazione su Dwave-Leap
  - Algoritmo per trasformare il grafo di flusso in equazione QUBO
  - Esecuzione tramite QPU
- Test ed eventuali confronti tramite NetworkX

## Risorse utili

- [Teorema MaxFlow-MinCut](https://en.wikipedia.org/wiki/Max-flow_min-cut_theorem)
- [Libreria NetworkX](https://networkx.org/documentation/stable/index.html) per la gestione dei flussi (e calcolo automatico del [MaxFlow](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.maximum_flow.html))
- [Dwave Leap](https://docs.ocean.dwavesys.com/en/stable/index.html)
- [Dispense sui modelli QUBO](https://drive.google.com/file/d/1d3AduRFHbS-_6aR5KAH3G7xRhIigxu0p/view)
  - In particolare guardare la IV parte e la sezione 21.1.2
