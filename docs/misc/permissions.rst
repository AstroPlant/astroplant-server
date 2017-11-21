=================================
Permissions and access management
=================================

The AstroPlant backend deals with complex relationships between users and objects.
For example, a user might have access to view a kit's dashboard, can add new users
to the kit, but is not allowed to change its configuration.

To keep track of object level permissions in a clean way (instead of, e.g., inlining
permission rules), the `Django Rules <https://github.com/dfunckt/django-rules>`_
application is used. This decouples the rules that make up a permission from using
permissions in the project as a whole.

The rules used in AstroPlant are defined in the :mod:`backend.rules` module.
