# Local Development

Start by installing [Homebrew](https://brew.sh/) and ensuring it's up-to-date:

```
brew update
```

Then setup up your Python environment:

```
brew install pyenv pyenv-virtualenv
pyenv install 3.11.4
```

You can ignore the warning about the `lzma` extension not being compiled.

Create a local virtualenv:

```
pyenv virtualenv 3.11.4 venv-django-shopify-embedded-app-3-11-4

# If you need to activate manually, run:
pyenv activate venv-django-shopify-embedded-app-3-11-4
```

Install Poetry, backend project dependencies and pre-commit hook:

```
brew install poetry
poetry install
```

Setup server environment variables:

```
cp .env.local.example .env
```

Setup your local database:

```
python manage.py migrate
```

Now you can run the local server:

```
python manage.py runserver
```
