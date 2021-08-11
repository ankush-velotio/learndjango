# Project structure

## Apps in the project

- ## jwtauth
    - This app is implemented using `djangorestframework-jwt` package. This app will return a JWT token and using this token we can perform authorization.
    - This app has limited customizations.

- ## users
    - This app is the full implementation of the authentication features.
    - Authentication is implemented using custom JWT token.
    - Creating JWT tokens using `pyjwt` package.
    - This app has features for registering user, login user, user view and logout.

- ## news
    - Simple django app using dynamic urls.

## Project directories

- ## postgres_docker
    - Docker compose file for provisioning PostgreSQL container with the database and PgAdmin and using docker volumes for persisting the data.

- ## postgresdocker
    - Docker compose file for provisioning PostgreSQL container with the database and using docker volumes for persisting the data.
