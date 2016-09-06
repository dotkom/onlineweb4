## Access to LDAP server

We use the production LDAP server for developing and testing.
Anything else would be silly...

### Create SSH tunnel

    ssh -L 389:ldap-mirror.dotkom:389 <publicserver>.online.ntnu.no -l root

### Edit local settings

The settings in example-local.py should work fine with your SSH tunnel.
Ask one of the server room Wizards for the LDAP-password.
