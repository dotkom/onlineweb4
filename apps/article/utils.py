from filebrowser.settings import VERSIONS


MONTH_STRINGS = {
    '1': u'Januar',
    '2': u'Februar',
    '3': u'Mars',
    '4': u'April',
    '5': u'Mai',
    '6': u'Juni',
    '7': u'Juli',
    '8': u'August',
    '9': u'September',
    '10': u'Oktober',
    '11': u'November',
    '12': u'Desember',
}


def find_image_versions(article):
    img = article.image
    img_strings = []

    for ver in VERSIONS.keys():
        if ver.startswith('article_'):
            img_strings.append(img.version_generate(ver).url)

    return img_strings


def create_article_filters(articles):
    rev_month_strings = dict((v, k) for k, v in MONTH_STRINGS.iteritems())

    # For creating the date filters.
    dates = {}
    for article in articles:
        d_year = str(article.published_date.year)
        if d_year not in dates:
            dates[d_year] = []
        dates = _create_months(article, dates)
    # Now sort months
    for year in dates:
        sorted_months = [''] * 12
        for month in dates[year]:
            sorted_months[int(rev_month_strings[month]) - 1] = month
        remove_these = []
        for n, m in enumerate(sorted_months):
            if m == '':
                remove_these.append(n)
        for i in reversed(remove_these):
            del sorted_months[i]
        dates[year] = sorted_months
    return dates


def _create_months(article, dates):
    d_year = str(article.published_date.year)
    d_month = str(article.published_date.month)
    for y in dates:
        if d_year == y:
            if MONTH_STRINGS[d_month] not in dates[d_year]:
                dates[d_year].append(MONTH_STRINGS[d_month])
    return dates
