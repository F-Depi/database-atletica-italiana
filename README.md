## Introduzione
L'obbiettivo è raccogliere tutti i risultati online dell'Atletica Italiana, in quanto non esiste un database scaricabile.
Sito ufficiale della FIDAL (Federazione Italiana di Atletica Leggera) [fidal.it](http://www.fidal.it/).

## Fonte
Viene utilizzata la pagina con le [graduatorie online](http://www.fidal.it/risultati/2019/COD7650/Index.htm) del sito FIDAL, da cui viene fatto lo scraping per ogni disciplina/anno/categoria.
I risultati purtroppo sono solo quelli dal 2005 in poi.

## Utilizzo
I risultati sono raccolti in diversi file CSV che è possibile scaricare qui [https://github.com/F-Depi/database](https://github.com/F-Depi/database-atletica-italiana/tree/master/database).
Ogni csv ha 13 colonne

<img width="1306" alt="image" src="https://github.com/F-Depi/database-atletica-italiana/assets/120582465/631a934e-170c-4105-8d61-e9a13d7844c6">


- ***prestazione*** contiene il tempo utile per classificare i risultati. Tempi/misure scritte erroneamente vengono trasformati in -1, in questo caso la colonna ***cronometraggio*** avrà valore 2. Tempi del tipo hh:mm:SS.ss (es. 1h23:45.67 o 12:34.56) vengono convertiti in SS.ss (es. 1h23:45.67 -> 5025.67 s o 12:34.56 -> 754.56 s). Tempi con una sola cifra decimale (es. 10.3) vengono considerati ottenuti con cronometraggio manuale e convertiti aggiungendo 0.25 s (es. 10.3 -> 10.55 s), in questo caso la colonna ***cronometraggo*** avrà valore 1.
- ***vento*** contiene il vento misurato durante la gara. È vuoto se non c'è nessun dato. La colonna c'è anche per gare in cui il vento non viene misurato (es. salto in alto, 1000m) ed è vuota.
- ***tempo*** contiene il risultato così come comoare nei ranking, può essere anche la misura di un salto o un lancio
- ***cronometraggio*** 0 per cronometraggio elettrico o misura correttamente registrata. 1 per cronometraggio manuale. 2 per valori inseriti erroneamente nei risultati del sito della Fidal (es. 1.23.45 o 12:34)
- ***atleta*** nome dell'atleta
- ***anno*** anno di nascita dell'atleta
- ***categoria*** categoria dell'atleta al tempo della prestazione
- ***società*** società dell'atleta al tempo della prestazione
- ***posizione*** posizione alla gara in cui è stata fatta la prestazione
- ***luogo*** e ***data*** somo della gara in cui è stata fatta la prestazione
- ***link_atleta*** link al profilo fidal dell'atleta
- ***link_società*** link alla pagina fidal della società dell'atleta

## Attezione
Il database è pieno di errori. Ho provato ad arginare questa cosa nella comversione del dato della colonna ***tempo*** a quello della colonna ***prestazione*** mettendo -1 dove il tempo non era stato inserito correttamente. Nonostante ciò ci somo comunque alcune prestazione che sfuggono al filtro ma che sono ovviamente sbagliate (es. il 10.01 nei 400m registrato a Cagliari che compare in cima al file csv. Il tempo è stato inserito come 10.007 quando probabilmente era 1:00.07 e lo script lo arrotonda a 10.01).

Alcuni file csv sono molto grossi, aspettatevi che qualunque programma usiate ci metta qualche secondo ad aprirli.

Oltre agli errori nel database della Fidal è molto provabile che ci siano errori nei meii script, quindi per favore segnalatemi eventuali incongruenze con quello che vi aspettate!


_Buone Statistiche!_
