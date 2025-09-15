# Lépésenkénti Terv a Projekt Befejezéséhez

Ez a dokumentum egy priorizált, lépésről-lépésre követhető útmutatót tartalmaz a projekt sikeres befejezéséhez.

### 1. Lépés: A Web Scraper Javítása (Kritikus Blokkoló Feloldása)

*   **Cél:** Működőképessé tenni az adatletöltést a `sejm.gov.pl` oldalról.
*   **Feladat:** A `src/scraping/web_client.py`-ban a `requests` alapú logikát cseréld le `Selenium` és egy headless böngésző (pl. Chrome) használatára. A `docs/refactor.md` részletes útmutatót és kód-példát tartalmaz ehhez.
*   **Ellenőrzés:** A szkriptnek képesnek kell lennie hiba nélkül letölteni egy parlamenti ülésnap HTML tartalmát anélkül, hogy a bot-védelem blokkolná.

### 2. Lépés: A Törzslogika Implementálása

*   **Cél:** A letöltött adatok helyes szegmentálása és újraépítése.
*   **Feladatok:**
    1.  **`RowInserter` implementálása:** A `src/reconstruction/row_inserter.py`-ban valósítsd meg az algoritmust, ami a szétvágott házelnöki szövegrészleteket (új sorokat) a megfelelő helyre illeszti be a többi felszólalás (`chair=0`) közé, a weboldalon látott sorrend alapján.
    2.  **`MetadataManager` finomítása:** A `src/segmentation/metadata_manager.py`-ban, a `RowInserter` működésének ismeretében, pontosítsd az `agenda_item` hozzárendelését.
    3.  **`OrderCalculator` integrálása:** A `src/reconstruction/dataset_builder.py`-ban, miután a `RowInserter` elvégezte a beillesztést és a sorrend helyes, hívd meg az `OrderCalculator`-t a `place_agenda` oszlop újraszámításához (1-től N-ig sorszámozva).
*   **Ellenőrzés:** Egyetlen ülésnap feldolgozása után a kimeneti adatokban a házelnöki beszédek szét vannak vágva és helyes sorrendben szerepelnek a többi felszólalás között, a `place_agenda` pedig folytonos sorszám.

### 3. Lépés: A Feldolgozás Kiterjesztése és Stabilizálása

*   **Cél:** A teljes adathalmaz feldolgozása és a szkript robusztussá tétele.
*   **Feladatok:**
    1.  **Új Scraping Szabályok:** A működő scraperrel tölts le egy 2012 utáni ülésnap HTML-jét, azonosítsd a CSS szelektorokat, és add hozzá az új szabályokat a `config/scraping_rules.yaml` fájlhoz.
    2.  **Validátorok Integrálása:** A `DatasetBuilder` `_process_session` metódusába építsd be a `SegmentValidator` és `ReconstructionValidator` hívásokat, hogy minden ülésnap feldolgozása után ellenőrizd az eredményt.
    3.  **CLI Bővítése:** A `scripts/run_segmentation.py` szkriptet egészítsd ki parancssori argumentum-kezeléssel (`argparse`) a be/kimeneti fájlok, dátumtartományok és `--dry-run` mód megadásához.

### 4. Lépés: Robusztusság és Tesztelés

*   **Cél:** A program megbízhatóságának növelése és a hibák minimalizálása.
*   **Feladatok:**
    1.  **Unit Tesztek:** Írj unit teszteket a `RowInserter`, `OrderCalculator` és a validátor osztályok logikájához.
    2.  **Integrációs Tesztek:** Hozz létre egy tesztet, ami egy teljes ülésnapot feldolgoz az elejétől a végéig, és az eredményt összeveti egy előre elkészített "elvárás" (`expected_output.csv`) fájllal.
    3.  **Feldolgozás Folytatása (Opcionális, de ajánlott):** Implementálj egy egyszerű mechanizmust (pl. egy `progress.txt` fájlba írva az utolsó sikeres dátumot), amivel a szkript képes folytatni a munkát egy esetleges hiba után.

### 5. Lépés: Befejező Munkálatok (Dokumentáció)

*   **Cél:** A projekt átadhatóvá és mások számára is érthetővé tétele.
*   **Feladatok:**
    1.  Hozd létre és töltsd fel tartalommal a hiányzó dokumentációs fájlokat: `docs/API.md`, `docs/DATA_SCHEMA.md`, `docs/TROUBLESHOOTING.md`.
    2.  Frissítsd a `README.md`-t a végleges használati útmutatóval, beleértve az új parancssori opciókat.
