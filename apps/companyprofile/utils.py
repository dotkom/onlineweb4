from filebrowser.settings import VERSIONS


def find_image_versions(company):
    img = company.old_image
    img_strings = []

    for ver in VERSIONS.keys():
        if ver.startswith('companies_'):
            img_strings.append(img.version_generate(ver).url)

    return img_strings
