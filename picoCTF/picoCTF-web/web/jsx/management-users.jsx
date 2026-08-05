const { Button } = ReactBootstrap;
const { ButtonToolbar } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Well } = ReactBootstrap;

const User = React.createClass({
  getInitialState() {
    return {
      deletion_reason: null
    };
  },

  updateReason(e) {
    this.setState(
      update(this.state, {
        $set: {
          deletion_reason: e.target.value
        }
      })
    );
  },

  disableAccount(e) {
    e.preventDefault();
    let reason = this.state.deletion_reason;
    let refresh = this.props.onRefresh;
    let uid = this.props.uid;
    confirmDialog(
      `User ${this.props.username} will be deleted for: ${reason ? reason : "Not specified"}`,
      "Delete Account Confirmation",
      "Delete Account",
      "Cancel",
      function() {
        const data = {
          reason: reason
        };
        apiCall(
          "POST",
          `/api/v1/users/${uid}/delete`,
          data
        )
          .done(data => {
            apiNotify({ status: 1, message: "Account successfully deleted!" });
            refresh();
          })
          .fail(jqXHR => {
            apiNotify({ status: 0, message: jqXHR.responseJSON.message });
          });
      },
      () => {
        //pass;
      }
    );
  },

  render() {
    if(this.props.disable_reason){
      return(
        <Panel>
          <Row>
            <Col md={3}>
              <h4>
                User Name:
              </h4>
            </Col>
            <Col md={9}>
              <h4>
                {this.props.username}
              </h4>
            </Col>
          </Row>
          <Row>
            <Col md={3}>
              <h4>
                Deletion Reason:
              </h4>
            </Col>
            <Col md={9}>
              <h4>
                {this.props.disable_reason}
              </h4>
            </Col>
          </Row>
        </Panel>
      );
    } else {
      return(
        <Panel>
          <Row>
            <Col md={3}>
              <h4>
                User Name:<br/>
                Email:<br/>
                Country:<br/>
                User Type:<br/>
                Age:<br/>
                Verified:<br/>
              </h4>
            </Col>
            <Col md={9}>
              <h4>
                {this.props.username}<br/>
                {this.props.email}<br/>
                {this.props.country}<br/>
                {this.props.usertype}<br/>
                {this.props.demo.age}<br/>
                {this.props.verified ? "Yes" : "No"}<br/>
              </h4>
            </Col>
          </Row>
          <Row>
            <Col md={10}>
              <TextEntry
                name="Deletion Reason"
                type="text"
                value={this.state.deletion_reason}
                onChange={this.updateReason}
                description="Optional reason for account deletion"
              />
            </Col>
            <Col md={2}>
              <ButtonToolbar>
                <Button onClick={this.disableAccount} className="btn-danger">Delete</Button>
              </ButtonToolbar>
            </Col>
          </Row>
        </Panel>
      );
    }
  }
});

const UserList = React.createClass({
  propTypes: {
    users: React.PropTypes.array.isRequired
  },

  render() {
    if (this.props.users.length === 0) {
      return (
        <h4>
          No matching users.
        </h4>
      );
    }

    const userComponents = this.props.users.map((user, i) => {
      return (
        <Col key={i} xs={12}>
          <User
            {...Object.assign(
              {
                onRefresh: this.props.onRefresh
              },
              user
            )}
          />
        </Col>
      );
    });

    return <Row>{userComponents}</Row>;
  }
});

const UserSearchTab = React.createClass({
  getInitialState() {
    return {
      search_field: "Email",
      search_query: "",
      users: []
    };
  },

  updateSearchField(value) {
    this.setState(
      update(this.state, {
        $set: {
          search_field: value
        }
      })
    );
  },

  updateSearchQuery(e) {
    this.setState(
      update(this.state, {
        $set: {
          search_query: e.target.value
        }
      })
    );
  },

  pushUpdates(makeChange) {
    let pushData = {
      field: this.state.search_field,
      query: this.state.search_query
    };

    if (typeof makeChange === "function") {
      pushData = makeChange(pushData);
    }

    apiCall("POST", "/api/v1/users/search", pushData)
      .done(data => {
        this.setState(
          React.addons.update(this.state, { users: { $set: data } })
        );
      })
      .fail(jqXHR => {
        apiNotify({ status: 0, message: jqXHR.responseJSON.message });
        this.setState(
          React.addons.update(this.state, { users: { $set: [] } })
        );
      });
  },

  render() {
    const searchFieldDescription = "The field to be searched in the user database";
    const searchQueryDescription = "The text of the query";

    return (
      <Well>
        <Row>
          <Col sm={8} smOffset={2}>
            <h3>User Search</h3>
            <OptionEntry
              name="Field"
              value={this.state.search_field}
              options={["Email", "Parent Email", "User Name"]}
              onChange={this.updateSearchField}
              description={searchFieldDescription}
            />
            <TextEntry
              name="Query"
              type="text"
              value={this.state.search_query}
              onChange={this.updateSearchQuery}
              description={searchQueryDescription}
              placeholder="email@example.com"
            />
            <Row>
              <Col sm={8} smOffset={4}>
                <div className="text-center">
                  <ButtonToolbar>
                    <Button onClick={this.pushUpdates}>Search</Button>
                  </ButtonToolbar>
                </div>
              </Col>
            </Row>
            <Row>
              <Col>
                <UserList
                  users={this.state.users}
                  onRefresh={this.pushUpdates}
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </Well>
    );
  }
});
