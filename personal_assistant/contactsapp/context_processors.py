from .localize import text_array as translations


def get_language(request):
    language = request.GET.get('lang')
    if not language:
        language = request.session.get('language', 'en')
    request.session['language'] = language
    return language


def translations_context_processor(request):
    language = get_language(request)
    return {
        'translations': translations.get(language, translations['en']),
        'months': {
            'January': translations[language]['January'],
            'February': translations[language]['February'],
            'March': translations[language]['March'],
            'April': translations[language]['April'],
            'May': translations[language]['May'],
            'June': translations[language]['June'],
            'July': translations[language]['July'],
            'August': translations[language]['August'],
            'September': translations[language]['September'],
            'October': translations[language]['October'],
            'November': translations[language]['November'],
            'December': translations[language]['December'],
        }
    }
