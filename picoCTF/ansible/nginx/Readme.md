# nginx

This role installs and configures the `nginx` web server.

This role is used by the `pico-web` web role to support the front-end and API.

This role is used  by the `pico-shell` role to support challenge artifact
downloads.

## Expected Varaibles

At a minimum this role expects:

`site_config_name`to be set to a value that matches a template provided in
the calling role. For example in the `pico-web` role `site_config_name` is set
to `ctf` and the file `pico-web/templates/ctf.nginx.j2` exists.


