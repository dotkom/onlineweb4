# List of groups that should have edit access to Online wiki (public)
WIKI_OPEN_EDIT_ACCESS = [1, 2]
WIKI_OPEN_EDIT_ACCESS_GROUP_ID = 3

# List of groups that should have access to the Komite wiki
WIKI_COMMITTEE_ACCESS = [1, 2]
WIKI_COMMITTEE_ACCESS_GROUP_ID = 3

# Override "spam-settings" for django-wiki
WIKI_REVISIONS_PER_HOUR = 1000
WIKI_REVISIONS_PER_MINUTES = 500
WIKI_ATTACHMENTS_EXTENSIONS = [
    "pdf",
    "doc",
    "odt",
    "docx",
    "txt",
    "xlsx",
    "xls",
    "png",
    "psd",
    "ai",
    "ods",
    "zip",
    "jpg",
    "jpeg",
    "gif",
    "patch",
]

# Disable django-wiki's internal signup/login pages
WIKI_ACCOUNT_HANDLING = False
