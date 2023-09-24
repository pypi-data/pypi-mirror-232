import unicodedata
from dataclasses import asdict

from ninetydf.models import Couple, Season

try:
    from ninetydf import couples_df, seasons_df

    couples = [Couple(*row) for row in couples_df.values]

    seasons_df["end_date"] = seasons_df["end_date"].fillna("")
    seasons = [Season(*row) for row in seasons_df.values]

except ImportError:
    from ninetydf import couples_list, seasons_list

    couples = couples_list
    seasons = seasons_list

SHOW_IDS = {
    "90 Day Fiancé": "90DF",
    "90 Day Fiancé: Before the 90 Days": "B90",
    "90 Day Fiancé: The Other Way": "TOW",
    "90 Day Fiancé: Happily Ever After?": "HEA",
    "90 Day: The Last Resort": "TLR",
}


def normalize_string(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def test_couple_values():
    assert len(couples) == 177

    missing_values = sum(
        1
        for couple in couples
        if any(value is None for value in asdict(couple).values())
    )
    assert missing_values == 0

    appearance_ids = [couple.appearance_id for couple in couples]
    assert len(appearance_ids) == len(set(appearance_ids)), "not unique"

    for couple in couples:
        assert couple.appearance_id == f"{couple.couple_id}_{couple.season_id}"
        assert couple.show_id == SHOW_IDS[couple.show_name]

        couple_id_parts = couple.couple_name.split(" & ")
        assert len(couple_id_parts) == 2

        for id_val in [couple.person_id_x, couple.person_id_y]:
            assert id_val == str.lower(normalize_string(id_val))
            assert len(id_val.split(" ")) == 1

        assert couple.couple_id == str.lower(
            normalize_string(couple_id_parts[0] + "_" + couple_id_parts[1])
        )

        for value in asdict(couple).values():
            if isinstance(value, str):
                assert value.strip() == value, "trailing white space"


def test_season_values():
    assert len(seasons) == 28

    missing_values = sum(
        1 for season in seasons if any(not value for value in asdict(season).values())
    )

    assert missing_values == 2, "current seasons do not have end dates"

    season_ids = [season.season_id for season in seasons]
    assert len(season_ids) == len(set(season_ids)), "not unique"

    for season in seasons:
        assert season.show_id == SHOW_IDS[season.show_name]
        assert season.season_id == f"{season.show_id}_{season.season}"

        for value in asdict(season).values():
            if isinstance(value, str):
                assert value.strip() == value, "trailing white space"
