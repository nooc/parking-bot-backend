# ParkingBot Backend

![App Icon](https://github.com/nooc/parking-bot-doc/blob/main/media/appicon.png)

## About

This is the backend for the ParkingBot [app](https://github.com/nooc/parking-bot-client) and runs on Google App Engine for Python.

## Setup

**Google**

- Create a google cloud project.
- Enable App Engine and Datastore.
- Create service account key. Generate json key and put it in the `parking-bot` folder.

**Repository**

- Configure the `.env` file.
- Configure the `app.yaml` file.
- Configure the `env.prod.yml` file.
- Configure the `env.test.yml` file.

Deploy using **gcloud** from inside `parking-bot` folder:

```sh
gcloud app deploy --promote --stop-previous-version --version=1 --project=<project name>
```

## Run

Change working dir to `parking-bot`.

Create local server certificate:

```sh
mkcert localhost 127.0.0.1 ::1
```

Create a python virtual environment:

```sh
python -m venv .venv
```

Activate the virtual environment and run pip:

```sh
python -m pip install -r requirements.txt
```

Run using for example **vscode** launch configuration:

```json
{
    "name": "Python Debugger: FastAPI",
    "type": "debugpy",
    "request": "launch",
    "module": "uvicorn",
    "args": [
        "app:parkingbot",
        "--reload",
        "--host","localhost",
        "--ssl-keyfile", "localhost+2-key.pem",
        "--ssl-certfile", "localhost+2.pem"
    ],
}
```

Browse swagger at `https://localhost:8000/docs`.

Rest API is accessed at `https://localhost:8000/api`

## Usage

### Authentication

For Android, authenticate to the service using JWT bearer containing the device id.

The JWT must be signed with a key shared between client and server.

A successful authentication request to `/api/user/init` will return a `test/plain` response containint an access token.

JWT EXAMPLE

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "identifier": "<DEVICE ID>",
  "exp": 1717002603,
  "iss": "parkingbot",
  "aud": "parkingbot",
  "iat": 1717002503
}
```

REQUEST EXAMPLE

```sh
curl -H 'Authorization: Bearer <JWT>' 'https://localhost:8000/api/user/init'
```

RESPONSE

The response is a signed JWT that should be validated.

Example payload:

```json
{
  "sub": "<DEVICE ID>",
  "exp": 1717002603,
  "iss": "parkingbot",
  "aud": "parkingbot",
  "iat": 1717002503
}
```
