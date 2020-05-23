import sys
import time

from mpi4py import MPI
from ploca import Ploca


def evaluate(kopija_ploce, zadnji_igrac, dubina):
    svi_porazi = True
    sve_pobjede = True
    trenutna_ploca = Ploca(zadana_ploca=kopija_ploce)
    if trenutna_ploca.kraj_igre() != 0:
        if zadnji_igrac == 1:
            return 1
        else:
            return -1
    if dubina == 0:
        return 0
    dubina -= 1
    if zadnji_igrac == 1:
        novi_igrac = 2
    else:
        novi_igrac = 1
    ukupno = 0
    poteza = 0
    for br_stupca in range(7):
        if trenutna_ploca.legalni_potez(br_stupca):
            poteza += 1
            trenutna_ploca.napravi_potez(br_stupca, novi_igrac)
            rezultat = evaluate(trenutna_ploca, novi_igrac, dubina)
            trenutna_ploca.ponisti_potez(br_stupca)
            if rezultat > -1:
                svi_porazi = False
            if rezultat != 1:
                sve_pobjede = False
            if rezultat == 1 and novi_igrac == 1:
                return 1
            if rezultat == -1 and novi_igrac == 2:
                return -1
            ukupno += rezultat
    if sve_pobjede:
        return 1
    if svi_porazi:
        return -1
    ukupno /= poteza
    return ukupno


def novi_zadatak(br_zadatka, ploca):
    rez = []
    potez1 = br_zadatka // 7
    if ploca.legalni_potez(potez1):
        rez.append(potez1)
        potez2 = br_zadatka % 7
        if ploca.legalni_potez(potez2):
            rez.append(potez2)
    return rez


if __name__ == '__main__':

    communicator = MPI.COMM_WORLD
    dubina = 6
    if len(sys.argv) > 1:
        dubina = sys.argv[1]

    size = communicator.Get_size()
    rank = communicator.Get_rank()
    # print("%d od %d" % (rank, size))

    # voditelj
    if rank == 0:
        ploca = Ploca("ploca")
        kraj_voditelj = False
        rezultati = dict()

        if ploca.kraj_igre() != 0:
            print("Pobjednik: " + str(ploca.kraj_igre()))
            kraj_voditelj = True
            # posalji radnicima da je kraj
            data = ["kraj", "pobjeda"]
            for i in range(1, size):
                communicator.send(data, dest=i, tag=1)

        potez = input()
        if ploca.legalni_potez(int(potez)):
            ploca.napravi_potez(int(potez), 2)
        start = time.time()

        if ploca.kraj_igre() != 0:
            print("Pobjednik: " + str(ploca.kraj_igre()))
            kraj_voditelj = True
            # posalji radnicima da je kraj
            data = ["kraj", "pobjeda"]
            for i in range(1, size):
                communicator.send(data, dest=i, tag=1)

        zadaci = []
        br_zadataka = 0
        while br_zadataka < 49:
            zadatak = novi_zadatak(br_zadataka, ploca)
            br_zadataka += 1
            if len(zadatak) == 2:
                zadaci.append(zadatak)

        broj_zadataka = len(zadaci)
        if broj_zadataka == 0 and ploca.kraj_igre() == 0:
            print("Nerijeseno!")
            kraj_voditelj = True
            data = ["kraj", "nerjeseno"]
            for i in range(1, size):
                communicator.send(data, dest=i, tag=1)

        """"# salji plocu svim radnicima
        data = ["ploca", ploca]
        for i in range(1, size):
            communicator.send(data, dest=i, tag=1)"""

        while not kraj_voditelj:
            # salji plocu svim radnicima
            data = ["ploca", ploca]
            for i in range(1, size):
                communicator.send(data, dest=i, tag=1)

            # cekaj zahtjeve ili rezultate
            poruka = communicator.recv(source=MPI.ANY_SOURCE, tag=2)
            if poruka[0] == "zahtjev":
                if len(zadaci) > 0:
                    zadatak = zadaci.pop()
                    data = ["zadatak", zadatak[0], zadatak[1]]
                    communicator.send(data, dest=poruka[1], tag=3)
                else:
                    # nema vise zadataka, salji kraj
                    data = ["kraj", "nema zadataka"]
                    #communicator.send(data, dest=poruka[1], tag=3)
                    for i in range(1, size):
                        communicator.send(data, dest=i, tag=3)
            if poruka[0] == "rezultat":
                # obradi rezultate
                rezultati[poruka[1], poruka[2]] = poruka[3]
                if len(rezultati) >= broj_zadataka:
                    # obradeni svi zadaci
                    kraj_voditelj = True

        rezultati_radnika = []
        izracunato = False
        for i in range(7):
            prosjek = 0
            br_rez = 0
            for j in range(7):
                if (i, j) in rezultati.keys():
                    if rezultati.get((i, j)) == -1:
                        rezultati_radnika.insert(i, -1)
                        izracunato = True
                        break
                    prosjek += rezultati.get((i, j))
                    br_rez += 1
                else:
                    continue
            if not izracunato:
                if br_rez != 0:
                    prosjek /= br_rez
                    rezultati_radnika.insert(i, prosjek)
                else:
                    rezultati_radnika.insert(i, -2)
        najbolji = rezultati_radnika.index(max(rezultati_radnika))
        ploca.napravi_potez(najbolji, 1)
        # ploca.ispis_ploce("ploca")
        for el in rezultati_radnika:
            if el == -2:
                continue
            print("%.3f" % el, end=" ")
        print("\n", end="")
        stop = time.time()
        # print("vrijeme:" + str(stop - start))
        ploca.ispis_ploce()
        ploca.ispis_ploce("ploca")
        sys.stdout.flush()

    else:
        kraj_radnik = False
        kopija_ploce = Ploca()
        while not kraj_radnik:
            # primi plocu ili kraj
            # if kraj_radnik:
              #  break
            poruka = communicator.recv(source=0, tag=1)
            if poruka[0] == "kraj":
                break
            if poruka[0] == "ploca":
                kopija_ploce = Ploca(zadana_ploca=poruka[1])

            while True:
                # salji zahtjev - trazi zadatak
                data = ["zahtjev", rank]
                communicator.send(data, dest=0, tag=2)

                # cekaj zadatak ili kraj
                poruka = communicator.recv(source=0, tag=3)
                if poruka[0] == "zadatak":
                    potez1 = poruka[1]
                    potez2 = poruka[2]
                if poruka[0] == "kraj":
                    kraj_radnik = True
                    break

                # obavi zadatak
                if kopija_ploce.legalni_potez(potez1):
                    kopija_ploce.napravi_potez(potez1, 1)
                    if kopija_ploce.kraj_igre() != 0:
                        # ako je CPU pobijedio - javi
                        data = ["rezultat", potez1, potez2, 1]
                        communicator.send(data, dest=0, tag=2)
                        continue
                if kopija_ploce.legalni_potez(potez2):
                    kopija_ploce.napravi_potez(potez2, 2)
                    if kopija_ploce.kraj_igre() != 0:
                        # ako je player pobijedio - javi
                        data = ["rezultat", potez1, potez2, -1]
                        communicator.send(data, dest=0, tag=2)
                        continue
                rezultat_radnik = evaluate(kopija_ploce, 2, int(dubina) - 2)
                data = ["rezultat", potez1, potez2, rezultat_radnik]
                communicator.send(data, dest=0, tag=2)
                kopija_ploce.ponisti_potez(potez2)
                kopija_ploce.ponisti_potez(potez1)
