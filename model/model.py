from database import escursione_DAO
from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model.escursione import Escursione


class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi


        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        lista_dict_ponte = EscursioneDAO.get_escursioni_punti_interesse()
        if lista_dict_ponte is None:
            return

        for dictionary in lista_dict_ponte:
            escursione = self.escursioni_map[dictionary["id_escursione"]]  #recupera dalla tabella ponte l'oggetto collegato al ID
            punto_interesse = self.punti_interesse_map[dictionary['id_punto_interesse']] # uguale

            escursione.punti_interesse.add(punto_interesse)  #aggiungo per ogni escursione (ogg) i punti di interesse nel set che ha l oggetto nell init
            punto_interesse.escursioni.add(escursione)

        return


    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._max_giorni = max_giorni
        self._max_budget = max_budget
        self._escursioni_parco = []

        for escursione in self.escursioni_map.values():
            if escursione.id_parco == id_parco:
                self._escursioni_parco.append(escursione) #prendo tutte ecursioni del parco scelto

        self._ricorsione(0,[], 0, 0, 0, set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        # terminazione
        if valore_corrente > self._valore_ottimo:
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente



        for i in range(start_index, len(self._escursioni_parco)):
            escursione = self._escursioni_parco[i]  #prende ogni escursione del parco dalla successiva alla precedente del parco scelto

            punti_interesse_ok = not punti_usati.intersection(escursione.punti_interesse) #evita doppioni punti interesse
            giorni_ok =self._max_giorni is None or self._max_giorni >= durata_corrente + escursione.durata_giorni
            costo_ok = self._max_budget is None or self._max_budget >= costo_corrente + escursione.costo

            if punti_interesse_ok and giorni_ok and costo_ok:
                nuovo_pacchetto = pacchetto_parziale.copy()
                nuovo_pacchetto.append(escursione)

                nuova_durata = durata_corrente + escursione.durata_giorni
                nuovo_costo = costo_corrente + escursione.costo
                nuovi_punti = punti_usati.union(escursione.punti_interesse)
                nuovo_valore = valore_corrente + sum(punto.voto_visitatori for punto in escursione.punti_interesse)


                self._ricorsione(i + 1, nuovo_pacchetto, nuova_durata, nuovo_costo,nuovo_valore, nuovi_punti)






