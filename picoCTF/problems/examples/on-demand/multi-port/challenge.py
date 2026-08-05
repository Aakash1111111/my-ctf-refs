from hacksport.docker import DockerChallenge, Netcat, Custom

# The DockerChallenge class allows the create of on-demand challenge instances
# in an isolated environment.
class Problem(DockerChallenge):

    def setup(self):

        # A DockerChallenge can have multiple ports supporting more complex
        # challenge constructions. The class support "naming" these ports for
        # more user friendly presentation. If a port is EXPOSED in the Dockerfile
        # but not explicitly named it will simply be presented to the user as a
        # host/port combination.
        self.ports = {
                5555: Netcat("key delivery service"),
                22: Custom("<code>ssh challenge@{host} -p {{port}}</code>", "SSH")
                }

        # The initialize_docker function builds an instance specific docker
        # image which a competitor will then launch on-demand.
        self.initialize_docker({})
