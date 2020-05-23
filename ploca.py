import numpy as np


class Ploca():
    def __init__(self, datoteka=None, brojRedaka=6, zadana_ploca=None):
        self.ploca = []
        if datoteka is not None:
            file = open(datoteka, 'r')
            lines = file.readlines()
            for i, line in enumerate(lines):
                if i == 0:
                    self.brojRedaka = int(line.split(" ")[0])
                else:
                    redak = line.strip().split(" ")
                    redak_int = [int(el) for el in redak]
                    self.ploca.append(redak_int)
            file.close()
            #self.ploca = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,1,0,1,1,0,0],[1,1,0,1,2,0,0],[2,2,2,1,2,2,0]]
            #self.brojRedaka = 6
        else:
            if zadana_ploca is None:
                self.brojRedaka = brojRedaka
                for i in range(self.brojRedaka):
                    redak = []
                    for j in range(7):
                        redak.append(0)
                    self.ploca.append(redak)
            else:
                self.brojRedaka = zadana_ploca.brojRedaka
                for i in range(self.brojRedaka):
                    redak = []
                    for j in range(7):
                        redak.append(zadana_ploca.ploca[i][j])
                    self.ploca.append(redak)

    def ispis_ploce(self, datoteka=None):
        if datoteka is not None:
            file = open(datoteka, 'w')
            file.write(str(self.brojRedaka) + " " + "7\n")
            for redak in self.ploca:
                for el in redak:
                    file.write(str(el) + " ")
                file.write("\n")
            file.close()
        else:
            for redak in self.ploca:
                for el in redak:
                    if el == 0:
                        print("=", end="")
                    elif el == 1:
                        print('C', end="")
                    elif el == 2:
                        print('P', end="")
                print("\n", end="")

    def kraj_igre(self):
        # provjera jel ima 4 u redu
        for i in range(self.brojRedaka):
            istih = 0
            for j in range(6):
                if self.ploca[i][j] == self.ploca[i][j + 1] and self.ploca[i][j] != 0:
                    istih += 1
                    if istih >= 3:
                        return self.ploca[i][j]
                else:
                    istih = 0
        # jel ima 4 u stupcu
        for i in range(7):
            istih = 0
            for j in range(self.brojRedaka - 1):
                if self.ploca[j][i] == self.ploca[j + 1][i] and self.ploca[j][i] != 0:
                    istih += 1
                    if istih >= 3:
                        return self.ploca[j][i]
                else:
                    istih = 0
        # jel ima 4 na dijagonali
        matrix = np.array(self.ploca)
        diags1 = [matrix[::1, :].diagonal(i) for i in range(-(self.brojRedaka - 3) + 1, 4)]
        diags2 = [matrix[::-1, :].diagonal(i) for i in range(-(self.brojRedaka - 3) + 1, 4)]
        diags1 = [n.tolist() for n in diags1]
        diags2 = [n.tolist() for n in diags2]

        for diag in diags1:
            istih = 0
            for i in range(len(diag) - 1):
                if diag[i] == diag[i + 1] and diag[i] != 0:
                    istih += 1
                    if istih >= 3:
                        return diag[i]
                else:
                    istih = 0

        for diag in diags2:
            istih = 0
            for i in range(len(diag) - 1):
                if diag[i] == diag[i + 1] and diag[i] != 0:
                    istih += 1
                    if istih >= 3:
                        return diag[i]
                else:
                    istih = 0
        return 0

    def stupci(self, br_stupca=None):
        stupci = []
        stupac = []

        if br_stupca is None:
            for j in range(7):
                for i in range(self.brojRedaka):
                    stupac.append(self.ploca[i][j])
                stupci.append(stupac)
                stupac = []
            return stupci
        else:
            for i in range(self.brojRedaka):
                stupac.append(self.ploca[i][br_stupca])
            return stupac

    # potez se ostavruje upisom broja stupca u koji igrac zeli staviti svoj znak
    # redak je jedinstveno određen "gravitacijom"
    def legalni_potez(self, br_stupca):
        if self.ploca[0][br_stupca] != 0 or br_stupca < 0 or br_stupca > 6:
            return False
        if self.stupci(br_stupca).count(0) == 0:
            return False
        return True

    def napravi_potez(self, br_stupca, igrac):
        if self.legalni_potez(br_stupca):
            for i in range(self.brojRedaka - 1, -1, -1):
                if self.ploca[i][br_stupca] == 0:
                    self.ploca[i][br_stupca] = igrac
                    break

    def ponisti_potez(self, br_stupca):
        for i in range(self.brojRedaka - 1, -1, -1):
            if self.ploca[i][br_stupca] == 0 and i + 1 < self.brojRedaka:
                self.ploca[i + 1][br_stupca] = 0
            if self.ploca[i][br_stupca] != 0 and i == 0:
                self.ploca[i][br_stupca] = 0

