from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(is_safe=True)
def get_responsive_image(image):

    fields = {
        'id': image.id,
        'data-image-id': "data-image-id='" + str(image.id) + "'",
        'xs': "data-bttrlazyloading-xs-src='" + image.image_xs.url + "'",
        'sm': "data-bttrlazyloading-sm-src='" + image.image_sm.url + "'",
        'md': "data-bttrlazyloading-md-src='" + image.image_md.url + "'",
        'lg': "data-bttrlazyloading-lg-src='" + image.image_lg.url + "'",
        'transition': "data-bttrlazyloading-transition='rotatedIn'"
    }

    image_tag = '<img id="image-{id}" class="bttrlazyloading {xs} {sm} {md} {lg} {transition} {data-image-id}" />' \
        .format(**fields)

    return mark_safe(image_tag)
