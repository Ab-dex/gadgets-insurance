# Flask API 

This repository demonstrates a solid foundation for building a protected API with Flask.

## References

*

## Setup Environment

Configure a virtual environment, activate it and then install the requirements.

```bash
$ virtualenv venv -p python3
$ . venv/bin/activate
$ pip install -r requirements.txt
```

To display your python installed libraries run `pip freeze`.

Initialize and then migrate a local SQLite database, you should then see a local *app.db* file.  

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
```

You should now see a file called **app.db**. You can view the database with [DB Browser for SQLite](https://sqlitebrowser.org/) or IntelliJ also has a plugin.

## Running the app

To start the application activate the python virtual environment and run flask:

```bash
$ . venv/bin/activate
(venv) $ flask run
 * Serving Flask app "application.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Register a new user and then get your information.

Using [HTTPie](https://httpie.org/) here is a how you can register a new user and acquire a token to use the API.

### Register a user

Register a new user.

```bash
$ http POST :5000/api/registerUser username=David password=pass email=a@mail.com
HTTP/1.0 201 CREATED
Content-Length: 57
Content-Type: application/json
Date: Tue, 09 Jul 2019 01:38:38 GMT
Location: http://localhost:5000/users/david
Server: Werkzeug/0.15.4 Python/3.7.3

{
    "email": "a@mail.com", 
    "username": "123456"
}
```

### Acquire a token 

Acquire a token.

```bash
$ http -adavid:pass GET http://localhost:5000/api/auth/token
HTTP/1.0 200 OK
Content-Length: 193
Content-Type: application/json
Date: Tue, 09 Jul 2019 01:41:37 GMT
Server: Werkzeug/0.15.4 Python/3.7.3

{
    "duration": 600, 
    "token": "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU2MjYzNjQ5NywiZXhwIjoxNTYyNjM3MDk3fQ.eyJpZCI6MX0.IXBjsz-uH43fGk5qqELjEupRMda1RzHobazafFVzTut0h40GfVttGSOJy9IvsTT2z8vcqTgYleZMbgC9nXozjQ"
}
```

### Get your account information by authenticating with the token

Get your account info.

```bash
$ http -aeyJhbGciOiJIUzUxMiIsImlhdCI6MTU2MjYzNjQ5NywiZXhwIjoxNTYyNjM3MDk3fQ.eyJpZCI6MX0.IXBjsz-uH43fGk5qqELjEupRMda1RzHobazafFVzTut0h40GfVttGSOJy9IvsTT2z8vcqTgYleZMbgC9nXozjQ:x GET http://localhost:5000/api/users/me
HTTP/1.0 200 OK
Content-Length: 57
Content-Type: application/json
Date: Tue, 09 Jul 2019 01:43:30 GMT
Server: Werkzeug/0.15.4 Python/3.7.3

{
    "email": "a@mailcom", 
    "username": "123456"
}
```

## Flask Shell

Flask shell gives you a python interpreter shell with the context of your application. Here is an example of creating a new user via CLI. 

```bash
$ flask shell
>>> from werkzeug.security import generate_password_hash
>>> db.session.add(User(username='david', email='a@mail.com', password=generate_password_hash('pass')))
>>> db.session.commit()
>>> exit()
```



# TODO

* Excerpt of related entities (i.e., POSTS)
* Decorators
