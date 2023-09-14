# Getting Started

This repo is a demonstration of how to build an embedded Shopify app using Django. It fully implements the recommended OAuth flow for Shopify apps and seamless support for adding/removing access scopes at any time after the app is installed. It was last confirmed working in September 2023.

## Shopify Setup

Start by creating a [Shopify Partner](https://www.shopify.com/partners) account and a [development store](https://shopify.dev/docs/apps/tools/development-stores#create-a-development-store-to-test-your-app) to use for testing. I recommend having Shopify generate test data in your development store.

On your [Shopify Partner dashboard](https://partners.shopify.com/) navigate to "Apps" and click the "Create app" button. Click "Create app manually" and provide your app a name. After your app is created go to "App setup" and fill out the "URLs" section: App URL (`http://localhost:8000/shopify/embedded_app/`) and Allowed redirection URL(s) (`http://localhost:8000/shopify/embedded_app/callback/`).

## Local Setup

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
