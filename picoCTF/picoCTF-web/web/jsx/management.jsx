const { Tabs } = ReactBootstrap;
const { Tab } = ReactBootstrap;

const ManagementTabs = React.createClass({
  getInitialState() {
    let tab = window.location.hash.substring(1);
    if (tab === "") {
      tab = "problems";
    }

    return {
      bundles: [],
      problems: [],
      submissions: [],
      exceptions: [],
      tabKey: tab
    };
  },

  onProblemChange() {
    apiCall(
      "GET",
      "/api/v1/problems?unlocked_only=false&include_disabled=true"
    ).done(data => {
      this.setState(
        React.addons.update(this.state, { problems: { $set: data } })
      );
    });

    apiCall("GET", "/api/v1/bundles").done(data => {
      this.setState(
        React.addons.update(this.state, { bundles: { $set: data } })
      );
    });

    //This could take awhile. However, it may
    //introduce a minor race condition with
    //get_all_problems
    apiCall("GET", "/api/v1/stats/submissions").done(data => {
      this.setState(
        React.addons.update(this.state, { submissions: { $set: data } })
      );
    });
  },

  onExceptionModification() {
    apiCall("GET", "/api/v1/exceptions").done(data => {
      this.setState(
        React.addons.update(this.state, { exceptions: { $set: data } })
      );
    });
  },

  componentDidMount() {
    // Formatting hack
    $("#main-content>.container").addClass("container-fluid").removeClass("container");
  },

  componentWillMount() {
    this.onProblemChange();
    this.onExceptionModification();
  },

  onTabSelect(tab) {
    this.setState(
      React.addons.update(this.state, {
        tabKey: {
          $set: tab
        }
      })
    );

    window.location.hash = `#${tab}`;

    if (tab === "problems") {
      this.onProblemChange();
    }

    if (tab === "exceptions") {
      this.onExceptionModification();
    }
  },

  render() {
    return (
      <Tabs activeKey={this.state.tabKey} onSelect={this.onTabSelect}>
        <Tab eventKey="problems" title="Manage Problems">
          <ProblemTab
            problems={this.state.problems}
            onProblemChange={this.onProblemChange}
            bundles={this.state.bundles}
            submissions={this.state.submissions}
          />
        </Tab>
        <Tab eventKey="users" title="Manage Users">
          <UserSearchTab />
        </Tab>
        <Tab eventKey="exceptions" title="Exceptions">
          <ExceptionTab
            onExceptionModification={this.onExceptionModification}
            exceptions={this.state.exceptions}
          />
        </Tab>
        <Tab eventKey="shell-servers" title="Shell Server">
          <ShellServerTab />
        </Tab>
        <Tab eventKey="configuration" title="Configuration">
          <SettingsTab />
        </Tab>
      </Tabs>
    );
  }
});

$(() =>
  ReactDOM.render(
    <ManagementTabs />,
    document.getElementById("management-tabs")
  )
);
