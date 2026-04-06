import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _is_valid_hex(value):
    return bool(value and _HEX_RE.match(value))


def _darken(hex_color, factor=0.7):
    """Darken a hex color by a factor (0-1)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color, factor=0.3):
    """Lighten a hex color by mixing with white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = r + int((255 - r) * factor)
    g = g + int((255 - g) * factor)
    b = b + int((255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


@register.simple_tag
def theme_vars(run):
    """Output inline CSS custom property overrides for per-run theming.

    Validates hex format to prevent XSS via organizer-supplied color values.
    """
    if not run:
        return ""
    overrides = []
    if _is_valid_hex(run.theme_accent):
        overrides.append(f"--gold: {run.theme_accent}")
        overrides.append(f"--gold-muted: {_lighten(run.theme_accent, 0.3)}")
        overrides.append(f"--gold-dark: {_darken(run.theme_accent, 0.6)}")
    if _is_valid_hex(run.theme_nav_bg):
        overrides.append(f"--brown-dark: {run.theme_nav_bg}")
        overrides.append(f"--brown-mid: {_lighten(run.theme_nav_bg, 0.15)}")
    if _is_valid_hex(run.theme_page_bg):
        overrides.append(f"--parchment-light: {run.theme_page_bg}")
        overrides.append(f"--parchment-dark: {_darken(run.theme_page_bg, 0.9)}")
    if _is_valid_hex(run.theme_text):
        overrides.append(f"--ink: {run.theme_text}")
    if not overrides:
        return ""
    css = "; ".join(overrides)
    return mark_safe(f'<style>:root {{ {css} }}</style>')
