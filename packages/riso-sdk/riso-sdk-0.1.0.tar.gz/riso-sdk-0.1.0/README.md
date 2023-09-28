One Software Development Kit
=====

Extend Django things as SDK for One Development


Installation and usage
======================

Quick start
-----------

1. Add "sdk" to your INSTALLED_APPS setting like this::

   ``` python
        INSTALLED_APPS = [
            ...,
            "sdk",
        ]
    ```


Django Allauth
--------------

1. Configure your settings.py

    ``` python
    # Add the following lines to your settings.py
    TEMPLATES = [
        {
            "OPTIONS": {
                # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
                "context_processors": [
                    ...
                    "sdk.allauth.context_processors.allauth_settings",
                ],
            },
        },
    ]
    
    # django-allauth
    # ------------------------------------------------------------------------------
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    ACCOUNT_ADAPTER = "sdk.allauth.adapters.AccountAdapter"
    # https://django-allauth.readthedocs.io/en/latest/forms.html
    ACCOUNT_FORMS = {"signup": "sdk.allauth.forms.UserSignupForm"}
    # https://django-allauth.readthedocs.io/en/latest/configuration.html
    SOCIALACCOUNT_ADAPTER = "sdk.allauth.adapters.SocialAccountAdapter"
    # https://django-allauth.readthedocs.io/en/latest/forms.html
    SOCIALACCOUNT_FORMS = {"signup": "sdk.allauth.forms.UserSocialSignupForm"}

    ```

Riso Sweet Message
------------------

1. Add "messages" to your TEMPLATES setting like this::

   ``` python
    TEMPLATES = [
        {
            "OPTIONS": {
                "builtins": [
                    "sdk.contrib.messages.templatetags.sweet_message",
                ]
            },
        },
    ]
    ```

2. Add "messages" to your "base.html" like this

    ``` html
    {% sweet_message_media True %} # If your template already add jquery and bootstrap, you can set this to False
    </head>

    {% include 'messages/widget.html' %}
    </body>
    ```

How to contribute
=================

Please make sure to update tests as appropriate.

Getting Started
---------------

1. Clone the repository

    ``` bash
    # Run the following command in your terminal
    pre-commit install
    git update-index --assume-unchanged .idea/runConfigurations/* .idea/riso.iml
    ```

2. Prepare the environment, Create a virtual environment with Python 3.11 or higher and activate it. Then install the
   dependencies using pip:

    ``` bash
    # Run the following command in your terminal
    cd riso
    pip install -r requirements.txt
    ```

3. Update following files

    ```
    # .envs/.local/.django
    # .envs/.local/.postgres
    ```

4. Then using pycharm runConfiguration to start coding

Useful commands
---------------

- Run test with coverage

    ``` bash
    docker-compose -f riso/local.yml run --rm django pytest --cov --cov-report term-missing --cov-report html
    ```

Other information
=================

What's in this project?
-----------------------

This project is a Django project with a single app called "sdk".
