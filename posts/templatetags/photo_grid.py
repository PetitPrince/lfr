from django import template

register = template.Library()


@register.inclusion_tag("player/partials/_photo_grid.html")
def photo_grid(photos, size="feed"):
    """Render a Facebook-style photo grid.

    photos: queryset or list of Photo objects
    size: "feed" or "detail" (controls CSS sizing)
    """
    photo_list = list(photos) if photos else []
    count = len(photo_list)
    visible = photo_list[:3]
    extra = count - 3 if count > 3 else 0
    if count == 0:
        grid_class = ""
    elif count == 1:
        grid_class = "photo-grid--1"
    elif count == 2:
        grid_class = "photo-grid--2"
    elif count == 3:
        grid_class = "photo-grid--3"
    else:
        grid_class = "photo-grid--4plus"
    return {
        "photos": visible,
        "count": count,
        "extra": extra,
        "grid_class": grid_class,
        "size": size,
    }
