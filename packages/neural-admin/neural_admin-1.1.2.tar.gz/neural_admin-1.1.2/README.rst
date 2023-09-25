=============================
Neural Dynamics custom admin
=============================

Overview
--------

Neural Dynamics custom admin is a Django app allowing to automaticly blur fields and make email agent popup on email click in django admin model

Also it provides search only by fields first_name and last_name used as showed below::

    first_name-/|\-last_name

Quick start
------------
1. Install using command

.. code-block:: bash
   
   pip install neural-admin

2. Define your admin model and import custom admin

.. code-block:: python

    from neural_admin.admin import CustomAdmin

    class SUserAdmin(CustomAdmin, UserAdmin):
        email_fields = ("email",) # Pass here fields you want to open an email agent onclick
        blur_fields = ("pin_code",) # Pass here fields you want to blur. When you click on blurred field it will show you field value.