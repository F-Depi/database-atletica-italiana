## Introduzione
Questa repository non è ufficiale e non ha alcun legame con la FIDAL.
L'obbiettivo è raccogliere tutti i risultati online dell'Atletica Italiana, in quanto non esiste un database scaricabile.
Sito ufficiale della FIDAL (Federazione Italiana di Atletica Leggera) [fidal.it](http://www.fidal.it/).

## Fonte
Viene utilizzata la pagina con le [graduatorie online](http://www.fidal.it/risultati/2019/COD7650/Index.htm) del sito FIDAL, da cui viene fatto lo scraping per ogni disciplina/anno/categoria.
I risultati purtroppo sono solo quelli dal 2005 in poi.

## Utilizzo
I risultati sono raccolti in diversi file CSV che è possibile scaricare qui [https://github.com/F-Depi/database](https://github.com/F-Depi/database-atletica-italiana/tree/master/database).
Ogni csv può avere fino a 13 colonne

![image](https://github.com/F-Depi/database-atletica-italiana/assets/120582465/d871b986-7b3b-426a-9568-91b316633563)


- ***prestazione*** contiene il tempo utile per classificare i risultati. Tempi/misure scritte erroneamente vengono trasformati in -1, in questo caso la colonna ***cronometraggio*** avrà valore _x_. Tempi del tipo hh:mm:SS.ss (es. 1h23:45.67 o 12:34.56) vengono convertiti in SS.ss (es. 1h23:45.67 -> 5025.67 s o 12:34.56 -> 754.56 s). Tempi con una sola cifra decimale (es. 10.3) vengono considerati ottenuti con cronometraggio manuale e convertiti aggiungendo 0.25 s (es. 10.3 -> 10.55 s), in questo caso la colonna ***cronometraggo*** avrà valore m.
- ***vento*** contiene il vento misurato durante la gara. È vuoto se non c'è nessun dato. La colonna c'è anche per gare in cui il vento non viene misurato (es. salto in alto, 1000m) ed è vuota.
- ***tempo*** contiene il risultato così come comoare nei ranking, può essere anche la misura di un salto o un lancio
- ***cronometraggio*** _e_ per cronometraggio elettrico o misura correttamente registrata. _m_ per cronometraggio manuale. _x_ per valori inseriti erroneamente nei risultati del sito della Fidal (es. 1.23:45). Tempi errati del tipo 1.23.45 vengono segnalati con _x_, ma interpretati come 1:23.45 in quanto è l'errore più comune commesso. Il database viene poi controllato e corretto a mano, gli errori corretti sono salvati in [errori outdoor](https://github.com/F-Depi/database-atletica-italiana/blob/master/database/outdoor/errori.csv) ed [errori indoor](https://github.com/F-Depi/database-atletica-italiana/blob/master/database/indoor/errori.csv)
- ***atleta*** nome dell'atleta
- ***anno*** anno di nascita dell'atleta
- ***categoria*** categoria dell'atleta al tempo della prestazione
- ***società*** società dell'atleta al tempo della prestazione
- ***posizione*** posizione alla gara in cui è stata fatta la prestazione
- ***luogo*** e ***data*** somo della gara in cui è stata fatta la prestazione
- ***link_atleta*** link al profilo fidal dell'atleta
- ***link_società*** link alla pagina fidal della società dell'atleta

## Attenzione
Il database è pieno di errori. Ho provato ad arginare questa cosa nella
conversione del dato della colonna ***tempo*** a quello della colonna
***prestazione*** mettendo -1 dove il tempo non era stato inserito correttamente.
Nonostante ciò ci sono comunque alcune prestazione che sfuggono al filtro ma che
sono ovviamente sbagliate (es. il 10.01 nei 400m registrato a Cagliari che
compare in cima al file csv. Il tempo è stato inserito come 10.007 quando
probabilmente era 1:00.07 e lo script lo arrotonda a 10.01).

Alcuni file csv sono molto grossi, aspettatevi che qualunque programma usiate
ci metta qualche secondo ad aprirli.

Oltre agli errori nel database della Fidal è molto provabile che ci siano errori
nei mei script, quindi per favore segnalatemi eventuali incongruenze con quello che vi aspettate!

Per discipline poco comuni (es. 24h) i dati hanno spesso errori e sono gestiti
male dagli script. Non ho intenzione di perderci tempo, ma mi sono comunque
preoccupato di scaricare tutto. Consiglio di fare riferimento alla colonna
***tempi*** che ha i dati grezzi.

A volte ci sono anche errori sulla data di nascita che impediscono al sistema
di rinoscere correttamente la categoria.

Gare mancanti (todo list):
 - più o meno tutta la categoria ragazzi poiché i risultati compaiono solo
 specificando la regione;
 - corse su strada;


## Errori su marcia e gare più lunghe di 1 minuto

Viene spesso erroneamente usato il punto per separare i minuti dai secondi. Questa cosa ha contaminato tantissimi risultati.

![image](https://github.com/F-Depi/database-atletica-italiana/assets/120582465/5535fc56-5779-44b3-9b3f-74ede643c6ec)

Ad esempio nelle graduatorie dei [10km di marcia su strada del 2012](https://www.fidal.it/graduatorie.php?anno=2012&tipo_attivita=S&sesso=M&categoria=XM&gara=49&tipologia_estrazione=2&vento=0&regione=0&nazionalita=2&limite=0&societa=&submit=Invia) il miglior tempo stagionale sarebbe di Alex Schwazer con 39:06 (ovvero 39 minuti e 6 secondi) che però è solo 21°, visti gli strabilianti tempi sotto al minuto (tutti inseriti erroneamente nella gara di Bressanone del 6 luglio 2012).

Al momento non ho intenzione di correggere questi errori, ma se qualcuno volesse farlo è il benvenuto.


_Buone Statistiche!_


## A seguito di una richiesta da casa...
Migliori (4) PB promesse nei 1500m fatti il giorno del proprio compleanno

![image](https://github.com/user-attachments/assets/85644ab6-1e64-4d01-9802-243df39c8868)

