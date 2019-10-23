# poptape-profile
Profile microservice written in Python Flask

This microservice stores basic profile data in a Postgres database.

Please see [this gist](https://gist.github.com/cliveyg/cf77c295e18156ba74cda46949231d69) to see how this microserv
cie works as part of the auction system software.

### API routes

```
/profile [GET] (Authenticated)

Returns the profile for the authenticated user. 
Possible return codes: [200, 404, 401, 502]

/profile [POST] (Authenticated)

Create a profile of the authenticated user.
Possible return codes: [200 400 401 422]

/profile [DELETE] (Authenticated)

Deletes the profile for the authenticated user
Possible return codes: [204, 401]

/profile/<uuid> [GET] (Unauthenticated)

Returns the profile resource defined by the UUID in the URL. 
Possible return codes: [200, 401, 404]

/profile/status [GET] (Unauthenticated)

Returns a JSON message indicating system is running 
Possible return codes: [200]

```

#### Notes:
To run this microservice it is recommended to use a Python virtual environment and run `pip install -r requirements.txt`. 

#### Rate limiting:
In addition most routes will return an HTTP status of 429 if too many requests are made in a certain space of time. The time frame is set on a route by route basis.

#### Tests:
Tests can be run from app root using: `pytest --cov=app app/tests`

#### Docker:
This app can now be run in Docker using the included docker-compose.yml and Dockerfile. The database and roles still need to be created manually after successful deployment of the app in Docker. It's on the TODO list to automate these parts :-)

#### TODO:
* Add more admin only routes for bulk actions etc.
* Add tests.
* Make code pep8 compliant even though imo pep8 code is uglier and harder to read ;-)
* Automate docker database creation and population.
