## AttestCreator
### Over
Jeugdorganisaties zijn vanaf inkomstenjaar 2022 verplicht zijn om [fiscale attesten](https://financien.belgium.be/nl/E-services/Belcotaxonweb/technische-documentatie) 
voor de terugbetaling van kinderopvang te voorzien. Niemand heeft zin in veel extra administratief werk,
daarom deze tool om de attesten makkelijker te genereren en door te sturen. AttestCreator genereert de attesten 
op basis van een excelsheet met ledendata en opgegeven info over het fiscale jaar, waarna alle nodige pdf's worden 
aangemaakt (en doorgestuurd indien gewenst). Na aanvullingen door de ouder/voogd kan het attest ondertekend worden.

De attesten moeten ook aangegeven worden bij FOD Financiën, waarvoor een KBO-nummer nodig is.
Feitelijke verenigingen moeten hiervoor [een aanvraag doen](https://financien.belgium.be/nl/E-services/Belcotaxonweb/hoe-toegang-krijgen-tot-belcotax-on-web#q3).
Daarna kan met behulp van [BowConverter](https://financien.belgium.be/sites/default/files/downloads/161-BowConvert86-2022.zip)
de data worden omgezet in een XML en de aanvraag gedaan worden. Om de teruggestuurde pdf's te vertalen naar het formaat 
gebruikt in BowConverter zal een aparte tool voorzien worden tegen het einde van dit fiscale jaar.

### Configuratie
Download de laatste release [hier](https://github.com/rokeppen/attestCreator/releases/download/v2/v2.zip) 
(mogelijks volgen meldingen over onveilige bestanden) en doorloop de installatie-wizard (voorlopig enkel via Windows). 
Vul vervolgens de gegevens van de vereniging aan in de volgende bestanden:
#### ```lijst.xlsx```
De ledenlijst met de opvangperiodes van het kind bij de vereniging. Deze data wordt op de volgende manier gefilterd:
- Enkel kinderen waarvoor een naam, voornaam en geboortedatum beschikbaar is, worden behouden.
- Voor kinderen die meerdere keren voorkomen, worden alle periodes samen gegooid. Je hoeft dus per nieuwe opvangperiode 
niet op zoek te gaan of het kind al aanwezig is. Ook de volgorde maakt niet uit: als bijvoorbeeld enkel periode 3 en 4 worden aangevuld, 
zullen die toch vanaf periode 1 ingevuld worden in het attest.
- Kinderen waarvoor geen enkele periode start voor hun veertiende verjaardag, worden gefilterd. 
Je kan dus de volledige aanwezigheidslijsten van het kamp/weekend aanvullen, ongeacht hun leeftijd.
- Overlapt een nieuwe opvangperiode van een kind met een vorige, dan wordt enkel de eerste behouden.
- Het opgegeven e-mailadres is het contactadres van de ouders waar het attest naartoe zal gestuurd worden. 
Indien een kind meerdere keren voorkomt met verschillende e-mailadressen, wordt enkel het eerste behouden.
- Enkel de tab "Gefilterd" wordt gebruikt (de extra tab dient ter ondersteuning van een latere versie, die de attesten zal ondertekenen).
#### ```instance.ini```
Data van de vereniging, ingevuld in vak I van het attest. In de release staat de voorbeelddata 
voor Scouts & Gidsen Lebbeke aangevuld, vraag zeker de correcte gegevens op bij de gemeente.
#### ```smtp.ini```
Indien de attesten automatisch dienen doorgestuurd te worden, moet hier de mailconfiguratie aangevuld worden.
Er wordt gebruik gemaakt van een uitgaande SMTP-server. Voor Gmail-gebruikers met tweestapsverificatie is een 
[app-paswoord](https://support.google.com/accounts/answer/185833) nodig, bij de meeste andere providers werkt de gebruikelijke login.
#### ```mailTemplate.html```
Dit is de standaard opmaak van de mail die wordt gestuurd naar de ouders, waarbij de naam en de gegevens van de vereniging
worden aangevuld in de velden tussen accolades:
- {0}: De voornaam van het kind
- {1}: Het fiscale jaar
- {2}: Het reply-to-mailadres opgegeven in ```smtp.ini```
- {3}: De naam van de vereniging opgegeven in ```instance.ini```

Wijzig dit template om de inhoud van deze mails te veranderen.

### Gebruik
#### GUI
Start de tool. Het volgende venster komt dan tevoorschijn:

![tool](app.png)

Het aantal rijen in de excel die aan de voorwaarden voldoet wordt weergegeven. Hier kan ook het fiscale jaar, ingevuld in vak I 
en in de titel van het attest, aangevuld worden, samen met het gebruikte prijsplafond voor 1 dag opvang van dat jaar. 
Het huidige jaar en € 14,4 (fiscaal jaar 2022) worden standaard ingevuld. De ingevulde attesten komen terecht in een mapje "out" 
op dezelfde plaats als de excel. Wanneer het vinkje "verstuur via mail" wordt gebruikt en de e-mailconfiguratie is correct,
worden de attesten gemaild naar de adressen opgegeven in excel (oor kinderen waarvoor in geen enkele rij een e-mailadres werd aangevuld, 
wordt enkel de pdf-gegenereerd). Bij succes wordt een popup weergegeven, die bij het wegklikken de tool afsluit.

#### CLI
De basisfunctionaliteit is beschikbaar via het python-script ```cli.py``` met de volgende syntax:
```
python cli.py -p <path-to-pdf> -l <path-to-excel> -y <fiscal-year> -r <max-reimbursement-rate>
```

### Aanpassingen
Deze tool is aan de ene kant geschreven om mijn Python wat af te stoffen en aan de andere kant om onze scoutsgroep later werk te besparen.
Noch de code, noch de info hier opgelijst zullen vrij zijn van fouten, dus voel je vrij om aanpassingen/verbeteringen te doen :)
> Never spend 6 minutes doing something by hand when you can spend 6 hours failing to automate it.
