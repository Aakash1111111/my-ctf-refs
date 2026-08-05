# picoCTF-web Load Tests

Locust tests designed to simulate user load against the web API.

Most actions on the picoCTF platform require the user to be signed into a registered account, so before running load tests, we must create a pool of user accounts for the test runners to use.

To do so, run the registration locustfile. This will create a variety of users with random attributes and store them in a specified MongoDB database (connection information can be modified in `config.py`). After starting Locust, navigate to its web interface running on port `:8089` and specify the number of users to simulate. For the registration locustfile, spawned threads will terminate after successfully registering an account, so "Number of users to simulate" corresponds exactly to the number of sample accounts to create. Creating at least a few thousand accounts is recommended.

The act of running the registration locustfile can also be thought of as simulating the initial flood of registrations during the start of a competition.

```
locust -f registration.py --host=<INSTANCE_ROOT_URL>
```

After an initial pool of test users has been created, the main testing locustfile (`load_testing.py`) can be used to simulate user flows. The credentials of a platform administrator must also be specified within `config.py` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`) prior to running the tests.

```
locust -f load_testing.py --host=<INSTANCE_ROOT_URL>
```
