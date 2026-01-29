# Analyysi
- Käytin Claude Code-agenttia PyCharmissa.
- Jouduin ajamaan ``uv init`` projektikansiossa ennen aloittamista, sillä täysin tyhjässä projektikansiossa agentti ei jostain syystä pystynyt löytämään uv-asennustani.

## 1. Mitä tekoäly teki hyvin?

- Nopeus. Noin päivän työn saa teoriassa tehtyä tunnin parin sisään.
- Logiikka ja koodityyli ovat yllättävän hyviä, kun promptit ovat tarpeeksi yksityiskohtaisia.
  - Clauden planning mode auttoi myös tämän kanssa erittäin paljon.
- Järkevät testit generoituivat hyvin nopeasti.
- Refaktorointi (esim. moduulien siirto omiin tiedostoihinsa) onnistui myös todella hyvin.

## 2. Mitä tekoäly teki huonosti?
- Se on tottunut tätä demonstraatiota monimutkaisempien sovellusten koodaamiseen. Erityisesti projektin alkuvaiheissa piti tehdä selväksi, että tätä projektia varten en tarvitse niin paljon hienouksia.
- Jostain syystä varauksen poisto ja olemassaolon validaatio päätyi samaan funktioon.
- Sen sijaan että agentti olisi lisännyt testaamisen dependencyt uv-komentojen kautta, se alun perin editoi pyproject.tomlia suoraan, lisäten deprekoitua syntaksia.
  - Myös docker-composeen tuli myös deprekoitu version-fieldi. 
- Varausten poistamisen koodi oli alun perin hyvin rumaa.
```python
def delete_reservation(reservation_id: int) -> bool:
    """
    Delete a reservation by ID.
    Returns True if deleted, False if not found.
    """
    global reservations
    initial_length = len(reservations)
    reservations = [res for res in reservations if res.id != reservation_id]
        return len(reservations) < initial_length
```
Tämä toimi, mutta se on turhan vaikealukuista verrattuna uudempaan versioon:
```python
def delete_reservation(reservation_id: int) -> bool:
    """
    Delete a reservation by ID.
    Returns True if deleted, False if not found.
    """
    global reservations

    for i, reservation in enumerate(reservations):
        if reservation.id == reservation_id:
            reservations.pop(i)
            return True

    return False
```

Jälkimmäinen on selvästi helpompi lukea ja tarvittaessa ylläpitää jos muutoksia tarvitsisi tehdä.

- Tämä esimerkki ei ole relevantti tähän projektiin, mutta kokeilin aiemmin, miten Claude tekisi OAuth2-salasanatodennuksen FastAPI:lla. Claude ei ollut siihen kykeneväinen edes toistuvan promptaamisen ja virheiden huomautuksen jälkeen. Uskon vieläkin vahvasti, että tekoälyn kirjoittamaa koodia tulee aina valvoa tarkasti, ja erittäin tarkasti kun todennuksen jättää tekoälylle. 

## 3. Mitkä olivat tärkeimmät parannukset, jotka tein tekoälyn tuottamaan koodiin ja miksi?
Ehdottomasti tärkeimpiä olivat:
  - tuo uusi delete_reservation-funktio.
  - varauksen olemassaolon validaation ja varauksen poiston separointi.

Syy: hyvä rakenne, helppo luettavuus ja ylläpidettävyys ovat äärimmäisen tärkeitä.
- Alkuperäinen delete_reservation-funktio "säikyttää" minua hieman. Muihin ohjelmointikieliin tottuneena henkilönä kysyisin todennäköisesti tekoälyltä, mitä se blokki tarkalleen tekee. Uuden version toiminta taas on hyvin helppo ymmärtää, vaikka netti olisi katkennut.
- Olisi epäloogista että vain varauksen poistaminen toimisi jotenkin täysin eri tavalla verrattuna kaikkiin muihin endpointteihin.