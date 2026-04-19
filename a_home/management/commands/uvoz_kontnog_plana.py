"""
Management komanda za uvoz Analitičkog kontnog plana FBiH.

Korištenje:
    python manage.py uvoz_kontnog_plana

Smjestite ovaj fajl u:
    a_home/management/commands/uvoz_kontnog_plana.py

Kreirajte i __init__.py fajlove:
    a_home/management/__init__.py
    a_home/management/commands/__init__.py
"""

from django.core.management.base import BaseCommand
from a_home.models import Konto


KONTNI_PLAN = [
    # ═══════════════════════════════════════════════
    # KLASA 0 - DUGOROČNA IMOVINA
    # ═══════════════════════════════════════════════
    ("010",   "Kapitalizirana ulaganja u razvoj",                           "aktiva"),
    ("0100",  "Dugoročna ulaganja u razvoj materijala, uređaja i proizvoda","aktiva"),
    ("0101",  "Dugoročna ulaganja u razvoj tehnologije proizvodnje",        "aktiva"),
    ("0102",  "Dugoročna ulaganja u razvoj tržišta (marketing)",            "aktiva"),
    ("0103",  "Dugoročna ulaganja u razvoj usluga",                         "aktiva"),
    ("0108",  "Ostala dugoročna ulaganja u razvoj",                         "aktiva"),
    ("011",   "Koncesije, patenti, licence, zaštitni znakovi i druga prava","aktiva"),
    ("0110",  "Koncesije",                                                  "aktiva"),
    ("0111",  "Patenti",                                                    "aktiva"),
    ("0112",  "Licence",                                                    "aktiva"),
    ("0113",  "Prava na model, uzorak, robni ili uslužni žig",             "aktiva"),
    ("0114",  "Industrijska znanja (know-how)",                             "aktiva"),
    ("0115",  "Specijalne licence",                                         "aktiva"),
    ("0118",  "Ostala dugoročna prava",                                     "aktiva"),
    ("012",   "Goodwill",                                                   "aktiva"),
    ("0120",  "Goodwill utvrđen kupovinom pravnog lica",                   "aktiva"),
    ("0121",  "Goodwill utvrđen putem poslovne kombinacije spajanja",      "aktiva"),
    ("014",   "Ostala nematerijalna imovina",                               "aktiva"),
    ("0140",  "Računarski programi - software",                             "aktiva"),
    ("0141",  "Izdaci za komasacije i druga dugoročna unapređenja",        "aktiva"),
    ("0142",  "Izdaci za arondacije",                                       "aktiva"),
    ("0143",  "Izdaci za višegodišnji zakup zemljišta, zasada, šuma",     "aktiva"),
    ("0144",  "Izdaci za višegodišnje pravo korištenja priplodne stoke",  "aktiva"),
    ("0148",  "Ulaganja u ostalu nematerijalnu imovinu",                    "aktiva"),
    ("015",   "Nematerijalna imovina u pripremi",                           "aktiva"),
    ("0150",  "Koncesije, patenti, licence i slična prava u pripremi",    "aktiva"),
    ("0152",  "Kapitalizirana ulaganja u razvoj - ulaganja u toku",        "aktiva"),
    ("0158",  "Ostala nematerijalna ulaganja u pripremi",                   "aktiva"),
    ("017",   "Avansi za nematerijalna sredstva",                           "aktiva"),
    ("0170",  "Avansi za nematerijalna ulaganja dobavljačima u zemlji",   "aktiva"),
    ("0171",  "Avansi za nematerijalna ulaganja dobavljačima u inostranstvu","aktiva"),
    ("0177",  "Avansi za ostalu nematerijalnu imovinu",                     "aktiva"),
    ("0179",  "Vrijednosno usklađivanje datih avansa za nematerijalna sredstva","aktiva"),
    ("018",   "Vrijednosna usklađivanja nematerijalne imovine",            "aktiva"),
    ("0180",  "Vrijednosno usklađivanje ulaganja u razvoj",                "aktiva"),
    ("0181",  "Vrijednosno usklađivanje koncesija, patenta, licenci",     "aktiva"),
    ("0182",  "Vrijednosno usklađivanje goodwill-a",                       "aktiva"),
    ("0188",  "Vrijednosno usklađivanje ostale nematerijalne imovine",     "aktiva"),
    ("019",   "Ispravka vrijednosti nematerijalne imovine",                 "aktiva"),
    ("0190",  "Ispravka vrijednosti ulaganja u razvoj",                     "aktiva"),
    ("0191",  "Ispravka vrijednosti koncesija, patenta, licenci",          "aktiva"),
    ("0198",  "Ispravka vrijednosti ostalih nematerijalnih sredstava",     "aktiva"),
    ("020",   "Zemljište",                                                  "aktiva"),
    ("0200",  "Vlastito zemljište",                                         "aktiva"),
    ("02001", "Poljoprivredno zemljište",                                   "aktiva"),
    ("02002", "Građevinsko zemljište",                                     "aktiva"),
    ("02003", "Šumsko zemljište",                                          "aktiva"),
    ("0201",  "Ulaganja u tuđe zemljište",                                 "aktiva"),
    ("0208",  "Ostala zemljišta",                                           "aktiva"),
    ("021",   "Građevinski objekti",                                       "aktiva"),
    ("0210",  "Vlastiti građevinski objekti",                              "aktiva"),
    ("02100", "Zgrade uprave i administracije",                             "aktiva"),
    ("02101", "Proizvodne zgrade",                                          "aktiva"),
    ("02102", "Poslovne zgrade trgovine",                                   "aktiva"),
    ("02103", "Zgrade hotela, motela i restorana",                         "aktiva"),
    ("02104", "Skladišta, silosi, garaže, sušione i hladnjače",          "aktiva"),
    ("02105", "Putevi, mostovi i parkinzi",                                 "aktiva"),
    ("02106", "Građevinski objekti van upotrebe",                          "aktiva"),
    ("0211",  "Ulaganja u tuđe građevinske objekte",                      "aktiva"),
    ("0212",  "Stambene zgrade i stanovi",                                  "aktiva"),
    ("022",   "Postrojenja i oprema (mašine)",                             "aktiva"),
    ("0220",  "Postrojenja za preradu, obradu i proizvodnju",              "aktiva"),
    ("0221",  "Mašine i oprema",                                           "aktiva"),
    ("0222",  "Kancelarijska i IT oprema",                                  "aktiva"),
    ("0223",  "Oprema za videonadzor i sigurnost podataka",                 "aktiva"),
    ("0224",  "Oprema za zagrijavanje i ventilaciju",                       "aktiva"),
    ("0225",  "Telefonske centrale i aparati",                              "aktiva"),
    ("0226",  "Oprema u trgovini i ugostiteljstvu",                        "aktiva"),
    ("0227",  "Postrojenja, oprema i mašine van upotrebe",                "aktiva"),
    ("0228",  "Ostala postrojenja, oprema i mašine",                      "aktiva"),
    ("023",   "Alati, pogonski i kancelarijski namještaj",                "aktiva"),
    ("0230",  "Specijalni alati",                                           "aktiva"),
    ("0231",  "Univerzalni i ostali alati",                                 "aktiva"),
    ("0232",  "Mjerni i kontrolni instrumenti",                             "aktiva"),
    ("0233",  "Pogonski i skladišni namještaj",                           "aktiva"),
    ("0234",  "Namještaj u trgovini, ugostiteljstvu i uslužnim djelatnostima","aktiva"),
    ("0235",  "Kancelarijski namještaj",                                   "aktiva"),
    ("0236",  "Audio i video aparati",                                      "aktiva"),
    ("0238",  "Ostali krupni inventar za opremanje i uređenje",           "aktiva"),
    ("024",   "Transportna sredstva",                                       "aktiva"),
    ("0240",  "Transportna sredstva u cestovnom prometu",                   "aktiva"),
    ("0241",  "Transportna sredstva u željezničkom prometu",              "aktiva"),
    ("0242",  "Transportna sredstva u riječnom i pomorskom prometu",      "aktiva"),
    ("0243",  "Transportna sredstva u zračnom prometu",                   "aktiva"),
    ("0244",  "Transportna sredstva za internu manipulaciju",               "aktiva"),
    ("0248",  "Ostala transportna sredstva i uređaji",                     "aktiva"),
    ("025",   "Nekretnine, postrojenja i oprema u pripremi",               "aktiva"),
    ("0250",  "Investicije u toku: zemljišta",                              "aktiva"),
    ("0251",  "Investicije u toku: građevinski objekti",                   "aktiva"),
    ("0252",  "Investicije u toku: postrojenja i oprema",                  "aktiva"),
    ("0253",  "Investicije u toku: alati i namještaj",                    "aktiva"),
    ("0254",  "Investicije u toku: transportna sredstva",                   "aktiva"),
    ("0256",  "Investicije u toku: stambene zgrade i stanovi",             "aktiva"),
    ("0258",  "Investicije u toku: ostala materijalna imovina",            "aktiva"),
    ("026",   "Ostala materijalna imovina",                                 "aktiva"),
    ("0260",  "Knjige trajne i dugoročne vrijednosti",                    "aktiva"),
    ("0261",  "Muzejski eksponati",                                         "aktiva"),
    ("0267",  "Ostala stalna materijalna imovina",                          "aktiva"),
    ("027",   "Avansi za nekretnine, postrojenja i opremu",                "aktiva"),
    ("0270",  "Avansi za zemljišta",                                        "aktiva"),
    ("0271",  "Avansi za građevinske objekte",                             "aktiva"),
    ("0272",  "Avansi za postrojenja i opremu",                            "aktiva"),
    ("0273",  "Avansi za alate i namještaj",                              "aktiva"),
    ("0274",  "Avansi za transportna sredstva",                             "aktiva"),
    ("028",   "Vrijednosna usklađivanja nekretnina, postrojenja i opreme","aktiva"),
    ("029",   "Ispravka vrijednosti nekretnina, postrojenja i opreme",     "aktiva"),
    ("0291",  "Ispravka vrijednosti građevinskih objekata",                "aktiva"),
    ("0293",  "Ispravka vrijednosti postrojenja i opreme",                 "aktiva"),
    ("0294",  "Ispravka vrijednosti transportnih sredstava",                "aktiva"),
    ("0298",  "Ispravka vrijednosti ostale materijalne imovine",           "aktiva"),
    ("060",   "Dugoročni finansijski plasmani u povezana pravna lica",     "aktiva"),
    ("061",   "Dugoročni finansijski plasmani u ostala pravna lica",       "aktiva"),
    ("062",   "Dugoročni zajmovi",                                          "aktiva"),
    ("063",   "Dugoročni depoziti",                                         "aktiva"),
    ("065",   "Ostali dugoročni finansijski plasmani",                      "aktiva"),
    ("069",   "Ispravka vrijednosti dugoročnih fin. plasmana",             "aktiva"),

    # ═══════════════════════════════════════════════
    # KLASA 1 - ZALIHE
    # ═══════════════════════════════════════════════
    ("100",   "Sirovine i materijal",                                       "aktiva"),
    ("1000",  "Sirovine i materijal na skladištu",                        "aktiva"),
    ("1001",  "Sirovine i materijal u obradi i preradi",                   "aktiva"),
    ("101",   "Rezervni dijelovi",                                          "aktiva"),
    ("102",   "Ambalaža",                                                   "aktiva"),
    ("103",   "Sitan inventar na skladištu",                              "aktiva"),
    ("104",   "Sitan inventar u upotrebi",                                  "aktiva"),
    ("109",   "Ispravka vrijednosti sirovina i materijala",                 "aktiva"),
    ("120",   "Gotovi proizvodi",                                           "aktiva"),
    ("130",   "Roba na skladištu",                                          "aktiva"),
    ("1300",  "Nabavna vrijednost robe na skladištu",                      "aktiva"),
    ("131",   "Roba u prodavnicama",                                        "aktiva"),
    ("132",   "Roba u transportu",                                          "aktiva"),
    ("133",   "Roba data u konsignaciju",                                   "aktiva"),
    ("139",   "Ispravka vrijednosti robe",                                  "aktiva"),
    ("150",   "Dati avansi za materijal i sirovine",                       "aktiva"),
    ("151",   "Dati avansi za robu",                                        "aktiva"),
    ("152",   "Dati avansi za usluge",                                      "aktiva"),

    # ═══════════════════════════════════════════════
    # KLASA 2 - GOTOVINA, POTRAŽIVANJA, PLASMANI
    # ═══════════════════════════════════════════════
    ("200",   "Gotovina u blagajni",                                        "aktiva"),
    ("2000",  "Gotovina u domaćoj valuti",                                 "aktiva"),
    ("2001",  "Gotovina u stranoj valuti",                                  "aktiva"),
    ("201",   "Gotovina na računima kod banaka",                            "aktiva"),
    ("2010",  "Žiro-račun",                                                "aktiva"),
    ("2011",  "Devizni račun",                                              "aktiva"),
    ("2012",  "Posebni namjenski računi",                                   "aktiva"),
    ("202",   "Gotovinski ekvivalenti",                                     "aktiva"),
    ("203",   "Ostala gotovina",                                             "aktiva"),
    ("204",   "Akreditivi",                                                  "aktiva"),
    ("205",   "Čekovi",                                                     "aktiva"),
    ("209",   "Ispravka vrijednosti gotovine i ekvivalenata",               "aktiva"),
    ("210",   "Potraživanja od kupaca u zemlji",                            "aktiva"),
    ("2100",  "Potraživanja od kupaca - domaća lica",                     "aktiva"),
    ("211",   "Potraživanja od kupaca u inostranstvu",                      "aktiva"),
    ("212",   "Potraživanja od povezanih pravnih lica",                     "aktiva"),
    ("213",   "Potraživanja po osnovu datih avansa",                        "aktiva"),
    ("214",   "Potraživanja po osnovu vrijednosnih papira",                 "aktiva"),
    ("215",   "Potraživanja za kamate i dividende",                         "aktiva"),
    ("219",   "Ispravka vrijednosti potraživanja od prodaje",               "aktiva"),
    ("230",   "Potraživanja od zaposlenih",                                  "aktiva"),
    ("231",   "Potraživanja od organa i institucija",                        "aktiva"),
    ("232",   "Potraživanja za naknade od osiguranja",                       "aktiva"),
    ("233",   "Potraživanja za refundacije i subvencije",                    "aktiva"),
    ("239",   "Ispravka vrijednosti ostalih kratkoročnih potraživanja",      "aktiva"),
    ("270",   "Potraživanja za PDV - odbitni ulazni porez",                  "aktiva"),
    ("2700",  "Ulazni PDV po stopi 17%",                                     "aktiva"),
    ("2701",  "Ulazni PDV po stopi 0%",                                      "aktiva"),
    ("271",   "Potraživanja za prethodni porez - pretporez",                  "aktiva"),
    ("280",   "Kratkoročna razgraničenja - unaprijed plaćeni troškovi",      "aktiva"),
    ("281",   "Kratkoročna razgraničenja - obračunati prihodi",              "aktiva"),

    # ═══════════════════════════════════════════════
    # KLASA 3 - KAPITAL
    # ═══════════════════════════════════════════════
    ("300",   "Dionički kapital",                                            "pasiva"),
    ("301",   "Kapital u d.o.o.",                                            "pasiva"),
    ("302",   "Državni kapital",                                             "pasiva"),
    ("303",   "Zadružni kapital",                                            "pasiva"),
    ("308",   "Ostali oblici vlasničkog kapitala",                           "pasiva"),
    ("320",   "Zakonske rezerve",                                            "pasiva"),
    ("321",   "Statutarne i druge rezerve",                                  "pasiva"),
    ("322",   "Rezerve iz dobiti",                                           "pasiva"),
    ("340",   "Dobit tekuće godine",                                         "pasiva"),
    ("341",   "Neraspoređena dobit ranijih godina",                          "pasiva"),
    ("350",   "Gubitak tekuće godine",                                       "pasiva"),
    ("351",   "Nepokriveni gubitak ranijih godina",                          "pasiva"),

    # ═══════════════════════════════════════════════
    # KLASA 4 - OBAVEZE, REZERVISANJA, RAZGRANIČENJA
    # ═══════════════════════════════════════════════
    ("400",   "Dugoročna rezervisanja za troškove i rizike",                 "pasiva"),
    ("401",   "Rezervisanja za otpremnine i jubilarene nagrade",             "pasiva"),
    ("402",   "Rezervisanja za sudske sporove",                              "pasiva"),
    ("403",   "Rezervisanja za troškove obnavljanja prirodnih bogatstava",   "pasiva"),
    ("408",   "Ostala dugoročna rezervisanja",                               "pasiva"),
    ("409",   "Odgođene porezne obaveze",                                    "pasiva"),
    ("410",   "Dugoročni krediti banaka u zemlji",                           "pasiva"),
    ("411",   "Dugoročni krediti banaka u inostranstvu",                     "pasiva"),
    ("412",   "Dugoročne obaveze prema dobavljačima",                        "pasiva"),
    ("413",   "Dugoročne obaveze po osnovu finansijskog lizinga",            "pasiva"),
    ("414",   "Emitovane obveznice",                                         "pasiva"),
    ("415",   "Dugoročne obaveze prema povezanim pravnim licima",            "pasiva"),
    ("418",   "Ostale dugoročne obaveze",                                    "pasiva"),
    ("420",   "Kratkoročni krediti banaka u zemlji",                         "pasiva"),
    ("421",   "Kratkoročni krediti banaka u inostranstvu",                   "pasiva"),
    ("422",   "Kratkoročne obaveze po osnovu finansijskog lizinga",          "pasiva"),
    ("423",   "Obaveze po osnovu emitovanih kratkoročnih obveznica",         "pasiva"),
    ("424",   "Obaveze po osnovu kratkoročnih vrijednosnih papira",          "pasiva"),
    ("425",   "Obaveze prema povezanim pravnim licima",                      "pasiva"),
    ("428",   "Ostale kratkoročne finansijske obaveze",                      "pasiva"),
    ("430",   "Obaveze prema dobavljačima u zemlji",                         "pasiva"),
    ("4300",  "Obaveze prema dobavljačima - domaća lica",                   "pasiva"),
    ("431",   "Obaveze prema dobavljačima u inostranstvu",                   "pasiva"),
    ("432",   "Obaveze prema dobavljačima - povezana lica",                  "pasiva"),
    ("433",   "Primljeni avansi, depoziti i kaucije",                        "pasiva"),
    ("434",   "Obaveze po osnovu vrijednosnih papira",                       "pasiva"),
    ("435",   "Obaveze za kamate",                                           "pasiva"),
    ("436",   "Dividende i učešća u dobiti",                                 "pasiva"),
    ("438",   "Ostale kratkoročne obaveze iz poslovanja",                    "pasiva"),
    ("450",   "Obaveze za neto plaće i naknade zaposlenih",                 "pasiva"),
    ("451",   "Obaveze za poreze i doprinose na plaće",                     "pasiva"),
    ("4510",  "Obaveze za porez na dohodak iz plaća zaposlenih",           "pasiva"),
    ("4511",  "Obaveze za doprinos za PIO/MIO iz plaća",                   "pasiva"),
    ("4512",  "Obaveze za doprinos za zdravstveno osiguranje iz plaća",    "pasiva"),
    ("4513",  "Obaveze za doprinos za osiguranje od nezaposlenosti iz plaća","pasiva"),
    ("4514",  "Obaveze za doprinos za PIO/MIO na plaće",                   "pasiva"),
    ("4515",  "Obaveze za doprinos za zdravstveno osiguranje na plaće",    "pasiva"),
    ("4516",  "Obaveze za doprinos za osiguranje od nezaposlenosti na plaće","pasiva"),
    ("452",   "Obaveze za naknade plaća",                                   "pasiva"),
    ("453",   "Obaveze za naknade troškova zaposlenih",                      "pasiva"),
    ("454",   "Obaveze za honorare i autorske naknade",                      "pasiva"),
    ("455",   "Obaveze za naknade fizičkim licima van radnog odnosa",        "pasiva"),
    ("458",   "Ostale obaveze prema zaposlenim",                             "pasiva"),
    ("460",   "Obaveze za dividende",                                        "pasiva"),
    ("461",   "Obaveze prema osnivačima i članovima",                        "pasiva"),
    ("462",   "Obaveze prema organima upravljanja",                          "pasiva"),
    ("463",   "Obaveze prema vlastitim dionicama",                           "pasiva"),
    ("465",   "Obaveze za porez na dobit",                                   "pasiva"),
    ("466",   "Obaveze za naknadu štete",                                    "pasiva"),
    ("468",   "Ostale obaveze",                                              "pasiva"),
    ("470",   "Obaveze za PDV",                                              "pasiva"),
    ("4700",  "Obaveze za PDV po stopi 17%",                                "pasiva"),
    ("4701",  "Obaveze za PDV po stopi 0%",                                 "pasiva"),
    ("471",   "Obaveze za PDV po osnovu uvoza",                              "pasiva"),
    ("472",   "Obaveze za razliku PDV",                                      "pasiva"),
    ("473",   "Pretplatni račun PDV",                                        "pasiva"),
    ("480",   "Obaveze za porez na promet",                                  "pasiva"),
    ("481",   "Obaveze za akcize",                                           "pasiva"),
    ("482",   "Obaveze za carinu i uvozne dažbine",                         "pasiva"),
    ("483",   "Obaveze za porez na imovinu",                                 "pasiva"),
    ("484",   "Obaveze za komunalne takse i naknade",                        "pasiva"),
    ("485",   "Obaveze za ostale poreze",                                    "pasiva"),
    ("486",   "Obaveze za doprinose",                                        "pasiva"),
    ("488",   "Ostale obaveze za poreze i doprinose",                        "pasiva"),
    ("490",   "Kratkoročna rezervisanja za troškove i rizike",               "pasiva"),
    ("491",   "Kratkoročna rezervisanja za sudske sporove",                  "pasiva"),
    ("492",   "Kratkoročna rezervisanja za garantne rokove",                 "pasiva"),
    ("498",   "Ostala kratkoročna rezervisanja",                             "pasiva"),
    ("499",   "Odgođeni prihodi i kratkoročna razgraničenja",               "pasiva"),

    # ═══════════════════════════════════════════════
    # KLASA 5 - RASHODI
    # ═══════════════════════════════════════════════
    ("500",   "Nabavna vrijednost prodate robe",                             "rashod"),
    ("510",   "Troškovi materijala za izradu",                               "rashod"),
    ("511",   "Troškovi ostalog materijala",                                 "rashod"),
    ("512",   "Troškovi goriva i energije",                                  "rashod"),
    ("513",   "Troškovi ambalaže",                                           "rashod"),
    ("514",   "Troškovi sitnog inventara",                                   "rashod"),
    ("515",   "Troškovi pisarničkog i administrativnog materijala",          "rashod"),
    ("518",   "Ostali materijalni troškovi",                                 "rashod"),
    ("520",   "Troškovi bruto plaća",                                       "rashod"),
    ("521",   "Troškovi naknada plaća",                                     "rashod"),
    ("522",   "Troškovi naknada fizičkim licima van radnog odnosa",          "rashod"),
    ("523",   "Troškovi naknada po ugovorima o djelu i autorskim ugovorima","rashod"),
    ("524",   "Troškovi naknada zaposlenim",                                 "rashod"),
    ("525",   "Troškovi stipendija i školarina",                             "rashod"),
    ("526",   "Troškovi doprinosa na teret poslodavca",                      "rashod"),
    ("528",   "Ostali troškovi zaposlenih",                                  "rashod"),
    ("530",   "Troškovi transportnih usluga",                                "rashod"),
    ("531",   "Troškovi usluga održavanja",                                  "rashod"),
    ("532",   "Troškovi zakupa",                                             "rashod"),
    ("533",   "Troškovi komunalnih usluga",                                  "rashod"),
    ("534",   "Troškovi usluga obrade podataka",                             "rashod"),
    ("535",   "Troškovi istraživanja",                                       "rashod"),
    ("536",   "Troškovi platnog prometa",                                    "rashod"),
    ("537",   "Troškovi sajmova i reklame",                                  "rashod"),
    ("538",   "Troškovi ostalih usluga",                                     "rashod"),
    ("540",   "Troškovi amortizacije nematerijalne imovine",                 "rashod"),
    ("541",   "Troškovi amortizacije nekretnina, postrojenja i opreme",      "rashod"),
    ("542",   "Troškovi amortizacije investicijskih nekretnina",             "rashod"),
    ("543",   "Troškovi amortizacije biološke imovine",                      "rashod"),
    ("544",   "Troškovi amortizacije imovine s pravom korištenja",          "rashod"),
    ("548",   "Ostali troškovi amortizacije",                                "rashod"),
    ("549",   "Troškovi rezervisanja",                                       "rashod"),
    ("550",   "Troškovi platnog prometa - naknade bankama",                  "rashod"),
    ("551",   "Troškovi osiguranja",                                         "rashod"),
    ("552",   "Troškovi reprezentacije",                                     "rashod"),
    ("553",   "Troškovi reklame i propagande",                               "rashod"),
    ("554",   "Troškovi registracije vozila i plovnih objekata",             "rashod"),
    ("555",   "Troškovi poreza i doprinosa",                                 "rashod"),
    ("556",   "Troškovi članarina",                                          "rashod"),
    ("557",   "Troškovi stručnog obrazovanja i usavršavanja",                "rashod"),
    ("558",   "Troškovi štampanja i kopiranja",                              "rashod"),
    ("559",   "Ostali nematerijalni troškovi",                               "rashod"),
    ("560",   "Rashodi kamata za dugoročne obaveze",                         "rashod"),
    ("561",   "Rashodi kamata za kratkoročne obaveze",                       "rashod"),
    ("562",   "Rashodi po osnovu negativnih kursnih razlika",                "rashod"),
    ("563",   "Rashodi po osnovu učešća u gubitku",                          "rashod"),
    ("564",   "Rashodi po osnovu smanjenja fer vrijednosti fin. imovine",   "rashod"),
    ("565",   "Rashodi od prodaje finansijskih instrumenata",                "rashod"),
    ("568",   "Ostali finansijski rashodi",                                  "rashod"),
    ("570",   "Rashodi po osnovu rashodovanja i prodaje imovine",            "rashod"),
    ("571",   "Rashodi po osnovu otpisa potraživanja",                       "rashod"),
    ("572",   "Kazne i penali",                                              "rashod"),
    ("573",   "Rashodi po osnovu donacija",                                  "rashod"),
    ("574",   "Manjkovi imovine",                                            "rashod"),
    ("578",   "Ostali rashodi i gubici",                                     "rashod"),

    # ═══════════════════════════════════════════════
    # KLASA 6 - PRIHODI
    # ═══════════════════════════════════════════════
    ("600",   "Prihodi od prodaje robe na domaćem tržištu",               "prihod"),
    ("601",   "Prihodi od prodaje robe na inostranom tržištu",             "prihod"),
    ("602",   "Prihodi od prodaje robe na malo",                           "prihod"),
    ("610",   "Prihodi od prodaje gotovih proizvoda na domaćem tržištu",  "prihod"),
    ("611",   "Prihodi od prodaje gotovih proizvoda na inostr. tržištu",  "prihod"),
    ("620",   "Prihodi od prodaje usluga na domaćem tržištu",             "prihod"),
    ("621",   "Prihodi od prodaje usluga na inostranom tržištu",          "prihod"),
    ("650",   "Prihodi od subvencija, dotacija i regresa",                 "prihod"),
    ("651",   "Prihodi od zakupnina",                                      "prihod"),
    ("652",   "Prihodi od tantijema i licencnih naknada",                  "prihod"),
    ("653",   "Prihodi od kompenzacija za troškove",                       "prihod"),
    ("658",   "Ostali poslovni prihodi",                                   "prihod"),
    ("660",   "Prihodi od dividendi i učešća u dobiti",                   "prihod"),
    ("661",   "Prihodi od kamata",                                         "prihod"),
    ("662",   "Prihodi po osnovu pozitivnih kursnih razlika",              "prihod"),
    ("663",   "Prihodi od prodaje finansijskih instrumenata",              "prihod"),
    ("664",   "Prihodi po osnovu povećanja fer vrijednosti fin. imovine",  "prihod"),
    ("668",   "Ostali finansijski prihodi",                                "prihod"),
    ("670",   "Prihodi od prodaje imovine",                                "prihod"),
    ("671",   "Prihodi po osnovu ukidanja rezervisanja",                   "prihod"),
    ("672",   "Prihodi od naplaćenih otpisanih potraživanja",              "prihod"),
    ("673",   "Prihodi od donacija",                                       "prihod"),
    ("674",   "Prihodi od viškova imovine",                               "prihod"),
    ("678",   "Ostali prihodi i dobici",                                   "prihod"),

    # ═══════════════════════════════════════════════
    # KLASA 7 - OTVARANJE I ZAKLJUČAK
    # ═══════════════════════════════════════════════
    ("700",   "Otvaranje konta aktive",                                    "aktiva"),
    ("701",   "Otvaranje konta pasive",                                    "pasiva"),
    ("710",   "Zaključak konta prihoda",                                   "prihod"),
    ("711",   "Zaključak konta rashoda",                                   "rashod"),
    ("720",   "Obračun dobiti ili gubitka",                                "pasiva"),
    ("730",   "Zaključak konta aktive",                                    "aktiva"),
    ("731",   "Zaključak konta pasive",                                    "pasiva"),

    # ═══════════════════════════════════════════════
    # KLASA 8 - VANBILANSNA EVIDENCIJA
    # ═══════════════════════════════════════════════
    ("880",   "Tuđa imovina primljena na čuvanje",                        "izvanbil"),
    ("881",   "Tuđa imovina primljena na obradu",                          "izvanbil"),
    ("882",   "Tuđa imovina primljena na korištenje",                     "izvanbil"),
    ("883",   "Primljene garancije i jemstva",                              "izvanbil"),
    ("884",   "Dati avansi bez fakture",                                    "izvanbil"),
    ("885",   "Vrijednosni papiri dati u zalog",                           "izvanbil"),
    ("886",   "Obaveze po sudskim presudama",                               "izvanbil"),
    ("888",   "Ostala vanbilansna aktiva",                                  "izvanbil"),
    ("890",   "Obaveze za tuđu imovinu na čuvanju",                       "izvanbil"),
    ("891",   "Obaveze za tuđu imovinu u obradi",                          "izvanbil"),
    ("892",   "Obaveze za tuđu imovinu na korištenju",                    "izvanbil"),
    ("893",   "Date garancije i jemstva",                                   "izvanbil"),
    ("898",   "Ostala vanbilansna pasiva",                                  "izvanbil"),
]


class Command(BaseCommand):
    help = 'Uvoz Analitičkog kontnog plana FBiH u bazu podataka'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Obriši sve postojeće konte prije uvoza',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Konto.objects.count()
            Konto.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Obrisano {count} konta.'))

        kreirano = 0
        azurirano = 0

        for broj, naziv, tip in KONTNI_PLAN:
            obj, created = Konto.objects.update_or_create(
                broj=broj,
                defaults={
                    'naziv': naziv,
                    'tip': tip,
                    'aktivan': True,
                }
            )
            if created:
                kreirano += 1
            else:
                azurirano += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Uvoz završen!\n'
            f'  Kreirano: {kreirano} konta\n'
            f'  Ažurirano: {azurirano} konta\n'
            f'  Ukupno: {kreirano + azurirano} konta\n'
        ))
