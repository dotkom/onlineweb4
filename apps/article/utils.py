from filebrowser.settings import VERSIONS


def find_image_versions(article):
    img = article.image
    img_strings = []

    for ver in VERSIONS.keys():
        if ver.startswith('article_'):
            img_strings.append(img.version_generate(ver).url)

    return img_strings
