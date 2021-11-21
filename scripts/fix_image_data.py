from apps.gallery.models import ResponsiveImage, UnhandledImage

images = UnhandledImage.objects.all()
for image in images:
    file = image.image
    thumb = image.thumbnail
    image.size = file.size
    image.thumbNailsize = thumb.size
    image.width = file.width
    image.height = file.height
    image.save()

images = ResponsiveImage.objects.all()
for image in images:
    total = 0
    total = image.thumbnail.size
    total += image.image_xs.size
    total += image.image_sm.size
    total += image.image_md.size
    total += image.image_lg.size
    total += image.image_wide.size
    total += image.image_original.size
    image.total_size = total
    image.save()
