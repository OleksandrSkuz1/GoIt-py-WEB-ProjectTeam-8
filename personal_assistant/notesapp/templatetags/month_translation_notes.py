from django import template

register = template.Library()


@register.filter(name='translate_month')
def translate_month(value, months):
    if not value:
        return value

    month_translation = {
        'January': months['January'],
        'February': months['February'],
        'March': months['March'],
        'April': months['April'],
        'May': months['May'],
        'June': months['June'],
        'July': months['July'],
        'August': months['August'],
        'September': months['September'],
        'October': months['October'],
        'November': months['November'],
        'December': months['December'],
    }

    for en, translated in month_translation.items():
        value = value.replace(en, translated)

    return value
