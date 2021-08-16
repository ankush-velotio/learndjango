# Project structure

## Apps in the project

- ## users
    - This app is the full implementation of the authentication features.
    - Authentication is implemented using custom JWT token.
    - Creating JWT tokens using `pyjwt` package.
    - This app has features for registering user, login user, user view and logout.

## Project directories

- ## postgresdocker
    - Docker compose file for provisioning PostgreSQL container with the database and using docker volumes for persisting the data.
