  A feladat a data/Szejm_0731_1.csv fájlban található parlamenti felszólalások adatainak korrekciója, kifejezetten a házelnök (Marszałek) beszédeinek szegmentálása.

  A probléma megértése


   1. Kiindulási állapot: A jelenlegi CSV fájlban minden parlamenti ülésnaphoz tartozik egy sor, ahol a chair oszlop értéke 1. Ez a sor a házelnök (Marszałek) felszólalását tartalmazza. A
      probléma az, hogy ez a "felszólalás" valójában az összes, aznap elhangzott házelnöki hozzászólás egyetlen szövegblokkba fűzve. A többi képviselő felszólalásai már külön sorokban, helyesen
      szerepelnek az adathalmazban (chair=0).


   2. Cél: A hosszú, egybefüggő házelnöki szöveget fel kell darabolni a tényleges hozzászólalásai szerint, és ezeket új sorokként kell beilleszteni a CSV-be a megfelelő kronológiai sorrendben,
      a többi képviselő felszólalásai közé.


  A szegmentálás menete

  A Webscraping_polish_parlspeech_segmentation_task.md és a forrásoldalak HTML-struktúrájának elemzése alapján a szegmentálást a következőképpen kell elvégezni:


   1. Azonosítás: Minden ülésnapon meg kell keresni azt az egy sort, ahol a chair oszlop értéke 1.


   2. Forrásoldal lekérése: Ennek a sornak a source oszlopában található URL-ről le kell tölteni a teljes HTML-forráskódot. Például az első sornál ez az URL:
      https://orka2.sejm.gov.pl/Debata1.nsf/118b9e577f3fceeac125746d0030d0fa/b786e1a6f47484a0c125750500453a5c?OpenDocument.


   3. HTML-elemzés és extrakció:
       * A letöltött HTML-forráskódban a releváns tartalom a <body> tagen belül található.
       * A struktúra úgy épül fel, hogy a házelnök (Marszałek) szövegrészletei sima szövegként (text node-ként) helyezkednek el, amelyeket <a> (anchor/link) tagek választanak el egymástól.
       * A házelnök beszéd-szegmensei: A tiszta szöveges részek a <a> tageken kívül, azok között találhatóak. Ezeket kell kinyerni.
       * Elválasztók: Az <a> tagek maguk a többi felszólalóra (pl. miniszterek, képviselők) mutatnak, akiknek a beszédei már külön sorokként szerepelnek a CSV-ben.


   4. Új sorok létrehozása és adatokkal való feltöltése:
       * Minden egyes kinyert házelnöki szövegrészlethez létre kell hozni egy új sort.
       * Az eredeti chair=1 sor metaadatait (év, téma, stb.) át kell másolni az új sorba.
       * A következő oszlopokat specifikusan kell kezelni:
           * text: Az újonnan létrehozott sor text oszlopába a HTML-ből kinyert, adott házelnöki szövegrészlet kerül.
           * agenda_item: Az agenda_item értékét a soron következő, már meglévő (chair=0) felszólalás sorából kell átvenni.
           * place_agenda: Ezt az oszlopot teljesen újra kell generálni. Ez egy egyszerű sorszám, amely az ülésnapon belüli sorrendet jelöli. Miután az összes új házelnöki sort beillesztettük
             a többi felszólalás közé a helyes sorrendben, ezt a sorszámot az elejétől a végéig újra kell írni (1, 2, 3, ...).


   5. Adatstruktúra újraépítése:
       * Az eredeti, egyetlen chair=1 sort el kell távolítani.
       * A helyére be kell szúrni a kinyert és új sorokba szervezett házelnöki felszólalás-részleteket, kronológiailag a már meglévő chair=0 sorok közé illesztve, pontosan úgy, ahogy a forrás
         HTML-oldalon követik egymást.

  A folyamatot minden egyedi ülésnapra (dátumra) el kell végezni a teljes Szejm_0731_1.csv fájlon.
