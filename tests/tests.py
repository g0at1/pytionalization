import json
import pytest
from pathlib import Path
from pytionalization import i18n as mod


PL_DICT = {
    "hello": "Cześć",
    "greet": "Cześć, {{user.name}}!",
    "greet_fmt": "Cześć, {user}!",
    "nested": {
        "title": "Tytuł: {{post.title}}",
        "count": "Liczba: {count}",
    },
    "list_val": [1, 2, 3],
    "obj_val": {"a": 1, "b": "x"},
    "composed": "Witaj {{user.first}} {user.last}",
    "missing_var": "Brak {{does.not.exist}} oraz {also_missing}",
}

EN_DICT = {
    "hello": "Hello",
    "greet": "Hello, {{user.name}}!",
    "greet_fmt": "Hello, {user}!",
    "nested": {
        "title": "Title: {{post.title}}",
        "count": "Count: {count}",
    },
}


@pytest.fixture
def tmp_locale_files(tmp_path: Path):
    pl = tmp_path / "pl.json"
    en = tmp_path / "en.json"
    pl.write_text(json.dumps(PL_DICT, ensure_ascii=False), encoding="utf-8")
    en.write_text(json.dumps(EN_DICT, ensure_ascii=False), encoding="utf-8")
    return {"pl": str(pl), "en": str(en)}


@pytest.fixture
def i18n(tmp_locale_files):
    return mod.I18n(
        sources={"pl": tmp_locale_files["pl"], "en": tmp_locale_files["en"]},
        default_locale="pl",
        fallback_locale="en",
    )


def test_loads_all_locales(i18n: mod.I18n):
    assert i18n.get_locale() == "pl"
    assert "pl" in i18n._bundles and "en" in i18n._bundles
    assert i18n._bundles["pl"]["hello"] == "Cześć"
    assert i18n._bundles["en"]["hello"] == "Hello"


def test_missing_file_raises(tmp_path: Path):
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError):
        mod.I18n(sources={"pl": str(missing)}, default_locale="pl")


def test_invalid_json_raises(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{invalid: json}", encoding="utf-8")
    with pytest.raises(ValueError):
        mod.I18n(sources={"pl": str(bad)}, default_locale="pl")


def test_set_locale_ok(i18n: mod.I18n):
    i18n.set_locale("en")
    assert i18n.get_locale() == "en"
    assert i18n.t("hello") == "Hello"


def test_set_locale_unknown_raises(i18n: mod.I18n):
    with pytest.raises(ValueError):
        i18n.set_locale("de")


def test_basic_translation_primary(i18n: mod.I18n):
    assert i18n.t("hello") == "Cześć"


def test_fallback_to_en_when_missing_in_pl(i18n: mod.I18n):
    del i18n._bundles["pl"]["greet_fmt"]
    assert i18n.t("greet_fmt", user="Rafał") == "Hello, Rafał!"


def test_no_fallback_returns_default_or_key(tmp_locale_files):
    i18n = mod.I18n(
        sources={"pl": tmp_locale_files["pl"]},
        default_locale="pl",
        fallback_locale=None,
    )
    assert i18n.t("not.exists", default="domyślne") == "domyślne"
    assert i18n.t("not.exists")
