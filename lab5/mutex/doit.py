"""
Application with a critical section (CS)
- sets up a group of peers
- peers compete for some critical section
- peers run in separate processes
- multiprocessing should work on unix and windows
- terminates random processes to simulate crash faults
"""

import sys
import time
import logging
import random
import multiprocessing as mp
from threading import Thread

from process import Process
from context import lab_channel, lab_logging

# Setup Logging
lab_logging.setup(stream_level=logging.DEBUG, file_level=logging.DEBUG)

logger = logging.getLogger("vs2lab.lab5.mutex.doit")


def create_and_run(num_bits, proc_class, enter_bar, run_bar):
    """
    Erzeugt und führt einen Peer aus
    :param num_bits: Adressbereich des Kanals
    :param node_class: Klasse des Peers
    :param enter_bar: Barrier für die Synchronisation der Kanalerstellung
    :param run_bar: Barrier für die Synchronisation des Starts
    """
    chan = lab_channel.Channel(n_bits=num_bits)
    proc = proc_class(chan)
    enter_bar.wait()  # Warte, bis alle Peers dem Kanal beigetreten sind
    proc.init()  # Bootstrapping ausführen
    run_bar.wait()  # Warte, bis alle Prozesse bereit sind
    proc.run()  # Starte die Ausführung


def simulate_crashes(children, num_crashes=2):
    """
    Simuliert den Absturz von Prozessen
    :param children: Liste der laufenden Prozesse
    :param num_crashes: Anzahl der simulierten Abstürze
    """
    logger.info("Starte Simulation von Abstürzen...")
    for _ in range(num_crashes):
        if len(children) > 0:
            # Wähle zufällig einen Prozess aus, der abstürzen soll
            proc_id = random.randint(0, len(children) - 1)
            proc_to_crash = children[proc_id]
            del(children[proc_id])  # Entferne den Prozess aus der Liste

            # Beende den ausgewählten Prozess
            proc_to_crash.terminate()
            proc_to_crash.join()

            logger.warning("Ein Prozess ist abgestürzt: {}".format(proc_to_crash))

        # Warte zufällig zwischen 5 und 10 Sekunden vor dem nächsten Absturz
        time.sleep(random.randint(5, 10))

    logger.info("Simulation der Abstürze abgeschlossen.")


if __name__ == "__main__":  # Startpunkt des Skripts
    m = 8  # Anzahl der Bits für Prozess-IDs
    n = 4  # Anzahl der Prozesse in der Gruppe

    # Überprüfe Kommandozeilenparameter m und n
    if len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])

    # Kanal leeren, um alte Nachrichten zu löschen
    chan = lab_channel.Channel()
    chan.channel.flushall()

    # Prozesse für Windows-Unterstützung mit "spawn" starten
    mp.set_start_method('spawn')

    # Barrieren für die Synchronisation erstellen
    bar1 = mp.Barrier(n)  # Warten, bis alle Prozesse dem Kanal beigetreten sind
    bar2 = mp.Barrier(n)  # Warten, bis die Initialisierung abgeschlossen ist

    # Starte n konkurrierende Peers in separaten Prozessen
    children = []
    for i in range(n):
        peer_proc = mp.Process(
            target=create_and_run,
            name="Peer-" + str(i),
            args=(m, Process, bar1, bar2))
        children.append(peer_proc)
        peer_proc.start()

    # Starte die Simulation von Abstürzen in einem separaten Thread
    crash_simulation_thread = Thread(target=simulate_crashes, args=(children,))
    crash_simulation_thread.start()

    # Hauptprozess wartet auf alle verbleibenden Prozesse, während die Simulation läuft
    logger.info("Warte, bis alle verbleibenden Prozesse abgeschlossen sind...")
    for peer_proc in children:
        peer_proc.join()

    # Warte, bis der Crash-Simulations-Thread abgeschlossen ist
    crash_simulation_thread.join()

    logger.info("Alle Prozesse abgeschlossen. Ende des Programms.")
