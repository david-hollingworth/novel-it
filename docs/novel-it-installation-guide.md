# Novel-It Installation Guide
## Requirements
Novel-It is a Django based, web-application. To run it you will need a system with Python (at least version 3.12) installed. The following installation instructions have been tested on Linux (Ubuntu), but should work equally well on a Windows system.

## Getting Started
Download the application from Github and cd to the application folder:

```
git clone https://github.com/david-hollingworth/novel-it.git
cd novel-it/novelapp
```
Create a virtual environment. This isn't mandatory, but it highly recommended to avoid Package version conflicts with other Python applications you have installed now, or may install in the future:
```
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```
Now install the application's requirements:

`pip install -r requirements.txt`

## Configuration

Copy the example .env.example to create a live version

`cp ../.env.example .env`

Before editing the file you'll need to create a Django secret key. Generate this by running the command:

```
python -c "import secrets; print(secrets.token_urlsafe(50))"
some-random-key-will-appear
```

Copy the key somewhere safe and then edit the .env file with your favorite text editor. For example:

`nano .env`

This table shows the environment variables and how to set them:

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | *(required)* | Django secret key, created above. |
| `DJANGO_DEBUG` | `False` | Set to `True` for a development environment, otherwise leave it as False|
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts. See below for comments. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Comma-separated list of trusted origins |
| `DATABASE_URL` | SQLite | PostgreSQL connection string, e.g. `postgresql://user:pass@localhost:5432/novelapp`. See below. |

### Allowed Hosts
If you're going to be accessing the application using a browser that's installed on the same system as the application then you can leave DJANGO_ALLOWED_HOSTS as it is. However, if you have the application on one machine and you want to access it from another computer then you need to add the IP address of the application server to the DJANGO_ALLOWED_HOSTS list.

For example, you have the application installed on a Linux machine, but you want to access it from your Windows laptop. Then you will need to add the IP address of the Linux machine to ALLOWED_HOSTS. Finding the IP address of the Linux machine is outside the scope of this document (hint: use `ìfconfig`). For example, if the IP address of your Linux machine is 192.168.1.10, and the machine's hostname is `myserver` then DJANGO_ALLOWED_HOSTS should look like this:

`DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,myserver,192.168.1.10`

### CSFR Trusted Origins
The same comments apply to DJANGO_CSRF_TRUSTED_ORIGINS as to DJANGO_ALLOWED_HOSTS. Use the full URL for DJANGO_CSRF_TRUSTED_ORIGINS, including the port number.

### Database Configuration
By default the application will use an sqlite database. For a single user this is probably going to be fine. It's very simple to backup and will work well without any further configuration.

If you've a preference for a full-blown relational database, or you're going to have several (or more) people working on content in Novel-It, then you'll want to use a Postgresql database. Again, installation and configuration of Postgresql is outside the scope of this document. Just make sure you have the database created and the Postgres user who owns the database can login to it (hint: use `pgadmin4` for managing the database server).

### Run Migrations
If you're using the default sqlite database then go ahead and run these commands to create the database and all the related structures. If you're using Postgresql you have to have installed the database server and created a database for Novel-It before you can run these commands.
```
python manage.py migrate
python manage.py createsuperuser
```

### Collect Static Files
This needs to be done once per installation:
`python manage.py collectstatic --noinput`

# Run The Server
You're now ready to run the application for the first time:

`gunicorn novelapp.wsgi`

Note, if you've configured a port other than 8000 in DJANGO_CSRF_TRUSTED_ORIGINS then use that port number in the command above.

The installation is now complete. To access the application point your web browser at one of the configured URLs. Don't forget to include the port number. For example `http://localhost:8000` If everything is configured correctly you'll see the login page.

