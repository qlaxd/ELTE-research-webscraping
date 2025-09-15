# Teendőlista a Projekt Befejezéséhez

Ez a dokumentum a projekt befejezéséhez szükséges összes fennmaradó feladatot összegzi, a meglévő dokumentáció és a kód elemzése alapján.

## 1. Fázis: Kritikus Blokkoló Feloldása

-   **[ ] Web Scraping Javítása:** A `requests` alapú scraper cseréje egy `Selenium` alapú, headless böngészőt használó megoldásra, hogy az anti-bot védelem megkerülhető legyen. Ez a legmagasabb prioritású feladat.
    -   *Referencia:* `docs/refactor.md`

## 2. Fázis: Törzslogika Implementálása

-   **[ ] `RowInserter` Véglegesítése:** A `src/reconstruction/row_inserter.py`-ban található placeholder logika lecserélése egy működő algoritmussal, ami helyes kronológiai sorrendbe illeszti be a szegmentált házelnöki felszólalásokat a többi közé.
-   **[ ] `MetadataManager` Bővítése:** Az `agenda_item` hozzárendelésének véglegesítése, hogy az a *ténylegesen* következő felszólalás napirendi pontját kapja meg a beillesztés után.
-   **[ ] `OrderCalculator` Integrálása:** A `place_agenda` oszlop újraszámításának implementálása és integrálása a `DatasetBuilder`-be, hogy az a sorok véglegesítése után fusson le.

## 3. Fázis: Konfiguráció és Funkcióbővítés

-   **[ ] Scraping Szabályok Kiterjesztése:** Új CSS szelektorok hozzáadása a `config/scraping_rules.yaml` fájlhoz a 2012 utáni évek parlamenti üléseihez (ezt a scraper javítása után lehet megtenni).
-   **[ ] CLI Felület Fejlesztése:** A `scripts/run_segmentation.py` parancssori szkript képességeinek bővítése `argparse` segítségével:
    -   `--input`, `--output` argumentumok a fájl elérési utakhoz.
    -   `--start-date`, `--end-date` argumentumok a feldolgozási időszak szűkítéséhez.
    -   `--dry-run` kapcsoló, ami a feldolgozást szimulálja, de nem ír fájlt.
-   **[ ] Feldolgozás Folytatása (Resume Capability):** A szkript képessé tétele a munkafolyamat állapotának mentésére (pl. minden sikeresen feldolgozott ülésnap után), hogy megszakítás esetén onnan lehessen folytatni, ne kelljen elölről kezdeni.

## 4. Fázis: Validáció és Minőségbiztosítás

-   **[ ] Validátorok Teljes Implementálása:**
    -   A `src/segmentation/segment_validator.py` és `src/reconstruction/reconstruction_validator.py` modulokban lévő validációs logikák kiterjesztése és integrálása a fő pipeline-ba.
-   **[ ] Validációs Szkriptek Létrehozása:**
    -   A `scripts/validate_output.py` szkript megírása, ami a kimeneti fájl séma- és adatintegritását ellenőrzi.

## 5. Fázis: Tesztelés

-   **[ ] Unit Tesztek Írása:** Hiányzó unit tesztek megírása minden modulhoz, különös tekintettel a `reconstruction` és `segmentation` logikákra.
-   **[ ] Integrációs Tesztek Írása:** A teljes adatfeldolgozási folyamatot lefedő integrációs tesztek létrehozása, amelyek egy-egy teljes ülésnap feldolgozását szimulálják a bemeneti CSV-től a kimeneti CSV-ig.
-   **[ ] Test Fixture-ök Bővítése:** További, bonyolultabb eseteket lefedő `sample_html.html` és `sample_data.csv` fájlok készítése.

## 6. Fázis: Dokumentáció Befejezése

-   **[ ] Hiányzó Dokumentumok Létrehozása:**
    -   `docs/API.md`: A főbb osztályok és függvények dokumentációja.
    -   `docs/DATA_SCHEMA.md`: A be- és kimeneti CSV fájlok adatsémájának leírása.
    -   `docs/TROUBLESHOOTING.md`: Gyakori hibák és azok megoldásának leírása.
-   **[ ] `README.md` Frissítése:** A futtatási útmutató frissítése az új parancssori argumentumokkal.
