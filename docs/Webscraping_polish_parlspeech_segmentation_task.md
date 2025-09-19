**Webscraping task: segmentation of the Polish parliament's speaker's
speeches**

**Your task is to adjust the data for the provided CSV file based on the
description below.**

Our data for the 1991-2011 Polish parliamentary speeches lacks proper
segmentation regarding the parliament's speaker (if the chair variable's
value is 1 within the dataset). At the beginning of a session, the very
first speech of the speaker contains all of his/her speeches of that
session, and only the other actors' speeches are included thereafter
separately. An example:

2010.08.06
([[https://orka2.sejm.gov.pl/Debata6.nsf/7075e4662b58d9b1c125737f0039d549/87e2b23e4b30becfc125777a002a87f0?OpenDocument]{.underline}](https://orka2.sejm.gov.pl/Debata6.nsf/7075e4662b58d9b1c125737f0039d549/87e2b23e4b30becfc125777a002a87f0?OpenDocument))

![](media/image2.png){width="6.915172790901138in"
height="2.838179133858268in"}

```
see also ([[first100-rows-of-csv.csv]{.underline}](./first100rows-of-csv.csv))
```

The speech by the Speaker (Marszalek in Polish) is in the first row
(where the value of chair is 1), followed by other speeches in the next
9 rows (where the value of chair is 0). Out of this, 8 are delivered by
the President of the Republic Bronisław Komorowski, and 1 is delivered
by a secretary (Beata Bublewicz). By clicking the above link, we can see
the Speaker's speech (and some information on the session day in general
in brackets before the name or title of the speaker, which should be
omitted from the corpus):

![](media/image1.png){width="6.299660979877515in" height="2.875in"}

```text of image1.png
6 kadencja, Zgromadzenie Narodowe (06-08-2010)
(Poczatek posiedzenia o godz. 10 min 01) (Posiedzeniu przewodniczy marszatek Sejmu Grzegorz Schetyna) (Marszatek Senatu Bogdan Borusewicz zajmuje miejsce przy stole prezydialnym) (Na sale wchodzi prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski z matzonka) (Zebrani wstaja, burzliwe oklaski) Marszatek: Otwieram obrady Zgromadzenia Narodowego zwofanego na podstawie art. 114 ust. 1 w zwiazku z art. 130 Konstytucji Rzeczypospolitej Polskiej w celu zioZenia przysiegi przez nowo wybranego prezydenta Rzeczypospolitej Polskiej. (Marszatek trzykrotnie uderza laska marszatkowska) (Orkiestra gra hymn paristwowy, zebrani wstaja, Spiewaja hymn) 'Witam pana prezydenta Bronistawa Komorowskiego wraz z maizonka. (Oklaski) 'Witam pana premiera Donalda Tuska wraz z czionkami rzadu. (Oklaski) Witam przewodniczacego Parlamentu Europejskiego pana Jerzego Buzka. (Oklaski) Witam postow i senatorow, czionkow Zgromadzenia Narodowego. (Oklaski) Witam bytych prezydentow pana Lecha Watese wraz z matzonka oraz pana Aleksandra Kwasniewskiego. (Oklaski) Witam bytych marszatkow Sejmu i Senatu oraz bylych premierow. (Oklaski) Witam korpus dyplomatyczny, przedstawicieli wszystkich wyznarn i Kosciotow w Polsce. (Oklaski) Witam czcigodnych gosci, ktorzy przybyli na uroczystos¢ zaprzysiezenia. (Oklaski) Na sekretarzy Zgromadzenia powotuje pania poset Beate Bublewicz i pana senatora Andrzeja Szewinskiego. Protokot prowadzic bedzie pani poset Beata Bublewicz. (Oklaski)
```

Further down below, we can find the other speeches with hyperlinks
containing the name and the title of the speaker:

![](media/image5.png){width="3.9806539807524057in"
height="6.437847769028871in"}

```text of image5.png
Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszatek: Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszatek: Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszalek:
Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszalek: Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszatek: ...a dobro Ojczyzny oraz pomysinosSc obywateli... Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszatek: Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
```

![](media/image3.png){width="6.912649825021872in"
height="2.875346675415573in"}

```text of image3.png
Marszalek: Stwierdzam, ze prezydent Rzeczypospolitej Polskiej pan Bronistaw Komorowski zioZyt wobec Zgromadzenia Narodowego przysiege przewidziana w art. 130 Konstytucji Rzeczypospolitej Polskiej. Wierzymy, Ze to bedzie prezydentura faczenia, a nie dzielenia. Wierzymy, chcemy dobrej wspdipracy, | taka dekiarujemy, miedzy panem prezydentem a Sejmem, Senatem | polskim rzadem. Wierzymy, 2e bedziemy z pana dumni. Niech pana Bog prowadzi. (Burziiwe oklaski) Prosze prezydenta Rzeczypospoltej Polskie] pana Bronistawa Komorowskiego o wygioszenie oredzia. (Oklaski)
Prezydent Rzeczypospolitej Polskiej Bronistaw Komorowski
Marszalek:
Dziekuje panu prezydentowi
Prosze sekretarza Zgromadzenia Narodowego pania pose! Beate Bublewicz o odczytanie protokolu Zgromadzenia Narodowego zwolanego w celu zloZenia przysiegi przez nowo wybranego prezydenta Rzeczypospolitej Polskie. Sekretarz Posel Beata Bublewicz
Marszalek: Dzigkuje. pani posel. Czy kto$ z czlonkdw Zgromadzenia Narodowego wnosi zastrzezenia do protokolu? Nie slysze. Dzigkuje wszystkim obecnym i informuje, Ze o godz. 12 w archikatedrze $w. Jana zostanie odprawiona msza $wieta w intencji ojczyzny i prezydenta Rzeczypospoiitej. Zamykam obrady Zgromadzenia Narodowego zwotanego w celu ZioZenia przysiegl przez nowo wybranego prezydenta Rzeczypospolite] Polskie). (Zebrani wstaja, dlugotrwaie oklaski) (Marszatek trzykrotnie uderza laska marszakowska) (Koniec posiedzenia o godz. 10 min 37)
```

The further parts of the speaker\'s speech are among the hyperlinked
text lines. The links themselves point to speeches that already exist in
our data and can be found after the chair\'s speech on each session day.

The task is to split the Speaker's speech into the parts between the
hyperlink texts and create new rows within the dataset for them between
the other speeches on the right places. The metadata of the original row
of the chair's speeches should be used, with the exception of the
following:

-   The "text" should have the split text segment

-   agenda_item: should include the next row's agenda item

-   place_agenda: a running number by session, this variable needs to be
    recreated; each row's value will change based on the new order after
    the segmentation

Place the new, segmented speeches between the already existing rows of
the other actors' speeches where they occur within the given session
day..

This is how the segmentation looks in the page's source:

![](media/image4.png){width="6.843518153980752in"
height="3.3482338145231845in"}

```html (text of image4.png)
<P> Prosze pana prezydenta o powtarzanie za mng roty przysiegi.</P>
<P> "Obejmujac z woli Narodu urzad Prezydenta Rzeczypospolitej Polskiej...</P> 
<P><A NAME="001"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/13E17D4D">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...uroczyscie przysiegam...</P>
<P><A NAME="002"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/57CDDC4E">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...ze dochowam wiernosci postanowieniom Konstytucji...</P>
<P><A NAME="003"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/1BBA3B4F">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...bede strzegl niezlomnie godnosci Narodu...</P>
<BR>
<P><A NAME="004"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/5FA69A50" >Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...niepodlegtosci i bezpieczeristwa Parstwa...</P>
<P><A NAME="005"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/2392F951">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...a dobro Ojczyzny oraz pomyslnos¢ obywateli...</P>
<P><A NAME="006"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/677F5852">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> ...beda dla mnie zawsze najwyzszym nakazem.</P>
<P><A NAME="007"></A><B><FONT SIZE="+1"><A HREF="/Debata6.nsf/main/2B6BB753">Prezydent Rzeczypospolitej Polskiej Bronislaw Komorowski</A></FONT></B></P>
<BR>
<P><B><FONT SIZE="+1">Marszalek:</FONT></B></P>
<P> Stwierdzam, Ze prezydent Rzeczypospolitej Polskiej pan Bronistaw Komorowski zYozyl wobec Zgromadzenia Narodowego przysiege przewidziang w art. 130
Konstytucji Rzeczypospolitej Polskiej.</P>
<P> Szanowny Panie Prezydencie! Szanowni Paristwo! Bylismy swiadkami zloZenia
przez pana prezydenta przysiegi wobec narodu polskiego. Z ta chwila stal sie
pan przedstawicielem Najjasniejszej Rzeczypospolitej Polskiej i jej
obywateli.</P>
```

We can see where the text is between which specific links, which are
already included in the database in the following rows.

**Webscraping task: segmentation of the Polish parliament’s speaker’s
speeches**

**Your task is to adjust the data for the provided CSV file based on the
description below.**

Our data for the 1991-2011 Polish parliamentary speeches lacks proper
segmentation regarding the parliament’s speaker (if the chair variable’s
value is 1 within the dataset). At the beginning of a session, the very
first speech of the speaker contains all of his/her speeches of that
session, and only the other actors’ speeches are included thereafter
separately. An example:

2010.08.06
([<u>https://orka2.sejm.gov.pl/Debata6.nsf/7075e4662b58d9b1c125737f0039d549/87e2b23e4b30becfc125777a002a87f0?OpenDocument</u>](https://orka2.sejm.gov.pl/Debata6.nsf/7075e4662b58d9b1c125737f0039d549/87e2b23e4b30becfc125777a002a87f0?OpenDocument))

<img src="media/image2.png" style="width:6.91517in;height:2.83818in" />

The speech by the Speaker (Marszalek in Polish) is in the first row
(where the value of chair is 1), followed by other speeches in the next
9 rows (where the value of chair is 0). Out of this, 8 are delivered by
the President of the Republic Bronisław Komorowski, and 1 is delivered
by a secretary (Beata Bublewicz). By clicking the above link, we can see
the Speaker’s speech (and some information on the session day in general
in brackets before the name or title of the speaker, which should be
omitted from the corpus):

<img src="media/image1.png" style="width:6.29966in;height:2.875in" />

Further down below, we can find the other speeches with hyperlinks
containing the name and the title of the speaker:

<img src="media/image5.png" style="width:3.98065in;height:6.43785in" />

<img src="media/image3.png" style="width:6.91265in;height:2.87535in" />

The further parts of the speaker's speech are among the hyperlinked text
lines. The links themselves point to speeches that already exist in our
data and can be found after the chair's speech on each session day.

The task is to split the Speaker’s speech into the parts between the
hyperlink texts and create new rows within the dataset for them between
the other speeches on the right places. The metadata of the original row
of the chair’s speeches should be used, with the exception of the
following:

- The “text” should have the split text segment

- agenda_item: should include the next row’s agenda item

- place_agenda: a running number by session, this variable needs to be
  recreated; each row’s value will change based on the new order after
  the segmentation

Place the new, segmented speeches between the already existing rows of
the other actors’ speeches where they occur within the given session
day..

This is how the segmentation looks in the page’s source:

<img src="media/image4.png" style="width:6.84352in;height:3.34823in" />

We can see where the text is between which specific links, which are
already included in the database in the following rows.
