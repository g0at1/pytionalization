# Pytionalization

A minimal JSON-based internationalization (i18n) helper for Python.

Supports nested keys, dot-notation access, placeholder interpolation, and automatic fallback between languages.

---

## 🚀 Installation

### Using pip install
```bash
pip install git+https://github.com/g0at1/pytionalization.git 
```
---

## 🧩 Usage

```python
from pytionalization import I18n, configure_i18n, translate

# Option 1: Create instance manually
i18n = I18n(
    sources={
        'pl': 'pl.json',
        'en': 'en.json',
    },
    default_locale='pl',
    fallback_locale='en',
)

print(i18n.t('PASSWORD-INPUT.FORGOT-PASSWORD-LINK'))  # → Zresetuj hasło
print(i18n.t(
    'CURRENCY-CONVERTER.CONVERT-TEXT',
    convertedValue=123.45,
    rate=4.2,
    exchangeDate='2025-10-20'
))

# Option 2: Configure global instance
configure_i18n(pl_path='pl.json', en_path='en.json')
translate('HEADER.USER.LOGOUT', locale='pl')
```

---

## 🧠 Features

✅ Loads from `pl.json` and `en.json` (or any mapping)

✅ Dot-notation key access (`DATA-FORM.VALIDATIONS.NAME-REQUIRED`)

✅ Safe fallback locale (e.g., fallback to English if missing in Polish)

✅ Interpolation for both `{{var}}` and `{var}` placehold
