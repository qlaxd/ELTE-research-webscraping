# TODO - A házelnöki beszédek szegmentálásának javítása

Ez a lista tartalmazza a hátralévő feladatokat a projekt helyes működésének eléréséhez a `docs/Webscraping_polish_parlspeech_segmentation_task.md` leírás alapján.

### Prioritási sorrend:

1.  **Dátumtartományra szűrés (1991-2011)**
    -   **Feladat:** Módosítani a `src/main.py` fájlt, hogy a bemeneti CSV-t a feldolgozás legelején szűrje a `1991-01-01` és `2011-12-31` közötti dátumtartományra.
    -   **Indoklás:** Megszünteti a hibákat és a program lassulását, amit a nem támogatott (2011 utáni) oldal-struktúrák feldolgozási kísérlete okoz. Csak a releváns adatokkal fog dolgozni a program.

2.  **Helyes sor-beillesztési logika implementálása**
    -   **Feladat:** Megvalósítani a logikát a `src/reconstruction/row_inserter.py`-ban, ami a feldarabolt házelnöki szegmenseket a megfelelő helyre illeszti be a többi felszólaló közé.
    -   **Indoklás:** Ez a projekt központi eleme, ami jelenleg teljesen hiányzik. A sorrendet a forrás HTML-ben található hiperhivatkozások sorrendje határozza meg.

3.  **`RowInserter` integrálása és `place_agenda` újraszámítása**
    -   **Feladat:** A `src/reconstruction/dataset_builder.py`-ban a jelenlegi `pd.concat` helyett a `RowInserter`-t kell használni. A beillesztés után meg kell hívni a `src/segmentation/order_calculator.py`-t a `place_agenda` oszlop újraszámításához.
    -   **Indoklás:** Biztosítja, hogy a kimeneti adatszerkezet megfeleljen a feladatleírásnak (helyes sorrend és sorszámozás).

4.  **`agenda_item` metaadat hozzárendelése**
    -   **Feladat:** Implementálni a logikát, ami a házelnök új szegmenseihez a sorrendben utána következő felszólalás `agenda_item` értékét rendeli hozzá.
    -   **Indoklás:** A feladatleírás ezt is előírja a helyes metaadatokhoz.

5.  **Validáció és ellenőrzés**
    -   **Feladat:** A `src/reconstruction/reconstruction_validator.py`-ban lévő validációs logika beépítése a folyamat végére, hogy automatikusan ellenőrizze a feldolgozás helyességét (sorszámok, beszédek megőrzése stb.).
    -   **Indoklás:** Biztosítja a kimenet minőségét és a hibák korai felismerését.