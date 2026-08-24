from flights import airports


def test_airport_search_matches_codes_cities_and_names():
    assert any(entry["code"] == "YYZ" for entry in airports.search("yyz"))
    assert any(entry["code"] == "SFO" for entry in airports.search("san francisco"))
    assert any(entry["code"] == "YTO" for entry in airports.search("toronto"))
    assert any(entry["code"] == "SJC" for entry in airports.search("mineta"))


def test_airport_search_prefers_city_codes_for_metro_queries():
    assert airports.search("toronto")[0]["code"] == "YTO"


def test_airport_search_ignores_very_short_queries():
    assert airports.search("t") == []


def test_airport_lookup_is_case_insensitive_and_reports_unknown_codes():
    assert airports.find("yyz")["city"] == "Toronto"
    assert airports.find("ZZZ") is None
    assert airports.is_known("SFO") is True


def test_airport_label_reads_naturally():
    assert airports.label("YYZ") == "Toronto (YYZ)"
    assert airports.label("YTO") == "Toronto"
    assert airports.label("ZZZ") == "ZZZ"


def test_nearby_finds_a_real_alternate_airport_within_range():
    codes = [entry["code"] for entry in airports.nearby("YYZ")]
    assert codes == ["YTZ"]


def test_nearby_matches_the_spec_named_bay_area_alternates():
    codes = [entry["code"] for entry in airports.nearby("SFO")]
    assert codes == ["OAK"]


def test_nearby_respects_a_wider_limit():
    codes = [entry["code"] for entry in airports.nearby("YYZ", limit=2)]
    assert codes == ["YTZ", "YHM"]


def test_nearby_excludes_airports_outside_the_radius():
    assert airports.nearby("YYZ", radius_km=5) == []


def test_nearby_returns_nothing_for_a_metro_city_code():
    assert airports.nearby("YTO") == []


def test_nearby_returns_nothing_for_an_unknown_code():
    assert airports.nearby("ZZZ") == []
