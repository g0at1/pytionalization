from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

__all__ = ["I18n", "translate"]

_HANDLEBARS_RE = re.compile(r"{{\s*([a-zA-Z0-9_\.]+)\s*}}")


@dataclass
class I18n:
    sources: Mapping[str, str]
    default_locale: str = "pl"
    fallback_locale: Optional[str] = "en"
    _bundles: Dict[str, Dict[str, Any]] = field(default_factory=dict, init=False)
    _locale: str = field(default="pl", init=False)

    def __post_init__(self) -> None:
        if self.default_locale not in self.sources:
            self.default_locale = next(iter(self.sources.keys()))
        self._locale = self.default_locale
        for loc, path in self.sources.items():
            self._bundles[loc] = self._load_json(path)

    def set_locale(self, locale: str) -> None:
        if locale not in self.sources:
            raise ValueError(f"Unknown locale '{locale}'. Known: {list(self.sources)}")
        self._locale = locale

    def get_locale(self) -> str:
        return self._locale

    def t(self, key: str, *, locale: Optional[str] = None, default: Optional[str] = None, **vars: Any) -> str:
        """Translate a key using the active or provided locale.

        Args:
            key: Dot-notation key path.
            locale: Optional override locale. If omitted, uses current instance locale.
            default: Optional default text if key is missing in both primary and fallback.
            **vars: Variables for interpolation. Both `{{var}}` and `{var}` styles are supported.
        """
        loc = locale or self._locale
        text = self._lookup(loc, key)
        if text is None and self.fallback_locale and self.fallback_locale != loc:
            text = self._lookup(self.fallback_locale, key)
        if text is None:
            text = default if default is not None else key  # return key as a last resort
        if not isinstance(text, str):
            text = json.dumps(text, ensure_ascii=False)
        return self._interpolate(text, vars)

    def _load_json(self, path: str) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Translation file not found: {p}")
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {p}: {e}") from e

    def _lookup(self, locale: str, key: str) -> Optional[Any]:
        node: Any = self._bundles.get(locale)
        if node is None:
            return None
        for part in key.split('.'):
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node

    def _interpolate(self, template: str, vars: Mapping[str, Any]) -> str:
        def repl(m: re.Match[str]) -> str:
            k = m.group(1)
            v = self._get_by_path(vars, k)
            return str(v) if v is not None else m.group(0)

        s = _HANDLEBARS_RE.sub(repl, template)
        try:
            s = s.format(**{k: v for k, v in vars.items()})
        except Exception:
            pass
        return s

    @staticmethod
    def _get_by_path(mapping: Mapping[str, Any], path: str) -> Optional[Any]:
        cur: Any = mapping
        for part in path.split('.'):
            if isinstance(cur, Mapping) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

_default_i18n: Optional[I18n] = None


def configure_i18n(*, pl_path: str, en_path: str, default_locale: str = "pl", fallback_locale: str = "en") -> None:
    """Configure a process-wide i18n instance.

    Example:
        configure_i18n(pl_path="/path/pl.json", en_path="/path/en.json")
    """
    global _default_i18n
    _default_i18n = I18n(
        sources={"pl": pl_path, "en": en_path},
        default_locale=default_locale,
        fallback_locale=fallback_locale,
    )


def translate(key: str, *, locale: Optional[str] = None, default: Optional[str] = None, **vars: Any) -> str:
    """Translate using the global instance configured via configure_i18n()."""
    if _default_i18n is None:
        raise RuntimeError("i18n is not configured. Call configure_i18n(pl_path=..., en_path=...) first.")
    return _default_i18n.t(key, locale=locale, default=default, **vars)
