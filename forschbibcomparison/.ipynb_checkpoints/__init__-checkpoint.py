import logging
import time
import sys
from forschbibcomparison import base, indexLists, config, indexMatchingWorkflow

logging.basicConfig(filename='process.log', level=logging.DEBUG)
print("##################################")
print("Wahl aus folgenden Optionen:")
print("##################################\n\n\n")
print(" 1 - Scopus-Zeitschriftenliste auf aktuellem Stand laden")
print(" 2 - SCIE-Zeitschriftenliste auf aktuellem Stand laden")
print(" 3 - SSCI-Zeitschriftenliste auf aktuellem Stand laden\n")
# print(" 4 - Vergleiche Bibsonomy-Inhalte (input-Verzeichnis) mit Scopus- und SciE-Liste - 1 zu 1 / Stringmatch")
print(" 5 - Update der Mappingtabelle")
print("     Zeitschriftentitel aus .bib-Datei (input-Verzeichnis) zum Abgleich mit Scopus-, SciE- und SSCIListe")
print(" 6 - Vergleiche Bibsonomy-Inhalte (input-Verzeichnis) mit Scopus-, SciE- und SSCIListe - strukturiertes Mapping inkl. Mappingtabelle - bibtex-Ausgabe")

print(" 7 - Erstelle Matchingtabelle der Forschbibzeitschriften auf Scopus, SciE und SSCI - Output in csv")


print("\n 0 - Programm beenden")


print("\n##################################")

choice = base.getUserInput()

if choice == "1":
    start_time = time.time()
    print("Aktualisiere Scopus-Zeitschriftenliste ...")
    indexLists.putScopusJournalListOnDisk()
    print("Laufzeit: ", time.time() - start_time)
elif choice == "2":
    start_time = time.time()
    print("Aktualisiere SCIE-Zeitschriftenliste ...")
    indexLists.putSCIJournalListOnDisk()
    print("Laufzeit: ", time.time() - start_time)
elif choice == "3":
    start_time = time.time()
    print("Aktualisiere SSCI-Zeitschriftenliste ...")
    indexLists.putSSCIJournalListOnDisk()
    print("Laufzeit: ", time.time() - start_time)
elif choice == "4":
    start_time = time.time()
    print("Lade input-Verzeichnis ...")
    bibsonomyInputFileString = base.readFileFromDirectoryToString(config.inputFileLocation)
    scopusJournalList = base.getScopusJournalList(config.scopusFileListFileNameOnDisk)
    sciJournalList    = base.getSciJournalList(config.sciFileListNameOnDiskPrefix)

    # Und hier nun der Vergleich...
    base.compareJournalEntries(bibsonomyInputFileString, scopusJournalList, sciJournalList, "simple")
    print("Fertig! Das Ergebnis des Vergleichs liegt im output-Verzeichnis!")
    print("Laufzeit: ", time.time() - start_time)

elif choice == "5":
    start_time = time.time()
    print("Lade input-Verzeichnis ...")
    bibsonomyInputFileString = base.readFileFromDirectoryToString(config.inputFileLocation)
    scopusJournalList = base.getScopusJournalList(config.scopusFileListFileNameOnDisk)
    sciJournalList = base.getSciJournalList(config.sciFileListNameOnDiskPrefix)
    ssciJournalList = base.getSciJournalList(config.ssciFileListNameOnDiskPrefix)
    indexMatchingWorkflow.indexMatching(bibsonomyInputFileString, scopusJournalList, sciJournalList, ssciJournalList)

    #base.compareJournalEntries(bibsonomyInputFileString, scopusJournalList, sciJournalList, ssciJournalList, "advanced")
    print("Fertig! Das Ergebnis des Skripts liegt im mapping-Verzeichnis!\nDie originale Mapping-Datei liegt im archive-Ordner.")
    print("Laufzeit des Skripts: ", time.time() - start_time)
    sys.exit()
elif choice == "6":
    start_time = time.time()
    print("Lade input-Verzeichnis ...")
    bibsonomyInputFileString = base.readFileFromDirectoryToString(config.inputFileLocation)
    scopusJournalList = base.getScopusJournalList(config.scopusFileListFileNameOnDisk)
    sciJournalList = base.getSciJournalList(config.sciFileListNameOnDiskPrefix)
    ssciJournalList = base.getSciJournalList(config.ssciFileListNameOnDiskPrefix)

    base.compareJournalEntriesAndPutThemToBibtextFile(bibsonomyInputFileString, scopusJournalList, sciJournalList, ssciJournalList)
    print("Fertig! Das Ergebnis der Anreicherung liegt im output-Verzeichnis!")
    print("Laufzeit: ", time.time() - start_time + " Sekunden")
elif choice == "7":
    start_time = time.time()
    base.checkMappingFileMatches()
    print("Laufzeit: ", time.time() - start_time)

elif choice == "0":
    print("Programm beendet!")
    sys.exit()