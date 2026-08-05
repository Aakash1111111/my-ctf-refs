# Buffer Overflow 2

This challenge demonstrates the ability to provide artifacts from a
`DockerChallenge` style challenge.

## Stats

- category: Binary Exploitation
- points: 50
- time: 10-60 minutes
- difficulty: Easy

## Description

This challenge runs a simple echo TCP network service that is vulnerable to
a stack based buffer overflow (`gets`).  The challenge disables many modern
mitigations disabled (DEP, stack-cookies). Additionally the challenge leaks the
address of the buffer that can be overflowed.

## Learning Objective

By the end of this challenge, competitors will have learned about the inherent
vulnerability of the `gets` function and exploited a stack based buffer
overflow. Additionally competitors can leverage a stack address leak to return
to shellcode on the stack.

## Solution

This challenge can be solved by reading the leaked stack address and sending
a payload that clobbers the return address in order to return to shellcode on
the stack.

The provided solve script demonstrates using `pwntools` to achieve this.

```
./solve.py HOST PORT
```

## Development/Testing/Deployment Notes

This challenge demonstrates a slightly more complex use of the `DockerChallenge`
class.

It shows the ability to describe the ports associated with a challenge for
a better user experience (`self.ports` and `Netcat`).

It also shows the ability to pass arguments to the docker build process in the
explicit `self.initialize_docker` call.

Finally it demonstrates the ability to extract artifacts from the per instance
docker image using `self.copy_from_image`. These artifacts can then be provided
to a competitor using the traditional  `url_for` approach.
