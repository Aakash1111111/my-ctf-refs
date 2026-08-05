from hacksport.docker import DockerChallenge, Netcat

class Problem(DockerChallenge):

    # by overriding the setup class a challenge author can pass custom arguments
    # to the docker build process as well as specify custom descriptions for the
    # dynamically assigned ports
    def setup(self):

        # The use of the `Netcat` utility format will cause the port to be
        # appropriately formatted when shown to a competitor.
        self.ports = {5555: Netcat("vuln")}

        # The initialize_docker function builds an instance specific docker
        # image. You can pass in BUILD_ARGS which will be passed along to the
        # image build process and can be used in your Dockerfile.
        args = {'FLAG': self.flag}
        self.initialize_docker(args)

        # Once an image is built you can copy artifacts out in order to provide
        # them as downloads to a competitor.
        self.copy_from_image("/challenge/vuln")
