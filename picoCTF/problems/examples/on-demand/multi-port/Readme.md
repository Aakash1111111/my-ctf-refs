# Key Delivery Service

This challenge demonstrates the ability to create more complex multi-port
challenges with the `DockerChallenge` class.

## Stats

- category: Miscellaneous
- points: 10
- time: 5-15 minutes
- difficulty: Easy

## Description

This challenge runs a simple, plaintext, TCP network service that delivers
a private key to a user. The user can then use the private key to SSH as
unprivileged user.

## Learning Objective

By the end of this challenge, competitors will have leveraged infomration from
one service to access another, thus chaining together multiple steps.
Additionally competitors will learn about key-based authentication options for
ssh.

## Solution

This challenge can be solved by connecting to the "key delivery service", saving
the private key that is provided and then using it to connect over SSH.

```
./solve.sh HOST KEY_PORT SSH_PORT
```

## Development/Testing/Deployment Notes

This challenge demonstrates the ability of the `DockerChallenge` class to
support more complex challenges involving multiple services or building blocks.

Additionally it shows the ability to describe the ports associated with
a challenge for a better user experience (`Netcat` and `Custom`).
