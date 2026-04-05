import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "p", "br", "strong", "em", "a", "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "code", "pre", "hr",
}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}


@register.filter(name="markdown")
def render_markdown(value):
    if not value:
        return ""
    html = markdown.markdown(value, extensions=["nl2br", "sane_lists"])
    clean = nh3.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return mark_safe(clean)
