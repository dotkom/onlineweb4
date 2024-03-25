from pathlib import Path

from django.core.management import BaseCommand
from wiki.models import URLPath


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # this creates online/ and komiteer/ in current working directory.
        root = URLPath.root()

        # the URLPath uses django-mptt (Modified Preorder Tree Traversa)
        # https://django-mptt.readthedocs.io/en/latest/models.html
        for p in root.get_descendants(include_self=True):
            # fields on each page: https://github.com/django-wiki/django-wiki/blob/0e4f95d69132148a4e1551991f33640f1b77d1ba/src/wiki/models/urlpath.py#L34

            # remove trailing slash
            filename = Path(
                f"{p.path[:-1]}.md" if p.is_leaf_node() else f"{p.path}index.md"
            )

            # fields on each article/revision https://github.com/django-wiki/django-wiki/blob/0e4f95d69132148a4e1551991f33640f1b77d1ba/src/wiki/models/article.py#L30
            article = p.article.current_revision
            # TODO: to we need a frontmatter?
            article_text = f"""# {article.title}

{article.content}"""
            filename.parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w") as f:
                f.write(article_text)
