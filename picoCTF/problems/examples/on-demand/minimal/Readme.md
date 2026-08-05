# Docker World

This challenge demonstrates the most simple use of the `DockerChallenge` class.

## Stats

- category: Miscellaneous
- points: 5
- time: 1-10 minutes
- difficulty: Easy

## Description

This challenge runs a simple plaintext TCP network service that provides the
flag when a competitor submits a specific message (`hello`) in response to
a prompt.

## Learning Objective

By the end of this challenge, competitors will have used a command line tool
such `netcat` to communicate and send specific data to a simple network service.
This will prepare a competitor to interact with more complex network services.

## Solution

This challenge can be solved by sending the requested message to the service.

```
./solve.sh HOST PORT
```

## Development/Testing/Deployment Notes

This challenge demonstrates the most simple use of the `DockerChallenge` class.

It demonstrates that essentially all that is required from a challenge author
is an arbitrary Dockerfile. It also shows the use of default port extraction
(based on EXPOSEd ports) as well as the ability to use standard picoCTF
templating in challenge design.
