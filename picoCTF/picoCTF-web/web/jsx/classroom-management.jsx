const { Input } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { ButtonGroup } = ReactBootstrap;
const { Panel } = ReactBootstrap;
const { ListGroup } = ReactBootstrap;
const { ListGroupItem } = ReactBootstrap;
const { Glyphicon } = ReactBootstrap;
const { Tabs } = ReactBootstrap;
const { Tab } = ReactBootstrap;

const { update } = React.addons;

const MemberManagementItem = React.createClass({
  removeTeam() {
    const data = {
      team_id: this.props.tid
    };
    apiCall("POST", `/api/v1/groups/${this.props.gid}/remove_team`, data,
      "Group", "RemoveMember")
      .done(data => {
        apiNotify({
          status: 1,
          message: "Team has successfully left the classroom."
        });
        this.props.refresh();
      })
      .fail(jqXHR => {
        apiNotify({ status: 0, message: jqXHR.responseJSON.message });
      });
  },

  elevateTeam() {
    const data = {
      team_id: this.props.tid
    };
    apiCall("POST", `/api/v1/groups/${this.props.gid}/elevate_team`, data,
      "Group", "ElevateTeacher")
      .done(data => {
        apiNotify({
          status: 1,
          message: "Team has been elevated to teacher role."
        });
        this.props.refresh();
      })
      .fail(jqXHR => {
        apiNotify({ status: 0, message: jqXHR.responseJSON.message });
      });
  },

  render() {
    return (
      <ListGroupItem>
        <Row className="row">
          <Col xs={2}>
            <Button bsStyle={this.props.isTeacher ? 'success' : 'primary'} className="btn-sq">
              <Glyphicon glyph="user" bsSize="large" />
            </Button>
          </Col>
          <Col xs={6}>
            <h4>{this.props.team_name}</h4>
            <p>
              <strong>Affiliation:</strong> {this.props.affiliation}
            </p>
          </Col>
          <Col xs={4}>
            <ButtonGroup vertical={true}>
              {this.props.tid !== this.props.owner &&
                <Button onClick={this.removeTeam}>Remove {this.props.isTeacher ? 'Teacher' : 'User/Team'}</Button>
              }
              {this.props.isTeacher === false && this.props.members[0].usertype === 'teacher' &&
                <Button onClick={this.elevateTeam}>Promote to Teacher</Button>
              }
            </ButtonGroup>
          </Col>
        </Row>
      </ListGroupItem>
    );
  }
});

const MemberInvitePanel = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  propTypes: {
    gid: React.PropTypes.string.isRequired
  },

  getInitialState() {
    return { role: "member" };
  },

  inviteUser(e) {
    e.preventDefault();
    const data = {
      email: this.state.email,
      as_teacher: this.state.role === "teacher"
    };
    apiCall("POST", `/api/v1/groups/${this.props.gid}/invite`, data,
      "Group", "EmailInvite")
      .done(data => {
        apiNotify({ status: 1, message: "Email invitation has been sent." });
        this.setState(update(this.state, { $set: { email: "" } }));
        this.props.refresh();
      })
      .fail(jqXHR => {
        apiNotify({ status: 0, message: jqXHR.responseJSON.message });
      });
  },

  render() {
    return (
      <Panel>
        <form onSubmit={this.inviteUser}>
          <Col xs={8}>
            <Input
              type="email"
              label="E-mail"
              valueLink={this.linkState("email")}
            />
          </Col>
          <Col xs={4}>
            <Input
              type="select"
              label="Role"
              placeholder="Member"
              valueLink={this.linkState("role")}
            >
              <option value="member">Member</option>
              <option value="teacher">Teacher</option>
            </Input>
          </Col>
          <Col xs={4}>
            <Button onClick={this.inviteUser}>Invite User</Button>
          </Col>
        </form>
      </Panel>
    );
  }
});

const BatchRegistrationPanel = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  propTypes: {
    gid: React.PropTypes.string.isRequired
  },

  handleFileUpload(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append("csv", this.refs.fileUpload.getInputDOMNode().files[0]);
    const params = {
      method: "POST",
      url: `/api/v1/groups/${this.props.gid}/batch_registration`,
      data: formData,
      cache: false,
      contentType: false,
      processData: false
    };
    $.ajax(params)
      .done(data => {
        gtag('event', 'BatchRegistration', {
          'event_category': 'Group',
          'event_label': 'Success'
        });
        let csv_content = "data:text/csv;charset=utf-8," + atob(data.as_csv);
        let encoded_uri = encodeURI(csv_content);

        let response_html =
          '<div class="panel panel-success batch-registration-response"><div class="panel-heading"><h4>Accounts successfully created!</h4>' +
          "<p>You have been prompted to download an updated CSV containing usernames and passwords for your students' accounts.</p>" +
          "<p>Make sure to save this file, as it will not available after leaving this page.</p>" +
          '<a class="btn btn-default" id="batch-credentials-download" href="' + encoded_uri + '" download="registered_accounts.csv">Redownload Account Credentials</a>' +
          "</div></div>"
        $(".batch-registration-response").remove();
        $("#batch-registration-panel").append(response_html).promise()
          .then(function() {
            // Automatically attempt to download account credentials
            $("#batch-credentials-download")[0].click()
          });
        this.props.refresh();
      })
      .fail(jqXHR => {
        gtag('event', 'BatchRegistration', {
          'event_category': 'Group',
          'event_label': 'Failure'
        });
        if (jqXHR.responseJSON !== undefined) {
          // If the error response comes from Flask
          if (typeof jqXHR.responseJSON.message === "object") {
            // If the error is an object of validation errors
            const errors = jqXHR.responseJSON.message;
            let response_html =
              '<div class="panel panel-danger batch-registration-response"><div class="panel-heading"><h4>Errors found in CSV.</h4>' +
              "<p>Please resolve the issues below and resubmit:</p>";
            for (let row_num in errors) {
              const row = errors[row_num];
              response_html += `<p><strong>Row ${parseInt(row_num) +
                1}:</strong></p><ul>`;
              for (let field in row) {
                const err_messages = row[field];
                for (let err_message of err_messages) {
                  if (field === "_schema") {
                    response_html += `<li>${_.escape(err_message)}</li>`;
                  } else {
                    response_html += `<li>${_.escape(field)}: ${_.escape(
                      err_message
                    )}</li>`;
                  }
                }
              }
              response_html += "</ul>";
            }
            $(".batch-registration-response").remove();
            $("#batch-registration-panel").append(response_html);
          } else {
            // Otherwise, assume a normal error message
            apiNotify({ status: 0, message: jqXHR.responseJSON.message });
            return;
          }
        } else {
          // If the response contains only a status code (e.g. from nginx)
          apiNotify({ status: 0, message: jqXHR.statusText });
          return;
        }
      });
  },

  render() {
    return (
      <Panel id="batch-registration-panel">
        <Row>
          <Col xs={12}>
            <p>
              Batch-register students into this classroom by uploading a CSV file
              containing student demographic information.
            </p>
            <p>
            Usernames and passwords will be automatically generated.
            </p>
          </Col>
        </Row>
        <Row>
          <Col xs={6}>
            <Button href="/files/batch_registration_template.csv">
              Download Template
            </Button>
          </Col>
          <Col xs={6}>
            <form>
              <Input
                type="file"
                label="Upload CSV"
                accept=".csv"
                ref="fileUpload"
              />
              <Input type="submit" onClick={this.handleFileUpload} />
            </form>
          </Col>
        </Row>
      </Panel>
    );
  }
});

const MemberManagement = React.createClass({
  render() {
    let memberList = (this.props.memberInformation === undefined) ? [] : this.props.memberInformation;
    let teacherList = (this.props.teacherInformation === undefined) ? [] : this.props.teacherInformation;
    const studentInformation = (
      <ListGroup>
        {memberList.map((member, i) => {
          return (
            <MemberManagementItem
              {...Object.assign(
                { key: i, gid: this.props.gid, refresh: this.props.refresh, isTeacher: false, owner: this.props.owner },
                member
              )}
            />
          );
        })}
      </ListGroup>
    );
    const teacherInformation = (
      <ListGroup>
        {teacherList.map((member, i) => {
          return (
            <MemberManagementItem
              {...Object.assign(
                { key: i, gid: this.props.gid, refresh: this.props.refresh, isTeacher: true, owner: this.props.owner },
                member
              )}
            />
          );
        })}
      </ListGroup>
    );

    return (
      <Panel>
        <h4>User Management</h4>
        <MemberInvitePanel gid={this.props.gid} refresh={this.props.refresh} />
        <h4>Batch Registration</h4>
        <BatchRegistrationPanel
          gid={this.props.gid}
          refresh={this.props.refresh}
        />
        {teacherList.length > 0 &&
          <h4>Teachers</h4>
        }
        {teacherInformation}
        {memberList.length > 0 &&
          <h4>Student Teams</h4>
        }
        {studentInformation}
      </Panel>
    );
  }
});

const GroupManagement = React.createClass({
  getInitialState() {
    return {
      name: "",
      owner: "",
      settings: {
        email_filter: [],
        hidden: false
      },
      member_information: undefined,
      teacher_information: undefined,
      current_user: {}
    };
  },

  componentDidMount() {
    this.refreshSettings();
  },

  refreshSettings() {
    apiCall("GET", `/api/v1/groups/${this.props.gid}`).done(data => {
      this.setState({ settings: data.settings });
      this.setState({ owner: data.owner });
      if (data.teachers) {
        this.setState({ teacher_information: data.teachers });
      }
      if (data.members) {
        this.setState({ member_information: data.members });
      }
    });
  },

  pushUpdates(modifier) {
    const data = this.state;

    if (modifier) {
      data.settings = modifier(data.settings);
    }

    apiCall("PATCH", `/api/v1/groups/${this.props.gid}`, {
      settings: data.settings
    }, "Group", "ChangeSettings")
      .done(data => {
        apiNotify({
          status: 1,
          message: "Classroom settings changed successfully."
        });
        this.refreshSettings();
      })
      .fail(jqXHR => {
        apiNotify({ status: 0, message: jqXHR.responseJSON.message });
      });
  },

  render() {
    let contents;
    if (this.state.member_information === undefined && this.state.teacher_information === undefined ) {
      contents = (
        <div className="row" style={{ marginTop: "10px" }}>
          <Col sm={12}>
            <p>An existing teacher must promote your account before you can modify this classroom.</p>
          </Col>
        </div>
      );
    } else {
      contents = (
        <div className="row" style={{ marginTop: "10px" }}>
          <Col sm={6}>
            <MemberManagement
              teacherInformation={this.state.teacher_information}
              currentUser={this.state.current_user}
              memberInformation={this.state.member_information}
              gid={this.props.gid}
              refresh={this.refreshSettings}
              owner={this.state.owner}
            />
          </Col>
          <Col sm={6}>
            <GroupOptions
              pushUpdates={this.pushUpdates}
              settings={this.state.settings}
              gid={this.props.gid}
            />
            <GroupEmailWhitelist
              emails={this.state.settings.email_filter}
              pushUpdates={this.pushUpdates}
              gid={this.props.gid}
            />
          </Col>
        </div>
      );
  }
  return contents;
  }
});

const GroupOptions = React.createClass({
  propTypes: {
    settings: React.PropTypes.object.isRequired,
    pushUpdates: React.PropTypes.func.isRequired,
    gid: React.PropTypes.string.isRequired
  },

  promptGroupHide() {
    return window.confirmDialog(
      "This option will hide all members of this classroom from public or competition scoreboards. This change is irrevocable; you will not be able to change this back later.",
      "Hidden Classroom Change",
      "Okay",
      "Cancel",
      function() {
        this.props.pushUpdates(data =>
          update(data, { hidden: { $set: true } })
        );
      }.bind(this)
    );
  },

  render() {
    let hiddenGroupDisplay;
    if (this.props.settings.hidden) {
      hiddenGroupDisplay = (
        <p>
          This classroom is <b>hidden</b> from the general scoreboard.
        </p>
      );
    } else {
      hiddenGroupDisplay = (
        <p>
          <span>This classroom is <b>visible</b> on the scoreboard. Click </span>
          <a href="#" onClick={this.promptGroupHide}>here</a>
          <span> to hide it.</span>
        </p>
      );
    }

    return (
      <Panel>
        <h4>Classroom Options</h4>
        <Panel>
          <form>{hiddenGroupDisplay}</form>
        </Panel>
      </Panel>
    );
  }
});

const EmailWhitelistItem = React.createClass({
  propTypes: {
    email: React.PropTypes.string.isRequired,
    pushUpdates: React.PropTypes.func.isRequired
  },

  render() {
    const removeEmail = this.props.pushUpdates.bind(null, data => {
      return update(data, {
        email_filter: { $apply: _.partial(_.without, _, this.props.email) }
      });
    });

    return (
      <ListGroupItem>
        *@
        {this.props.email}
        <span className="pull-right">
          <Glyphicon glyph="remove" onClick={removeEmail} />
        </span>
      </ListGroupItem>
    );
  }
});

const GroupEmailWhitelist = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  getInitialState() {
    return {};
  },

  propTypes: {
    pushUpdates: React.PropTypes.func.isRequired,
    emails: React.PropTypes.array.isRequired,
    gid: React.PropTypes.string.isRequired
  },

  addEmailDomain(e) {
    // It would probably make more sense to this kind of validation server side.
    // However, it can't cause any real issue being here.

    e.preventDefault();

    if (_.indexOf(this.props.emails, this.state.emailDomain) !== -1) {
      apiNotify({
        status: 0,
        message: "This email domain has already been whitelisted."
      });
    } else if (_.indexOf(this.state.emailDomain, "@") !== -1) {
      apiNotify({
        status: 0,
        message:
          "You should not include '@'. I want the email domain that follows '@'."
      });
    } else if (_.indexOf(this.state.emailDomain, ".") === -1) {
      apiNotify({
        status: 0,
        message:
          "Your email domain did not include a '.' as I expected. Please make sure this is an email domain."
      });
    } else {
      this.props.pushUpdates(data => {
        this.setState({ emailDomain: "" });
        return update(data, {
          email_filter: { $push: [this.state.emailDomain] }
        });
      });
    }
  },

  createItemDisplay() {
    return (
      <ListGroup>
        {this.props.emails.map((email, i) => {
          return (
            <EmailWhitelistItem
              key={i}
              email={email}
              pushUpdates={this.props.pushUpdates}
            />
          );
        })}
      </ListGroup>
    );
  },

  render() {
    const emptyItemDisplay = (
      <p>
        The whitelist is current empty. All emails will be accepted during
        registration.
      </p>
    );

    return (
      <div>
        <h4>Email Domain Whitelist</h4>
        <Panel>
          <form onSubmit={this.addEmailDomain}>
            <Input
              type="text"
              addonBefore="@ Domain"
              valueLink={this.linkState("emailDomain")}
            />
            {this.props.emails.length > 0
              ? this.createItemDisplay()
              : emptyItemDisplay}
          </form>
        </Panel>
      </div>
    );
  }
});

const TeacherManagement = React.createClass({
  getInitialState() {
    return {
      groups: [],
      tabKey: 0
    };
  },

  onTabSelect(tab) {
    this.setState(update(this.state, { tabKey: { $set: tab } }));
  },

  componentDidMount() {
    addAjaxListener("teacherManagementState", "/api/v1/groups", data => {
      this.setState(update(this.state, { groups: { $set: data } }));
    });
  },

  render() {
    if (this.state.groups.length === 0) {
      return (<p className="alert alert-warning">Please create a classroom first.</p>);
    } else {
      return (
        <Tabs activeKey={this.state.tabKey} onSelect={this.onTabSelect}>
          {this.state.groups.map((group, i) => {
            return (
              <Tab
                eventKey={i}
                key={i}
                title={group.name}
                className="tab-pane-outline"
              >
                <GroupManagement key={group.name} gid={group.gid}/>
              </Tab>
            );
          })}
        </Tabs>
      );
    }
  }
});
$(function() {
  ReactDOM.render(
    <TeacherManagement />,
    document.getElementById("group-management")
  );

  $(document).on(
    "shown.bs.tab",
    'a[href="#group-management-tab"]',
    function() {
      ReactDOM.unmountComponentAtNode(
        document.getElementById("group-management")
      );
      ReactDOM.render(
        <TeacherManagement />,
        document.getElementById("group-management")
      );
    }
  );
});
