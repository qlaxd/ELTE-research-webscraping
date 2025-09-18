### **Architekturális Terv: Parlamenti Felszólalások Szegmentációs Rendszere**

**Verzió:** 1.0
**Dátum:** 2025-08-28

#### **1. Bevezetés és Rendszer-célok**

A projekt célja egy automatizált ETL (Extract, Transform, Load) pipeline létrehozása, amely korrigálja a lengyel parlamenti felszólalásokat tartalmazó adatforrásban azonosított integritási hibát. A hiba az ülést vezető elnök (`chair == 1`) felszólalásainak monolitikus tárolásából ered.

**Architekturális Alapelvek:**

*   **Modularitás:** A rendszert logikailag elkülönülő, önálló felelősséggel bíró komponensekre bontjuk (pl. adatbetöltés, transzformáció, mentés). Ez javítja a karbantarthatóságot és a tesztelhetőséget.
*   **Skálázhatóság:** A rendszert úgy tervezzük, hogy ne csak a jelenlegi ~2GB-os fájllal, hanem lényegesen nagyobb adatmennyiséggel is hatékonyan tudjon működni, mind memória-, mind CPU-kihasználtság szempontjából.
*   **Idempotencia:** A pipeline-nak idempotensnek kell lennie. Ugyanarra a bemeneti adathalmazra futtatva minden alkalommal pontosan ugyanazt a kimenetet kell produkálnia, mellékhatások nélkül. Ez biztosítja a megbízhatóságot és a reprodukálhatóságot.
*   **Konfigurálhatóság:** A rendszer viselkedését (pl. fájlútvonalak, naplózási szint) külső konfiguráción keresztül vezéreljük, elválasztva a kódtól a környezet-specifikus beállításokat.

#### **2. Magas Szintű Rendszerarchitektúra**

A rendszer egy klasszikus, szakaszos adatfeldolgozó folyamatot (pipeline) valósít meg:

`[Forrás CSV] -> [1. Adatbetöltési Réteg] -> [2. Feldolgozás-vezérlő] -> [3. Ülésnap-feldolgozó Modul] -> [4. Adat-aggregációs Réteg] -> [5. Adatkivezetési Réteg] -> [Cél CSV]`

A feldolgozás központi egysége az ülésnap, amely garantálja, hogy az egyes napok transzformációja párhuzamosítható legyen.

#### **3. Komponens-szintű Tervezés**

1.  **Adatbetöltési Réteg (Data Ingestion Layer):**
    *   **Felelősség:** A forrás CSV fájl beolvasása.
    *   **Technológia:** `pandas.read_csv`.
    *   **Skálázhatósági megfontolás:** A memóriahasználat kordában tartása érdekében a fájlt nem egyben, hanem darabokban (chunk-okban) kell feldolgozni a `chunksize` paraméter használatával. Ez lehetővé teszi, hogy a rendszer a rendelkezésre álló RAM méretétől függetlenül működőképes legyen.

2.  **Feldolgozás-vezérlő (Processing Controller):**
    *   **Felelősség:** A beolvasott adatok (vagy chunk-ok) csoportosítása és szétosztása a feldolgozó egységek között.
    *   **Logika:** A vezérlő a `date_presented` oszlop alapján atomi egységekre – ülésnapokra – bontja az adatfolyamot. Ez a csoportosítás a párhuzamosítás kulcsa.

3.  **Ülésnap-feldolgozó Modul (Session Processor Module):**
    *   **Felelősség:** Egyetlen, teljes ülésnap adatainak transzformációja. Ennek egy **állapotmentes (stateless)**, tiszta függvénynek kell lennie, amely egy DataFrame-et kap bemenetként és egy transzformált DataFrame-et ad vissza.
    *   **Alkomponensek:**
        *   **Szegmentációs Szolgáltatás:** Ez a modul felel az elnöki beszéd (`chair == 1`) feldarabolásáért. A javasolt megközelítés egy dinamikus, reguláris kifejezésen alapuló motor, amely a `chair == 0` sorokból futásidőben nyeri ki az elválasztó mintázatokat (a felszólalók neveit/címeit). Ez a dinamizmus biztosítja a robusztusságot a különböző névalakokkal szemben.
        *   **Rekonstrukciós Logika:** Az újonnan generált elnöki szegmensek és az eredeti felszólalói sorok helyes kronológiai sorrendbe fűzése.
        *   **Normalizációs Egység:** A `place_agenda` oszlop újragenerálása (szekvenciális sorszámozás) és az `agenda_item` metaadat korrekt hozzárendelése a specifikáció szerint.

4.  **Adat-aggregációs és Kivezetési Réteg (Aggregation & Egress Layer):**
    *   **Felelősség:** A feldolgozott, de még memóriában lévő ülésnap-DataFrame-ek összefűzése és perzisztálása.
    *   **Technológia:** `pandas.concat` az összefűzéshez, `DataFrame.to_csv` a kivezetéshez. A kimenetet új fájlba írjuk, az eredetit soha nem módosítjuk (idempotencia elve).

#### **4. Konfiguráció Menedzsment**

A rendszer konfigurációját (fájlútvonalak, naplózási szint, párhuzamos szálak száma) a kódtól szigorúan elválasztva kell kezelni. Az `.env` fájl használata erre a célra kiváló. A `python-dotenv` könyvtár segítségével a szkript indításkor betöltheti ezeket a környezeti változókat.

#### **5. Hibakezelés és Naplózás**

*   **Hibakezelés:** A `process_session` modulnak robusztusnak kell lennie. Ha egy ülésnap feldolgozása során hiba lép fel (pl. váratlan adatformátum), a modulnak nem szabad összeomlania. A hibás ülésnapot ki kell hagynia, a hibát részletesen naplóznia kell, és a folyamatnak folytatódnia kell a következő ülésnappal.
*   **Naplózás:** A beépített `logging` modul használata javasolt. Különböző naplózási szinteket (DEBUG, INFO, WARNING, ERROR) kell alkalmazni, hogy a rendszer működése transzparens és utólag is elemezhető legyen.

#### **6. Skálázhatóság és Teljesítményoptimalizálás**

A rendszer teljesítménye két fő ponton optimalizálható:

1.  **Memória (I/O bound):** A `read_csv` `chunksize` paraméterének használata már tárgyalva lett.
2.  **CPU (CPU bound):** Mivel az egyes ülésnapok feldolgozása egymástól teljesen független, a feladat triviálisan párhuzamosítható. A `multiprocessing` könyvtár `Pool` objektumával a feldolgozandó ülésnapok szétoszthatók a rendelkezésre álló összes CPU mag között. Ez a futási időt közel lineárisan csökkentheti a magok számának függvényében.

#### **7. Tesztelési Stratégia**

*   **Unit Tesztek:** A Szegmentációs Szolgáltatás logikáját izoláltan, számos különböző bemeneti szöveggel és elválasztó-listával kell tesztelni (`pytest` keretrendszerrel).
*   **Integrációs Tesztek:** A teljes pipeline-t egy kicsi, de reprezentatív (minden él-esetet tartalmazó) bemeneti CSV fájllal kell tesztelni. A teszt során a generált kimeneti fájlt egy előre elkészített, "helyes" kimeneti fájllal kell összehasonlítani.
