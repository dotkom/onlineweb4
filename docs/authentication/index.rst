Authentication
==============

.. toctree::
   :maxdepth: 2
   
   api

Registration
------------

Uses :py:class:`apps.authentication.forms.RegisterForm`.

Generates an :py:class:`apps.authentication.models.RegisterToken` which is used to verify the email.

On successful registration a new :py:class:`apps.authentication.models.OnlineUser` object is created.
This object is based on the built-in Django User object.

Since a user can have multiple emails the registered email is stored as :py:class:`apps.authentication.models.Email`.
This email is also marked as the primary email, but the primary email can be changed by the user.

Email verification
******************

Upon registration an email with an uuid generated URL is sent to the user.
This URL has to be visited before the account is activated. 

If the email the user registrated with is an NTNU issued email (stud.ntnu.no) the :py:attr:`apps.authentication.models.OnlineUser.ntnu_username` field is set.
`ntnu_username` is used to verify that the user is a student.

If the user has already been approved as an Online member info mail is automatically enabled.
Nowadays this is not used anymore as all members are required to be manually approved.  

Login
-----

Uses :py:class:`apps.authentication.forms.LoginForm`.

Allows logging in with both username and email. 

Logout
-------

Uses built-in Django logout method. 

Recover lost password
---------------------

Uses :py:class:`apps.authentication.forms.RecoveryForm`.

Creates a :py:class:`apps.authentication.models.RegisterToken` which is emailed to the user in the same manner as verification during registration is.
Allows the user to create a new password.
