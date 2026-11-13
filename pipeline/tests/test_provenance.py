import pandas as pd
import pytest

from worldatlas.provenance import ProvenanceError, validate_observations

KNOWN = {"USA", "CHN"}


def obs(**over):
    row = {"iso3": "USA", "indicator": "pop", "year": 2024, "value": 1.0, "unit": "persons", "source_id": "wb_wdi", "proxy": False}
    row.update(over)
    return pd.DataFrame([row])


def test_valid_rows_pass_and_are_canonical():
    df = validate_observations(pd.concat([obs(iso3="CHN"), obs()]), KNOWN)
    assert list(df.iso3) == ["CHN", "USA"]
    assert df.year.dtype.kind == "i"


@pytest.mark.parametrize("bad, msg", [
    ({"source_id": "made_up"}, "unregistered source"),
    ({"iso3": "XXX"}, "unknown iso3"),
    ({"unit": None}, "null provenance"),
])
def test_rejects_untraceable_rows(bad, msg):
    with pytest.raises(ProvenanceError, match=msg):
        validate_observations(obs(**bad), KNOWN)


def test_rejects_missing_columns():
    with pytest.raises(ProvenanceError, match="missing columns"):
        validate_observations(obs().drop(columns="source_id"), KNOWN)


def test_rejects_duplicates():
    with pytest.raises(ProvenanceError, match="duplicate"):
        validate_observations(pd.concat([obs(), obs()]), KNOWN)


def test_null_value_is_allowed_but_not_null_provenance():
    assert len(validate_observations(obs(value=None), KNOWN)) == 1
