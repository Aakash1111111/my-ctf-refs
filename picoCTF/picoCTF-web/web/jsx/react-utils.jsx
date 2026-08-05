const { Tooltip } = ReactBootstrap;
const { OverlayTrigger } = ReactBootstrap;
const { Input } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { Panel } = ReactBootstrap;
const { ListGroup } = ReactBootstrap;
const { ListGroupItem } = ReactBootstrap;
const { Glyphicon } = ReactBootstrap;

const { update } = React.addons;

const Hint = React.createClass({
  propTypes: {
    text: React.PropTypes.string.isRequired,
    id: React.PropTypes.string.isRequired
  },

  render() {
    const tooltip = <Tooltip id={this.props.id}>{this.props.text}</Tooltip>;
    return (
      <OverlayTrigger placement="top" overlay={tooltip}>
        <Glyphicon
          className="pad"
          glyph="question-sign"
          style={{ fontSize: "0.8em" }}
        />
      </OverlayTrigger>
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

const EmailWhitelist = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  getInitialState() {
    return {};
  },

  propTypes: {
    pushUpdates: React.PropTypes.func.isRequired,
    emails: React.PropTypes.array.isRequired
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
        <form onSubmit={this.addEmailDomain}>
          <Row>
            <Input
              type="text"
              addonBefore="@ Domain"
              valueLink={this.linkState("emailDomain")}
            />
          </Row>
          <Row>
            {this.props.emails.length > 0
              ? this.createItemDisplay()
              : emptyItemDisplay}
          </Row>
        </form>
      </div>
    );
  }
});

const FormEntry = React.createClass({
  propTypes: {
    name: React.PropTypes.string.isRequired,
    entry: React.PropTypes.object.isRequired,
    description: React.PropTypes.string
  },

  render() {
    let hint;
    if (this.props.description) {
      hint = <Hint id="email-hint" text={this.props.description} />;
    } else {
      hint = "";
    }

    return (
      <Row>
        <Col md={4}>
          <h4 className="pull-left">
            {hint}
            {this.props.name}
          </h4>
        </Col>
        <Col md={8}>{this.props.entry}</Col>
      </Row>
    );
  }
});

const TextEntry = React.createClass({
  propTypes: {
    name: React.PropTypes.string.isRequired,
    type: React.PropTypes.string.isRequired,
    onChange: React.PropTypes.func.isRequired,
    placeholder: React.PropTypes.string
  },

  render() {
    const input = (
      <Input
        className="form-control"
        type={this.props.type}
        value={this.props.value}
        onChange={this.props.onChange}
        placeholder={this.props.placeholder}
      />
    );
    return <FormEntry {...Object.assign({ entry: input }, this.props)} />;
  }
});

const BooleanEntry = React.createClass({
  propTypes: {
    name: React.PropTypes.string.isRequired,
    value: React.PropTypes.bool.isRequired,
    onChange: React.PropTypes.func.isRequired
  },

  render() {
    const button = (
      <Button bsSize="xsmall" onClick={this.props.onChange}>
        {this.props.value ? "Enabled" : "Disabled"}
      </Button>
    );
    return <FormEntry {...Object.assign({ entry: button }, this.props)} />;
  }
});

const TimeEntry = React.createClass({
  propTypes: {
    name: React.PropTypes.string.isRequired,
    value: React.PropTypes.string.isRequired,
    onChange: React.PropTypes.func.isRequired
  },

  componentDidMount() {
    const date = new Date(this.props.value);
    const node = ReactDOM.findDOMNode(this.refs.datetimepicker);
    return $(node)
      .datetimepicker({
        defaultDate: date,
        inline: true,
        sideBySide: true
      })
      .on("dp.change", e => {
        return this.props.onChange(e.date.toDate().getTime());
      });
  },

  render() {
    const timepicker = (
      <Panel>
        {" "}
        <div ref="datetimepicker" />{" "}
      </Panel>
    );
    return <FormEntry {...Object.assign({ entry: timepicker }, this.props)} />;
  }
});

const OptionEntry = React.createClass({
  propTypes: {
    name: React.PropTypes.string.isRequired,
    value: React.PropTypes.string.isRequired,
    options: React.PropTypes.array.isRequired,
    onChange: React.PropTypes.func.isRequired
  },

  render() {
    const buttons = _.map(this.props.options, option => {
      const onClick = e => {
        return this.props.onChange(option);
      };

      const buttonClass = option === this.props.value ? "active" : "";
      return (
        <Button key={option} onClick={onClick} className={buttonClass}>
          {option}
        </Button>
      );
    });

    const buttonGroup = <ButtonGroup>{buttons}</ButtonGroup>;

    return <FormEntry {...Object.assign({ entry: buttonGroup }, this.props)} />;
  }
});
