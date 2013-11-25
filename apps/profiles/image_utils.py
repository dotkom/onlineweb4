#-*- coding: utf-8 -*-
import os
import shutil

from PIL import Image

from apps.profiles import images2gif

from django.conf import settings
from django.utils.translation import ugettext as _


def handle_upload(request):

    # Make sure the image directories exist before we try doing anything
    create_directories_error = create_directories_if_not_exist()
    if create_directories_error:
        return False, create_directories_error

    statuses = []
    uploaded_file = request.FILES['image']

    if uploaded_file is None:
        statuses.append('Ingen fil lastet opp')
        return False, statuses

    statuses.extend(validate_image_content_type(uploaded_file))
    statuses.extend(validate_image_file_size(uploaded_file))
    extension, file_type_errors = validate_file_type(uploaded_file)
    statuses.extend(file_type_errors)

    # If we got errors already, return them, as there is no point in proceeding any further
    if len(statuses) > 0:
        return False, statuses

    username = request.user.username
    # Create variables for image name, image backup name and their paths
    user_image_name = username + extension
    user_image_name_path = os.path.join(settings.MEDIA_ROOT, "images", "profiles", user_image_name)
    user_image_name_backup = user_image_name + ".bak"
    user_image_name_backup_path = os.path.join(settings.MEDIA_ROOT, "images", "profiles", user_image_name_backup)

    exception_thrown = False
    generic_fail_status = _(u'Bildet kunne ikke lagres')

    try:
        # Attempt to create a backup of user's image
        created_backup = create_file_backup(user_image_name_path, user_image_name_backup_path)
        # Attempt removing a users image
        remove_user_profile_image_successful = remove_user_profile_image(request)

        # If (file existed AND backup failed) OR remove user image failed
        if (os.path.exists(user_image_name_path) and created_backup is False) or not remove_user_profile_image_successful:
            return False, [generic_fail_status]

        if extension == ".gif":
            save_animated_image(request, uploaded_file, extension, user_image_name_path)
        else:
            save_regular_image(request, uploaded_file, extension, user_image_name_path)

    except Exception, err:

        print err.message

        os.remove(user_image_name_path)
        request.user.image = None
        exception_thrown = True

        # If we created a backup of the user's image, restore it
        if created_backup:
            shutil.copy2(user_image_name_backup_path, user_image_name_path)
            request.user.image = os.path.join(settings.MEDIA_URL, "images", "profiles", request.user.username + extension)

    finally:
        # Remove the backup if we created a backup of the user's image
        if created_backup:
            os.remove(user_image_name_backup_path)

        request.user.save()

    if exception_thrown:
        return False, statuses
    else:
        statuses.append(_(u"Bildet ble lagret"))

    return True, statuses


# Validate content type of upload. Content type must be 'image'
def validate_image_content_type(uploaded_file):

    accepted_content_type = 'image'
    uploaded_content_type = uploaded_file.content_type.split('/')[0]

    if uploaded_content_type.lower() != accepted_content_type.lower():
        return [_(u"Filen som ble lastet opp er ikke et bilde")]
    return []


# Validate the file not exceeding the max allowed file size
def validate_image_file_size(uploaded_file):

    # 2.5MB - 2621440
    max_file_size = 2621440
    uploaded_file_size = uploaded_file.size

    if uploaded_file_size > max_file_size:
        # Output returns megabytes instead of bytes
        return [_(u"Filstørrelsen er for stor (max %sMB)" % str(float(max_file_size) / float(1024**2)))]
    return []


# Validate that the file type is of an acceptable type
def validate_file_type(uploaded_file):

    allowed_file_types = ['.bmp', '.gif', '.jfif', '.jpeg', '.jpg', '.png']
    errors = []
    extension_index, file_ending_error = validate_file_ending(uploaded_file)

    if extension_index == -1:
        errors.extend(file_ending_error)
        return None, errors

    extension = uploaded_file.name[extension_index:]

    if extension not in allowed_file_types:
        errors.extend([_(u"Filtypen er ikke av et godkjent format %s" % ", ".join(allowed_file_types))])
        return extension, errors

    return extension, errors


# Validate the file ending, the file must have a file type
def validate_file_ending(uploaded_file):

    extension_index = uploaded_file.name.rfind('.')
    errors = []

    if extension_index == -1:
        errors.extend([_(u"Filnavnet inneholder ikke en filtype")])

    return extension_index, errors


# Make sure directories exist
def create_directories_if_not_exist():

    try:
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "images", "profiles")):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "images", "profiles"))
    except OSError:
        return [_(u'Internal server error')]
    return None


# Copies a file to a destination with attributes intact
def create_file_backup(source_path, destination_path):

    try:
        if os.path.exists(source_path):
            shutil.copy2(source_path, destination_path)
            return True
        return False

    except OSError:
        return False


# Removes a users profile image
def remove_user_profile_image(request):

    try:
        # If "/profiles/" is in the filename, it is not the default profile image
        if "/profiles/" in request.user.get_image_url():
            extension_index = request.user.image.name.rfind('.')
            extension = request.user.image.name[extension_index:]
            filename = os.path.join(settings.MEDIA_ROOT, "images", "profiles", request.user.username + extension)
            request.user.image = None
            request.user.save()
            os.remove(filename)
        return True
    except OSError:
        return False


def save_regular_image(request, uploaded_file, extension, user_image_name_path):

    save_image_file(uploaded_file, user_image_name_path)
    crop_bounding_box = get_crop_bounding_box(request)

    img = Image.open(user_image_name_path)
    crop_img = img.crop(crop_bounding_box)

    #Saving the image here so we release the lock on the file
    img.save(user_image_name_path)

    #Actual cropping save
    crop_img.save(user_image_name_path)

    #Set media url for user image
    request.user.image = os.path.join(settings.MEDIA_URL, "images", "profiles", request.user.username + extension)
    request.user.save()


def save_image_file(uploaded_file, user_image_name_path):

    destination = open(user_image_name_path, 'wb+')

    for chunk in uploaded_file.chunks():
        destination.write(chunk)
    destination.close()


def get_crop_bounding_box(request):

    return (int(float(request.POST['x'])), int(float(request.POST['y'])),
            int(float(request.POST['x2'])), int(float(request.POST['y2'])))


def save_animated_image(request, uploaded_file, extension, user_image_name_path):

    save_image_file(uploaded_file, user_image_name_path)
    crop_bounding_box = get_crop_bounding_box(request)

    frames = images2gif.readGif(user_image_name_path, False)
    frames2 = []

    for frame in frames:
        frame2 = frame
        frame2 = frame2.crop(crop_bounding_box)
        frames2.append(frame2)

    images2gif.writeGif(user_image_name_path, frames2, subRectangles=True)

    request.user.image = os.path.join(settings.MEDIA_URL, "images", "profiles", request.user.username + extension)
    request.user.save()