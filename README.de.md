Visuelle Workbench für Reparierbare Systeme

Überblick

Repairable Systems Visual Workbench ist eine unabhängige Desktop Anwendung für die explorative Zuverlässigkeitsanalyse reparierbarer Systeme. Sie bietet eine visuelle Oberfläche zur Eingabe von Ausfalldaten, zur Anpassung eines Power Law Process Modells, zur Erstellung diagnostischer Diagramme und zum Export statistischer Ergebnisse.

Dieses Projekt ist eine unabhängige Softwareimplementierung auf Grundlage öffentlich bekannter statistischer Methoden für NHPP, Power Law Process Modellierung und Zuverlässigkeitswachstumsanalyse. Es ist keine offizielle Veröffentlichung, Empfehlung, Zertifizierung oder validierte Anwendung einer Normungsorganisation, eines Verlags oder einer dritten Institution.

Hauptfunktionen

1. Visuelle Dateneingabe mit Tabellen im Stil einer Tabellenkalkulation
2. Unterstützung für Daten eines einzelnen Elements, mehrere Elemente mit gemeinsamem Beobachtungshorizont, mehrere Elemente mit unterschiedlichen Beobachtungshorizonten und gruppierte Intervalldaten
3. Schätzung von beta, lambda und Ausfallintensität z(t)
4. Diagramme kumulierter Ausfälle, log log Diagramme, QQ Diagramme, TTT Diagramme und Intensitätsdiagramme
5. Bootstrap basierte Konfidenzbänder für Modellkurven, wenn diese Option aktiviert ist
6. Bewertung der Anpassungsgüte mittels Cramer von Mises Simulation
7. Export von Diagrammen und statistischen Zusammenfassungen
8. Unterstützung einer mehrsprachigen Oberfläche

Mathematischer Kern

Die Anwendung implementiert die Form des Power Law Process

Lambda(t) = lambda t^beta

z(t) = lambda beta t^(beta minus 1)

Die kritischen Werte von Cramer von Mises werden zur Laufzeit durch Monte Carlo Simulation berechnet. Das Programm enthält keine reproduzierten Tabellen kritischer Werte. In jeder Simulation werden geordnete Gleichverteilungsstichproben erzeugt, der relative Formparameter erneut geschätzt, die Cramer von Mises Statistik berechnet und das angeforderte Quantil als kritischer Schwellenwert verwendet.

Die Konfidenzgrenzen für z(t) werden je nach gewählter Option aus analytischen Approximationen und Bootstrap Verfahren berechnet. Für diese Berechnungen werden keine eingebetteten Tabellierungen verwendet.

Datenbeispiele

Die eingebetteten Beispiele sind synthetisch und werden ausschließlich zur Demonstration der Software erzeugt. Sie wurden nicht aus einer geschützten Veröffentlichung oder aus einer proprietären Datenquelle kopiert.

Projektstruktur

run_workbench.py
    Hauptdatei zum Starten der Anwendung.

repairable_workbench/i18n.py
    Oberflächentexte, Übersetzungen, Beschriftungen und Sprachwörterbücher.

repairable_workbench/math_core.py
    Statistische Schätzung, Modellanpassung, Berechnungen zur Anpassungsgüte, Konfidenzintervalle, Bootstrap Routinen und Erzeugung kritischer Werte durch Monte Carlo.

repairable_workbench/results.py
    Ergebniscontainer und formatierte statistische Zusammenfassungen.

repairable_workbench/plotting.py
    Hilfsfunktionen zur Vorbereitung von Diagrammen und Unterstützung für Modellkurven.

repairable_workbench/resources.py
    Import, Export, Speichern, synthetische Beispiele und Hilfsressourcen.

repairable_workbench/ui_components.py
    Wiederverwendbare visuelle Komponenten, einschließlich Datentabellen im Stil einer Tabellenkalkulation.

repairable_workbench/visual.py
    Hauptgrafikoberfläche und Layout der Anwendung.

Installation

Python 3.10 oder neuer wird empfohlen.

Installieren Sie die erforderlichen Pakete mit

pip install numpy scipy matplotlib

Ausführen der Anwendung

Führen Sie aus dem Projektordner aus

python run_workbench.py

Windows Beispiel

cd "C:\Users\Windows\Documents\Projects\modular_workbench_v3"
C:\Users\Windows\AppData\Local\Programs\Python\Python313\python.exe .\run_workbench.py

Wenn die ZIP Datei einen verschachtelten Ordner erstellt, wechseln Sie vor dem Ausführen des Befehls in den inneren Ordner, der run_workbench.py und das Verzeichnis repairable_workbench enthält.

Wichtigste aktuelle Änderung

Die wichtigste in dieser Version geänderte Datei ist

repairable_workbench/math_core.py

Die frühere Logik auf Basis einer festen Tabelle für den Cramer von Mises Schwellenwert wurde durch die Erzeugung kritischer Werte mittels Monte Carlo ersetzt.

Hinweise zur Veröffentlichung

Dieses Repository ist als unabhängige Bildungs und Ingenieursoftware gedacht. Vor einer öffentlichen Veröffentlichung sollten geschützte Texte, reproduzierte Tabellen, Screenshots, Abbildungen, Logos oder Beispiele aus kommerziellen Normen, Büchern, Handbüchern oder proprietären internen Berichten vermieden werden.

Empfohlene Repository Namen

repairable_systems_workbench
nhpp_reliability_workbench
power_law_process_workbench

Vorgeschlagene kurze Repository Beschreibung

Unabhängige visuelle Workbench für die Zuverlässigkeitsanalyse reparierbarer Systeme mit NHPP und Power Law Process Methoden.

Lizenz

Fügen Sie vor der Veröffentlichung des Projekts eine Lizenzdatei hinzu. Für eine öffentliche Veröffentlichung als Open Source sind gängige Optionen MIT, BSD 3 Clause, Apache 2.0 oder GPL 3.0, je nachdem, wie permissiv die Bedingungen für die Wiederverwendung sein sollen.