const { Input } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { ButtonToolbar } = ReactBootstrap;
const { Grid } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Well } = ReactBootstrap;
const { Accordion } = ReactBootstrap;

const ServerForm = React.createClass({
  propTypes: {
    new: React.PropTypes.bool.isRequired,
    refresh: React.PropTypes.func.isRequired,
    server: React.PropTypes.object
  },

  getInitialState() {
    let server;
    if (this.props.new) {
      server = {
        host: "",
        port: 22,
        username: "",
        password: "",
        protocol: "HTTP",
        name: "",
        server_number: 1
      };
    } else {
      ({ server } = this.props);
    }

    return { new: this.props.new, shellServer: server };
  },

  addServer() {
    apiCall("POST", "/api/v1/shell_servers", this.state.shellServer)
      .done(data => {
        apiNotify({ status: 1, message: "Shell server added." });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  deleteServer() {
    apiCall(
      "DELETE",
      `/api/v1/shell_servers/${this.state.shellServer.sid}`
    )
      .done(data => {
        apiNotify({ status: 1, message: "Shell server deleted." });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  updateServer() {
    const data = {
      name: this.state.shellServer.name,
      host: this.state.shellServer.host,
      port: this.state.shellServer.port,
      username: this.state.shellServer.username,
      password: this.state.shellServer.password,
      protocol: this.state.shellServer.protocol,
      server_number: this.state.shellServer.server_number
    };
    apiCall(
      "PATCH",
      `/api/v1/shell_servers/${this.state.shellServer.sid}`,
      data
    )
      .done(data => {
        apiNotify({ status: 1, message: "Shell server updated." });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  loadProblems() {
    apiCall(
      "PATCH",
      `/api/v1/problems?sid=${this.state.shellServer.sid}`
    )
      .done(data => {
        apiNotify({ status: 1, message: "Successfully loaded problems." });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  checkStatus() {
    apiCall(
      "GET",
      `/api/v1/shell_servers/${this.state.shellServer.sid}/status`
    )
      .done(function(data) {
        if (data.all_problems_online) {
          apiNotify({ status: 1, message: "All problems are online" });
        } else {
          apiNotify({
            status: 0,
            message:
              "One or more problems are offline. Please connect and fix the errors."
          });
        }
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  updateHost(e) {
    const copy = this.state.shellServer;
    copy.host = e.target.value;
    this.setState({ shellServer: copy });
  },

  updateName(e) {
    const copy = this.state.shellServer;
    copy.name = e.target.value;
    this.setState({ shellServer: copy });
  },

  updatePort(e) {
    const copy = this.state.shellServer;
    copy.port = parseInt(e.target.value);
    this.setState({ shellServer: copy });
  },

  updateUsername(e) {
    const copy = this.state.shellServer;
    copy.username = e.target.value;
    this.setState({ shellServer: copy });
  },

  updatePassword(e) {
    const copy = this.state.shellServer;
    copy.password = e.target.value;
    this.setState({ shellServer: copy });
  },

  updateServerNumber(e) {
    const copy = this.state.shellServer;
    copy.server_number = parseInt(e.target.value);
    this.setState({ shellServer: copy });
  },

  updateProtocol(value) {
    const copy = this.state.shellServer;
    copy.protocol = value;
    this.setState({ shellServer: copy });
  },

  render() {
    let buttons;
    const nameDescription = "A unique name given to this shell server.";
    const hostDescription = "The host name of your shell server.";
    const portDescription = "The port that SSH is running on.";
    const usernameDescription =
      "The username to connect as - Be sure that this user has sudo privileges!";
    const passwordDescription =
      "The password to use for authentication - Be sure that this is password is only used once.";
    const serverNumberDescription =
      "The designated server_number if sharding is enabled.";
    const protocolDescription =
      "The web protocol to access the problem files and shell server. This is most often just HTTP.";

    if (this.state.new) {
      buttons = (
        <ButtonToolbar className="pull-right">
          <Button onClick={this.addServer}>Add</Button>
        </ButtonToolbar>
      );
    } else {
      buttons = (
        <ButtonToolbar className="pull-right">
          <Button onClick={this.updateServer}>Update</Button>
          <Button onClick={this.deleteServer}>Delete</Button>
          <Button onClick={this.loadProblems}>Load Deployment</Button>
          <Button onClick={this.checkStatus}>Check Status</Button>
        </ButtonToolbar>
      );
    }

    return (
      <div>
        {this.props.new ? (
          <TextEntry
            name="Name"
            type="text"
            value={this.state.shellServer.name}
            onChange={this.updateName}
            description={nameDescription}
          />
        ) : (
          <span />
        )}
        <TextEntry
          name="Host"
          type="text"
          value={this.state.shellServer.host}
          onChange={this.updateHost}
          description={hostDescription}
        />
        <TextEntry
          name="SSH Port"
          type="number"
          value={this.state.shellServer.port.toString()}
          onChange={this.updatePort}
          description={portDescription}
        />
        <TextEntry
          name="Username"
          type="text"
          value={this.state.shellServer.username}
          onChange={this.updateUsername}
          description={usernameDescription}
        />
        <TextEntry
          name="Password"
          type="password"
          value={this.state.shellServer.password}
          onChange={this.updatePassword}
          description={passwordDescription}
        />
        <TextEntry
          name="Server Number"
          type="number"
          value={this.state.shellServer.server_number.toString()}
          onChange={this.updateServerNumber}
          description={serverNumberDescription}
        />
        <OptionEntry
          name="Web Protocol"
          value={this.state.shellServer.protocol}
          options={["HTTP", "HTTPS"]}
          onChange={this.updateProtocol}
          description={protocolDescription}
        />
        {buttons}
      </div>
    );
  }
});

const ShellServerList = React.createClass({
  getInitialState() {
    return { shellServers: [] };
  },

  refresh() {
    apiCall("GET", "/api/v1/shell_servers?assigned_only=false").done(
      data => {
        this.setState({ shellServers: data });
      }
    );
  },

  componentDidMount() {
    this.refresh();
  },

  createShellServerForm(server, i) {
    let header, shellServer;
    if (server === null) {
      shellServer = (
        <ServerForm new={true} key={i + "new"} refresh={this.refresh} />
      );
      header = <div> New Shell Server </div>;
    } else {
      shellServer = (
        <ServerForm
          new={false}
          server={server}
          key={server.sid}
          refresh={this.refresh}
        />
      );
      header = (
        <div>
          {server.name} - {server.host}
        </div>
      );
    }

    return (
      <Panel bsStyle="default" eventKey={i} key={i} header={header}>
        {shellServer}
      </Panel>
    );
  },

  render() {
    const serverList = _.map(
      this.state.shellServers,
      this.createShellServerForm
    );
    serverList.push(
      this.createShellServerForm(null, this.state.shellServers.length)
    );

    return <Accordion defaultActiveKey={0}>{serverList}</Accordion>;
  }
});

const ProblemLoaderTab = React.createClass({
  getInitialState() {
    return { publishedJSON: "" };
  },

  handleChange(e) {
    this.setState({ publishedJSON: e.target.value });
  },

  pushData() {
    apiCall("PATCH", "/api/v1/problems", this.state.publishedJSON)
      .done(data => {
        apiNotify({ status: 1, message: "Successfully loaded problems." });
        this.clearPublishedJSON();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  clearPublishedJSON() {
    this.setState({ publishedJSON: "" });
  },

  render() {
    const publishArea = (
      <div className="form-group">
        <h4>
          <Hint
            id="publisharea-hint"
            text="This should be the output of running 'shell_manager publish' on your shell server."
          />
          Paste your published JSON here:
        </h4>
        <Input
          className="form-control"
          type="textarea"
          rows="10"
          value={this.state.publishedJSON}
          onChange={this.handleChange}
        />
      </div>
    );

    return (
      <div>
        <Row>{publishArea}</Row>
        <Row>
          <ButtonToolbar>
            <Button onClick={this.pushData}>Submit</Button>
            <Button onClick={this.clearPublishedJSON}>Clear Data</Button>
          </ButtonToolbar>
        </Row>
      </div>
    );
  }
});

const ShellServerTab = React.createClass({
  render() {
    return (
      <Well>
        <Grid>
          <Row>
            <h4>To add problems, enter your shell server information below.</h4>
          </Row>
          <Row>
            <Col md={6}>
              <ShellServerList />
            </Col>
          </Row>
        </Grid>
      </Well>
    );
  }
});
