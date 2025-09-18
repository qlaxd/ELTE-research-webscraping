# A Szoftver Felépítése és Működése (`filestructure.md`)

Verzió: 1.0

Ez a dokumentum a lengyel parlamenti felszólalásokat feldolgozó ETL (Extract, Transform, Load) szkript komponenseit, azok felelősségi köreit és a köztük lévő kapcsolatokat írja le.

---

## 1. Magas Szintű Folyamatábra

A rendszer egy klasszikus, adatdarabokon (chunk-okon) alapuló ETL folyamatot valósít meg a nagy méretű bemeneti fájl memóriahatékony kezelése érdekében.

`Konfiguráció (.env)` -> `Fő Vezérlő (process_speeches.py)` -> **CIKLUS** [`Adatbetöltés (chunk)` -> `Ülésnap-feldolgozó (process_session)`] -> `Adatkivezetés (CSV)`

---

## 2. Komponensek Részletesen

### 2.1. Konfiguráció (`.env` fájl)

-   **Felelősség:** A szoftver futtatásához szükséges, környezetfüggő beállítások tárolása a kódtól elválasztva.
-   **Tartalma:**
    -   `INPUT_CSV_PATH`: A bemeneti, feldolgozandó CSV fájl elérési útja.
    -   `OUTPUT_CSV_PATH`: A kimeneti, már feldolgozott CSV fájl mentési helye.
-   **Kapcsolat:** A `Fő Vezérlő` indításkor beolvassa ezeket az értékeket a `python-dotenv` könyvtár segítségével, így a szkript könnyen adaptálható más környezetekhez anélkül, hogy a forráskódot módosítani kellene.

### 2.2. Fő Vezérlő (`src/process_speeches.py`)

-   **Felelősség:** A teljes ETL folyamat vezénylése, az adatfolyam menedzselése és a komponensek munkájának összehangolása.
-   **Működési Lépései:**
    1.  **Inicializálás:** Beolvassa a konfigurációt a `.env` fájlból.
    2.  **Iteratív Adatbetöltés:** Létrehoz egy `pandas` iterátort, amely a bemeneti CSV-t `chunksize` méretű darabokban olvassa be. Ez a kulcsa a skálázhatóságnak.
    3.  **Ülésnap-integritás Kezelése:** Ciklusonként összefűzi az előző ciklusból megmaradt, vélhetően töredékes utolsó ülésnapot tartalmazó sorokat (`leftover_df`) az aktuális `chunk`-kal. Ezzel biztosítja, hogy egy ülésnap adatai ne vágódjanak ketté két feldolgozási egység között.
    4.  **Feldolgozás Delegálása:** Az összefűzött adathalmazból a teljes, feldolgozható ülésnapokat `date_presented` szerint csoportosítja, és minden egyes ülésnapra meghívja az `Ülésnap-feldolgozó` függvényt.
    5.  **Eredmények Aggregálása:** A feldolgozott ülésnapokból visszaérkező DataFrame-eket egy listában gyűjti.
    6.  **Adatkivezetés:** A ciklus végeztével összefűzi a feldolgozott darabokat egyetlen nagy DataFrame-mé, és elmenti azt a konfigurációban megadott kimeneti CSV fájlba.

### 2.3. Ülésnap-feldolgozó (`process_session` függvény)

-   **Felelősség:** A rendszer központi üzleti logikájának végrehajtása. Egyetlen, teljes ülésnap adatait kapja meg és alakítja át a specifikáció szerint. **Fontos, hogy ez egy állapotmentes (stateless) függvény**, ami azt jelenti, hogy a működése csak a bemeneti paramétereitől függ, és nincsenek külső mellékhatásai.
-   **Belső Logikája:**
    1.  **Szétválasztás:** A bemeneti DataFrame-et két részre bontja: az elnök sorára (`chair == 1`) és a többi felszólaló soraira (`chair == 0`).
    2.  **Elválasztók Kinyerése:** A `chair == 0` sorokból kigyűjti a felszólalók nevét és titulusát. Ezek fognak elválasztó mintaként (`delimiter`) szolgálni.
    3.  **Szegmentálás:** Az elnök teljes beszédét (`text`) egy reguláris kifejezés (`re.split`) segítségével feldarabolja a kinyert elválasztók mentén.
    4.  **Újraépítés:** Egy új, üres listába kezdi el felépíteni a transzformált ülésnapot. Sorban halad a `chair == 0` felszólalókon, és mindegyik elé beilleszti a hozzá tartozó, újonnan létrehozott elnöki beszéd-szegmenst. Eközben a specifikáció szerint beállítja az `agenda_item` értékét és másolja a metaadatokat.
    5.  **Finalizálás:** Az újraépített sorokból egy új DataFrame-et készít, újraszámolja a `place_agenda` oszlopot (1-től kezdődő sorszámozás), majd ezt a kész, transzformált DataFrame-et adja vissza a `Fő Vezérlőnek`.

### 2.4. Adattárolás (`data/` mappa)

-   **Felelősség:** A bemeneti és kimeneti adatok tárolása.
-   **Tartalma:**
    -   `Szejm_0731_1.csv`: A forrásadat, amelyet a szkript olvas.
    -   `Szejm_0731_1_segmented.csv` (létrehozandó): A feldolgozás eredménye, amelyet a szkript ír.
-   **Kapcsolat:** A `Fő Vezérlő` innen olvassa a bemenetet és ide írja a kimenetet a `.env` fájlban megadott útvonalak alapján.
