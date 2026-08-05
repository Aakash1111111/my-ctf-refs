const { ListGroupItem } = ReactBootstrap;
const { ListGroup } = ReactBootstrap;
const { Accordion } = ReactBootstrap;
const { Panel } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { Glyphicon } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Badge } = ReactBootstrap;

const ExceptionTab = React.createClass({
  onDelete(exception) {
    apiCall("DELETE", `/api/v1/exceptions/${exception.id}`).done(
      this.props.onExceptionModification()
    );
  },

  createRequestInfo(request) {
    if (request) {
      return (
        <div>
          <h4>Browser information</h4>
          <p>
            Version: {request.browser} {request.browser_version}
          </p>
          <p>Platform: {request.platform}</p>
          <p>Address: {request.ip}</p>
        </div>
      );
    } else {
      return <p>No request information available.</p>;
    }
  },

  createUserInfo(user) {
    if (user) {
      return (
        <div>
          <h4>User information</h4>
          <p>Username: {user.username}</p>
          <p>Email: {user.email}</p>
          <p>Team: {user.team_name}</p>
        </div>
      );
    } else {
      return <p>No user information available.</p>;
    }
  },

  createInfoDisplay(exception) {
    return (
      <div>
        <h3>Exception:</h3>
        <pre>{exception.trace}</pre>
        <Col xs={6}> {this.createRequestInfo(exception.request)} </Col>
        <Col xs={6}> {this.createUserInfo(exception.user)} </Col>
      </div>
    );
  },

  createExceptionItem(exception, i) {
    const time = <small>{new Date(exception.time).toUTCString()}</small>;

    const deleteButton = (
      <Glyphicon onClick={this.onDelete.bind(this, exception)} glyph="remove" />
    );

    const occurencesBadge = <Badge>{exception.count}</Badge>;

    const apiDescription = exception.request ? (
      <span>
        {exception.request.api_endpoint_method}{" "}
        <b>{exception.request.api_endpoint}</b>
      </span>
    ) : (
      <span>Internal Exception</span>
    );

    const exceptionHeader = (
      <div>
        {apiDescription}
        <div className="pull-right">
          {occurencesBadge} {time} {deleteButton}
        </div>
      </div>
    );

    return (
      <Panel bsStyle="default" eventKey={i} key={i} header={exceptionHeader}>
        {this.createInfoDisplay(exception)}
      </Panel>
    );
  },

  render() {
    if (this.props.exceptions.length > 0) {
      const groupedExceptions = _.groupBy(
        this.props.exceptions,
        exception => exception.trace
      );

      const uniqueExceptions = _.map(groupedExceptions, function(
        exceptions,
        commonTrace
      ) {
        const exception = _.first(exceptions);
        exception.count = exceptions.length;
        return exception;
      });

      const exceptionList = uniqueExceptions.map(this.createExceptionItem);
      const exceptionDisplay = (
        <Accordion defaultActiveKey={0}>{exceptionList}</Accordion>
      );

      return (
        <div>
          <h3>
            Displaying the {this.props.exceptions.length} most recent
            exceptions.
          </h3>
          {exceptionDisplay}
        </div>
      );
    } else {
      return (
        <div>
          <h3>No exceptions to display.</h3>
        </div>
      );
    }
  }
});
