from filebrowser.settings import VERSIONS


def find_image_versions(company):
    img = company.image
    img_strings = []
    print("gnna find sm imgs")

    for ver in VERSIONS.keys():
        if ver.startswith('companies_'):
            print(ver)
            img_strings.append(img.version_generate(ver).url)

    return img_strings