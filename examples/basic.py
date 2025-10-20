import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pytionalization import i18n


def main():
    i18n_instance = i18n.I18n(
        sources={
            "pl": str(Path(__file__).parent / "pl.json"),
            "en": str(Path(__file__).parent / "en.json"),
        },
        default_locale="pl",
        fallback_locale="en",
    )

    print(i18n_instance.t("hello"))
    print(i18n_instance.t("greet", user={"name": "Michael"}))
    print(i18n_instance.t("nested.title", post={"title": "New entry"}))
    print(i18n_instance.t("missing_var", does={"not": {"exist": "value"}}))


if __name__ == "__main__":
    main()
