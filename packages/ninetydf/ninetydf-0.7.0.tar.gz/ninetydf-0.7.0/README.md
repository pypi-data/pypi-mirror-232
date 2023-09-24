# ninetydf

90 Day Fiancé DataFrames

## Installing

To use the DataFrames, install `pandas` separately or with the extra:

```bash
pip install ninetydf[pandas]
```

Without pandas, the data can be imported as a list of dataclasses.

## Example with Data Classes

```python
from ninetydf import couples_list, seasons_list


def main():
    for couple in couples_list[:5]:
        print(couple)
    for season in seasons_list[:5]:
        print(season)


if __name__ == "__main__":
    main()

```

**Output**:

```bash
Couple(show_id='90DF', show_name='90 Day Fiancé', season=1, season_id='90DF_1', couple_name='Alan & Kirlyam', couple_id='alan_kirlyam', appearance_id='alan_kirlyam_90DF_1', person_id_x='alan_cox', person_id_y='kirlyam')
Couple(show_id='90DF', show_name='90 Day Fiancé', season=1, season_id='90DF_1', couple_name='Louis & Aya', couple_id='louis_aya', appearance_id='louis_aya_90DF_1', person_id_x='louis\xa0gattone', person_id_y='aya')
Couple(show_id='90DF', show_name='90 Day Fiancé', season=1, season_id='90DF_1', couple_name='Mike & Aziza', couple_id='mike_aziza', appearance_id='mike_aziza_90DF_1', person_id_x='mike_eloshway', person_id_y='aziza_mazhidova')
Couple(show_id='90DF', show_name='90 Day Fiancé', season=1, season_id='90DF_1', couple_name='Russ & Paola', couple_id='russ_paola', appearance_id='russ_paola_90DF_1', person_id_x='russ_mayfield', person_id_y='paola_blaze')
Couple(show_id='90DF', show_name='90 Day Fiancé', season=2, season_id='90DF_2', couple_name='Brett & Daya', couple_id='brett_daya', appearance_id='brett_daya_90DF_2', person_id_x='brett_otto', person_id_y='daya_de_arce')
Season(show_id='90DF', show_name='90 Day Fiancé', season=1, season_id='90DF_1', start_date='2014-01-12', end_date='2014-02-23')
Season(show_id='90DF', show_name='90 Day Fiancé', season=2, season_id='90DF_2', start_date='2014-10-19', end_date='2014-12-28')
Season(show_id='90DF', show_name='90 Day Fiancé', season=3, season_id='90DF_3', start_date='2015-10-11', end_date='2015-12-06')
Season(show_id='90DF', show_name='90 Day Fiancé', season=4, season_id='90DF_4', start_date='2016-08-22', end_date='2016-11-20')
Season(show_id='90DF', show_name='90 Day Fiancé', season=5, season_id='90DF_5', start_date='2017-10-08', end_date='2017-12-18')
```

## Example with Pandas

```python
from ninetydf import couples_df, seasons_df


def main():
    print(couples_df.head(10))
    print(seasons_df.head(10))


if __name__ == "__main__":
    main()

```

**Output**:

```bash
  show_id      show_name  season season_id         couple_name         couple_id            appearance_id       person_id_x      person_id_y
0    90DF  90 Day Fiancé       1    90DF_1      Alan & Kirlyam      alan_kirlyam      alan_kirlyam_90DF_1          alan_cox          kirlyam
1    90DF  90 Day Fiancé       1    90DF_1         Louis & Aya         louis_aya         louis_aya_90DF_1     louis gattone              aya
2    90DF  90 Day Fiancé       1    90DF_1        Mike & Aziza        mike_aziza        mike_aziza_90DF_1     mike_eloshway  aziza_mazhidova
3    90DF  90 Day Fiancé       1    90DF_1        Russ & Paola        russ_paola        russ_paola_90DF_1     russ_mayfield      paola_blaze
4    90DF  90 Day Fiancé       2    90DF_2        Brett & Daya        brett_daya        brett_daya_90DF_2        brett_otto     daya_de_arce
5    90DF  90 Day Fiancé       2    90DF_2     Chelsea & Yamir     chelsea_yamir     chelsea_yamir_90DF_2     chelsea_macek   yamir_castillo
6    90DF  90 Day Fiancé       2    90DF_2  Danielle & Mohamed  danielle_mohamed  danielle_mohamed_90DF_2  danielle_mullins    mohamed_jbali
7    90DF  90 Day Fiancé       2    90DF_2         Danny & Amy         danny_amy         danny_amy_90DF_2   danny_frishmuth              amy
8    90DF  90 Day Fiancé       2    90DF_2      Jason & Cássia      jason_cassia      jason_cassia_90DF_2       jason_hitch   cassia_tavares
9    90DF  90 Day Fiancé       2    90DF_2     Justin & Evelyn     justin_evelyn     justin_evelyn_90DF_2      justin_halas           evelyn
  show_id                          show_name  season season_id  start_date    end_date
0    90DF                      90 Day Fiancé       1    90DF_1  2014-01-12  2014-02-23
1    90DF                      90 Day Fiancé       2    90DF_2  2014-10-19  2014-12-28
2    90DF                      90 Day Fiancé       3    90DF_3  2015-10-11  2015-12-06
3    90DF                      90 Day Fiancé       4    90DF_4  2016-08-22  2016-11-20
4    90DF                      90 Day Fiancé       5    90DF_5  2017-10-08  2017-12-18
5    90DF                      90 Day Fiancé       6    90DF_6  2018-10-21  2019-01-13
6    90DF                      90 Day Fiancé       7    90DF_7  2019-11-03  2020-02-17
7    90DF                      90 Day Fiancé       8    90DF_8  2020-12-06  2021-02-21
8    90DF                      90 Day Fiancé       9    90DF_9  2022-04-17  2022-08-21
9     B90  90 Day Fiancé: Before the 90 Days       1     B90_1  2017-08-06  2017-10-30
```

## Disclaimer

The data provided in this repository related to "90 Day Fiancé" (the "Data")
is intended for educational and research purposes only. The Data might be
copyrighted and/or subject to other legal protections.

Users agree to the following terms when using the Data:

1. Not to use the Data for commercial purposes.
2. To use the Data in a fair and ethical manner, respecting the rights of the original creators and copyright holders.
3. That they are solely responsible for any legal implications or violations arising from their use of the Data.
4. Not to distribute or reproduce the Data without explicit permission from the original copyright holders.
5. To provide proper attribution when referencing the Data in any publications or outputs.

**This repository and its maintainers are not affiliated with, endorsed by,
or sponsored by the creators or copyright holders of "90 Day Fiancé".**
Any use of the Data is at the user's own risk, and the maintainers
of this repository disclaim any and all liability related thereto.
