## test per importare i dati che si trovano in
## https://github.com/F-Depi/database-atletica-italiana

## Una funzione utile per importare i csv che contengono sia numeri che scritte
## è csv2cell(), questa funzione però è presente nel pacchetto "io" che va
## installato la prima volta con il comando
##
## pkg install -forge io
##
## poi basterà dire a octave di usare il paccchetto "io" all'inizio di uno
## script con
pkg load io

data = csv2cell('60m_2025-01-24.csv');

# Prendo la prima colonna 8a meno del primo elemento che è l'intestazione) e la
# converto in numeri
tempi = data(2:end, 1);
cat = data(2:end, 6);
tempi = cell2mat(tempi);

## Trovo gli indici delle celle che hanno M o F, per dividere uomini e donne
uomini = cellfun(@(x) ~isempty(strfind(x, "M")), cat);
donne = cellfun(@(x) ~isempty(strfind(x, "F")), cat);

tempi_uomini = tempi(uomini);
tempi_donne = tempi(donne);

# Per far venire l'histogramma più bello tengo solo i tempi minori di 12 secondi
tempi_uomini = tempi_uomini(tempi_uomini < 12);
tempi_donne = tempi_donne(tempi_donne < 12);

figure()
hold on;
hist(tempi_uomini, bin=50, 'facecolor', 'r', 'facealpha', 0.5)
hist(tempi_donne, bin=50, 'facecolor', 'b', 'facealpha', 0.5)
legend('Uomini', 'Donne')
xlabel('Tempo [s]')
ylabel('# prestazioni')
title('Distribuzione delle prestazioni nei 60m piani indoor')
set(gca, 'FontSize', 18, 'LineWidth', 1.2, 'Box', 'on');

