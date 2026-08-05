## Documentation
OpenAPI documentation for the picoCTF web API is automatically generated and available at `<site_root>/api/v1`.

For example, if you are using `flask run` for [local development](https://github.com/picoCTF/picoCTF/blob/master/picoCTF-web/README.md), visit `http://localhost:5000/api/v1/`.

## CSRF token
Certain endpoints require a CSRF token. This token is sent by the server as the cookie `token` after signing in, and should be attached to requests as the `X-CSRF-Token` header.