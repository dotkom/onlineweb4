from pathlib import Path

from django.core.management import BaseCommand
from git import Actor, Repo
from tqdm import tqdm
from wiki.models import ArticleRevision


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        path = Path("repo")
        repo = Repo.init(path)

        for revision in tqdm(
            ArticleRevision.objects.filter(
                article__other_read=True,
            )
            .select_related("article", "user")
            .iterator(chunk_size=500),
            total=ArticleRevision.objects.filter(article__other_read=True).count(),
        ):
            url: str = revision.article.get_absolute_url()
            if not url.startswith("/wiki/online"):
                continue
            # remove inital /, makes path absolute which we do not want

            repo_relative = (
                Path(url.replace("/wiki/online/", "src/content/docs/")) / "index.md"
            )
            file = path / repo_relative
            if revision.deleted:
                file.unlink()
            else:
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch(exist_ok=True)

            file.write_text(f"""---
+title: "{revision.title}"
+---
+
 {revision.content}""")
            repo.index.add([repo_relative])

            author_info = revision.user
            if author_info is not None:
                author = Actor(author_info.first_name, author_info.email)
            else:
                author = Actor(f"Ukjent (brukerid {revision.user_id})", None)
            repo.index.commit(
                revision.user_message,
                author=author,
                committer=author,
                author_date=revision.created,
                commit_date=revision.created,
                skip_hooks=True,
            )

        repo.index.write()
