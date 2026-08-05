const { ListGroupItem } = ReactBootstrap;
const { ListGroup } = ReactBootstrap;
const { Accordion } = ReactBootstrap;
const { Panel } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { Glyphicon } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Badge } = ReactBootstrap;

const { update } = React.addons;

const TestGroupItem = React.createClass({
  render() {
    let glyphName = "asterik";
    let glyphStyle = "";

    switch (this.props.status) {
      case "waiting":
        glyphName = "refresh";
        glyphStyle = "spin";
        break;
      case "failing":
        glyphName = "remove";
        break;
      case "passing":
        glyphName = "ok";
        break;
    }

    let elapsedDisplay = "...";
    if (this.props.elapsed) {
      elapsedDisplay = `${parseFloat(this.props.elapsed).toFixed(1)} secs`;
    }

    return (
      <ListGroupItem>
        <h4>
          <Glyphicon glyph={glyphName} className={glyphStyle} />{" "}
          {this.props.name} <span className="pull-right">{elapsedDisplay}</span>
        </h4>
      </ListGroupItem>
    );
  }
});

const TestGroup = React.createClass({
  getInitialState() {
    const state = {};
    _.map(this.props.tests, function(test) {
      state[test.name] = test;
      state[test.name].status = "waiting";
      state[test.name].start = Date.now();
    });
    return state;
  },

  updateTestState(testName, status) {
    const updateObject = {};
    updateObject[testName] = {
      status: { $set: status },
      elapsed: {
        $set: (Date.now() - this.state[testName].start) / 1000.0 //seconds
      }
    };
    const newState = update(this.state, updateObject);

    let totalStatus = "passing";
    if (_.any(newState, test => test.status === "waiting")) {
      totalStatus = "waiting";
    } else if (_.any(newState, test => test.status === "failing")) {
      totalStatus = "failing";
    }

    this.setState(newState);
    his.props.onStatusChange(totalStatus);
  },

  componentWillMount() {
    //Initiate all the tests with the updateTestState callback
    _.each(this.state, (test, testName) => {
      test.func(this.updateTestState.bind(null, testName));
    });
  },

  render() {
    return (
      <Panel>
        <ListGroup fill={true}>
          {_.map(_.values(this.state), (test, i) => (
            <TestGroupItem {...Object.assign({ key: i }, test)} />
          ))}
        </ListGroup>
      </Panel>
    );
  }
});

const CompetitionCheck = React.createClass({
  getInitialState() {
    return { competitionReadiness: "waiting" };
  },

  alwaysTrue(t, setStatus) {
    return setTimeout(setStatus.bind(null, t), Math.random() * 3000);
  },

  checkEnabledProblems(setStatus) {
    apiCall(
      "GET",
      "/api/v1/problems?unlocked_only=false&include_disabled=true"
    ).done(function(data) {
      let status = "failing";
      for (let problem of data) {
        if (problem.disabled === false) {
          status = "passing";
          break;
        }
      }

      setStatus(status);
    });
  },

  checkProblemsAlive(setStatus) {
    apiCall("GET", "/api/v1/shell_servers?assigned_only=false").done(
      data => {
        let status = "passing";
        const servers = data;

        if (servers.length === 0) {
          status = "failing";
        }

        const apiCalls = $.map(servers, server =>
          apiCall("GET", `/api/v1/shell_servers/${server.sid}/status`)
        );
        $.when.apply(this, apiCalls).done(function() {
          for (let result of $.map(arguments, _.first)) {
            if (!result.status) {
              status = "failing";
            }
          }
          setStatus(status);
        });
      }
    );
  },

  checkDownloadsAccessible(setStatus) {
    apiCall(
      "GET",
      "/api/v1/problems?unlocked_only=false&include_disabled=true"
    ).done(data => {
      let status = "passing";
      const requests = [];
      for (let problem of data) {
        for (let instance of problem.instances) {
          $(`<p>${instance.description}</p>`)
            .find("a")
            .each(function(i, a) {
              const url = $(a).attr("href");
              requests.push(
                $.ajax({ url, dataType: "text", type: "GET" })
              );
            });
        }
      }

      $.when.apply(this, apiCalls).done(function() {
        for (let result of arguments) {
          if (result.status === 404) {
            status = "failing";
          }
        }

        setStatus(status);
      });
    });
  },

  onStatusChange(status) {
    this.setState(
      update(this.state, { competitionReadiness: { $set: status } })
    );
  },

  render() {
    const sanityChecks = [
      { name: "Check Enabled Problems", func: this.checkEnabledProblems },
      {
        name: "Problems Alive on Shell Servers",
        func: this.checkProblemsAlive
        //{name: "Problem Downloads Accessible", func: @checkDownloadsAccessible}
      }
    ];

    return (
      <div>
        <h3>
          Competition Status: <b>{this.state.competitionReadiness}</b>
        </h3>
        <Col md={6} className="hard-right">
          <TestGroup
            tests={sanityChecks}
            onStatusChange={this.onStatusChange}
          />
        </Col>
      </div>
    );
  }
});
