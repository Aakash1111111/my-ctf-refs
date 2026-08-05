const { Well } = ReactBootstrap;
const { ButtonGroup } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { Grid } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;

const { update } = React.addons;

// The settings fields need to use the linked state mixin to avoid a lot of boilerplate.

const GeneralTab = React.createClass({
  propTypes: {
    refresh: React.PropTypes.func.isRequired,
    settings: React.PropTypes.object.isRequired
  },

  getInitialState() {
    return this.props.settings;
  },

  toggleFeedbackEnabled() {
    this.setState(
      update(this.state, {
        $set: {
          enable_feedback: !this.state.enable_feedback
        }
      })
    );
  },

  updateCompetitionName(e) {
    this.setState(
      update(this.state, {
        $set: {
          competition_name: e.target.value
        }
      })
    );
  },

  updateCompetitionURL(e) {
    this.setState(
      update(this.state, {
        $set: {
          competition_url: e.target.value
        }
      })
    );
  },

  updateStartTime(value) {
    this.setState(
      update(this.state, {
        $set: {
          start_time: value
        }
      })
    );
  },

  updateEndTime(value) {
    this.setState(
      update(this.state, {
        $set: {
          end_time: value
        }
      })
    );
  },

  updateMaxTeamSize(e) {
    this.setState(
      update(this.state, {
        $set: {
          max_team_size: parseInt(e.target.value)
        }
      })
    );
  },

  updateUsernameBlacklist(e) {
    this.setState(
      update(this.state, {
        $set: {
          username_blacklist: e.target.value.split("\n")
        }
      })
    );
  },

  updateMaxBatchRegistrations(e) {
    this.setState(
      update(this.state, {
        $set: {
          max_batch_registrations: parseInt(e.target.value)
        }
      })
    );
  },

  updateGroupLimit(e) {
    this.setState(
      update(this.state, {
        $set: {
          group_limit: parseInt(e.target.value)
        }
      })
    )
  },

  toggleRateLimiting() {
    this.setState(
      update(this.state, {
        $set: {
          enable_rate_limiting: !this.state.enable_rate_limiting
        }
      })
    );
  },

  pushUpdates() {
    const data = {
      enable_feedback: this.state.enable_feedback,
      competition_name: this.state.competition_name,
      competition_url: this.state.competition_url,
      start_time: new Date(this.state.start_time).toUTCString(),
      end_time: new Date(this.state.end_time).toUTCString(),
      max_team_size: this.state.max_team_size,
      username_blacklist: this.state.username_blacklist,
      max_batch_registrations: this.state.max_batch_registrations,
      enable_rate_limiting: this.state.enable_rate_limiting,
      group_limit: this.state.group_limit,
    };
    apiCall("PATCH", "/api/v1/settings", data)
      .done(data => {
        apiNotify({ status: 1, message: "Settings updated successfully" });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  render() {
    const feedbackDescription = `Users will be able to review problems when this feature is enabled. The ratings will be available to you \
on the Problem tab.`;
    const competitionNameDescription = "The name of the competition.";
    const competitionURLDescription = `The base URL for the competition website. This must be set in order for users to reset \
their passwords.`;
    const startTimeDescription =
      "Before the competition has started, users will be able to register without viewing the problems.";
    const endTimeDescription =
      "After the competition has ended, users will no longer be able to submit keys to the challenges.";
    const maxTeamSizeDescription =
      "Maximum number of users that can join a single team.";
    const usernameBlacklistDescription =
      "Usernames that are unavailable for registration.";
    const maxBatchRegistrationsDescription =
      "Maximum number of student accounts a teacher can create via batch registration.";
    const groupLimitDescription =
      "Maximum number of classrooms that a teacher account can create.";
    const rateLimitingDescription =
      "Whether to enable rate limiting for certain endpoints.";

    return (
      <Well>
        <BooleanEntry
          name="Receive Problem Feedback"
          value={this.state.enable_feedback}
          onChange={this.toggleFeedbackEnabled}
          description={feedbackDescription}
        />
        <TextEntry
          name="Competition Name"
          value={this.state.competition_name}
          type="text"
          onChange={this.updateCompetitionName}
          description={competitionNameDescription}
        />
        <TextEntry
          name="Competition URL"
          value={this.state.competition_url}
          type="text"
          onChange={this.updateCompetitionURL}
          description={competitionURLDescription}
        />
        <TimeEntry
          name="Competition Start Time"
          value={this.state.start_time}
          onChange={this.updateStartTime}
          description={startTimeDescription}
        />
        <TimeEntry
          name="Competition End Time"
          value={this.state.end_time}
          onChange={this.updateEndTime}
          description={endTimeDescription}
        />
        <TextEntry
          name="Max Team Size"
          value={this.state.max_team_size}
          type="number"
          onChange={this.updateMaxTeamSize}
          description={maxTeamSizeDescription}
        />
        <TextEntry
          name="Username Blacklist"
          value={this.state.username_blacklist.join("\n")}
          type="textarea"
          onChange={this.updateUsernameBlacklist}
          description={usernameBlacklistDescription}
        />
        <TextEntry
          name="Max Batch Registrations per Teacher"
          value={this.state.max_batch_registrations}
          type="number"
          onChange={this.updateMaxBatchRegistrations}
          description={maxBatchRegistrationsDescription}
        />
        <TextEntry
          name="Classroom Limit per Teacher"
          value={this.state.group_limit}
          type="number"
          onChange={this.updateGroupLimit}
          description={groupLimitDescription}
        />
        <BooleanEntry
          name="Enable Rate Limiting"
          value={this.state.enable_rate_limiting}
          onChange={this.toggleRateLimiting}
          description={rateLimitingDescription}
        />
        <Row>
          <div className="text-center">
            <ButtonToolbar>
              <Button onClick={this.pushUpdates}>Update</Button>
            </ButtonToolbar>
          </div>
        </Row>
      </Well>
    );
  }
});

const EmailTab = React.createClass({
  propTypes: {
    refresh: React.PropTypes.func.isRequired,
    emailSettings: React.PropTypes.object.isRequired,
    emailFilterSettings: React.PropTypes.array.isRequired
  },

  getInitialState() {
    const settings = this.props.emailSettings;
    settings.email_filter = this.props.emailFilterSettings;
    return settings;
  },

  updateSMTPUrl(e) {
    this.setState(
      update(this.state, {
        $set: {
          smtp_url: e.target.value
        }
      })
    );
  },

  updateSMTPSecurity(e) {
    this.setState(
      update(this.state, { $set: { smtp_security: e.target.value } })
    );
  },

  updateSMTPPort(e) {
    this.setState(
      update(this.state, {
        $set: {
          smtp_port: parseInt(e.target.value)
        }
      })
    );
  },

  updateUsername(e) {
    this.setState(
      update(this.state, {
        $set: {
          email_username: e.target.value
        }
      })
    );
  },

  updatePassword(e) {
    this.setState(
      update(this.state, {
        $set: {
          email_password: e.target.value
        }
      })
    );
  },

  updateFromAddr(e) {
    this.setState(
      update(this.state, {
        $set: {
          from_addr: e.target.value
        }
      })
    );
  },

  updateFromName(e) {
    this.setState(
      update(this.state, {
        $set: {
          from_name: e.target.value
        }
      })
    );
  },

  updateMaxVerificationEmails(e) {
    this.setState(
      update(this.state, {
        $set: {
          max_verification_emails: parseInt(e.target.value)
        }
      })
    );
  },

  toggleEnabled() {
    this.setState(
      update(this.state, {
        $set: {
          enable_email: !this.state.enable_email
        }
      })
    );
  },

  toggleEmailVerification() {
    this.setState(
      update(this.state, {
        $set: {
          email_verification: !this.state.email_verification
        }
      })
    );
  },

  toggleSendParentVerificationEmail() {
    this.setState(
      update(this.state, {
        $set: {
          parent_verification_email: !this.state.parent_verification_email
        }
      })
    );
  },

  pushUpdates(makeChange) {
    let pushData = {
      email: {
        enable_email: this.state.enable_email,
        email_verification: this.state.email_verification,
        max_verification_emails: this.state.max_verification_emails,
        parent_verification_email: this.state.parent_verification_email,
        smtp_url: this.state.smtp_url,
        smtp_port: this.state.smtp_port,
        email_username: this.state.email_username,
        email_password: this.state.email_password,
        from_addr: this.state.from_addr,
        from_name: this.state.from_name,
        smtp_security: this.state.smtp_security
      },
      email_filter: this.state.email_filter
    };

    if (typeof makeChange === "function") {
      pushData = makeChange(pushData);
    }

    apiCall("PATCH", "/api/v1/settings", pushData)
      .done(data => {
        apiNotify({ status: 1, message: "Settings updated successfully" });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  render() {
    let securityOptions;
    const emailDescription =
      "Emails must be sent in order for users to reset their passwords.";
    const emailVerificationDescription =
      "Mandate email verification for new users";
    const MaxVerificationEmailsDescription =
      "The number of times a verification email can be resent before the account is locked";
    const parentEmailVerificationDescription =
      "Send an email to the parent's email address (if provided) upon registration";
    const SMTPDescription = "The URL of the STMP server you are using";
    const SMTPPortDescription = "The port of the running SMTP server";
    const usernameDescription = "The username of the email account";
    const passwordDescription = "The password of the email account";
    const fromAddressDescription =
      "The address that the emails should be sent from";
    const fromNameDescription = "The name to use for sending emails";
    const SMTPSecurityDescription = "Security employed by the SMTP server";

    // This is pretty bad. Much of this file needs reworked.
    if (this.state.smtp_security === "TLS") {
      securityOptions = (
        <Input type="select" onChange={this.updateSMTPSecurity} key="TLS">
          <option value="TLS">TLS</option>
          <option value="SSL">SSL</option>
        </Input>
      );
    } else {
      securityOptions = (
        <Input type="select" onChange={this.updateSMTPSecurity} key="SSL">
          <option value="SSL">SSL</option>
          <option value="TLS">TLS</option>
        </Input>
      );
    }

    const SMTPSecuritySelect = (
      <Row>
        <Col md={4}>
          <h4 className="pull-left">
            <Hint id="smtp-hint" text={SMTPSecurityDescription} />
            Security
          </h4>
        </Col>
        <Col md={8}>{securityOptions}</Col>
      </Row>
    );

    return (
      <Well>
        <Row>
          <Col xs={6}>
            <BooleanEntry
              name="Send Emails"
              value={this.state.enable_email}
              onChange={this.toggleEnabled}
              description={emailDescription}
            />
            <TextEntry
              name="SMTP URL"
              value={this.state.smtp_url}
              type="text"
              onChange={this.updateSMTPUrl}
              description={SMTPDescription}
            />
            <TextEntry
              name="SMTP Port"
              value={this.state.smtp_port}
              type="number"
              onChange={this.updateSMTPPort}
              description={SMTPPortDescription}
            />
            <TextEntry
              name="Email Username"
              value={this.state.email_username}
              type="text"
              onChange={this.updateUsername}
              description={usernameDescription}
            />
            <TextEntry
              name="Email Password"
              value={this.state.email_password}
              type="password"
              onChange={this.updatePassword}
              description={passwordDescription}
            />
            <TextEntry
              name="From Address"
              value={this.state.from_addr}
              type="text"
              onChange={this.updateFromAddr}
              description={fromAddressDescription}
            />
            <TextEntry
              name="From Name"
              value={this.state.from_name}
              type="text"
              onChange={this.updateFromName}
              description={fromNameDescription}
            />
            <BooleanEntry
              name="Email Verification"
              value={this.state.email_verification}
              onChange={this.toggleEmailVerification}
              description={emailVerificationDescription}
            />
            <TextEntry
              name="Max Verification Emails"
              value={this.state.max_verification_emails}
              type="number"
              onChange={this.updateMaxVerificationEmails}
              description={MaxVerificationEmailsDescription}
            />
            <BooleanEntry
              name="Parent Verification Email"
              value={this.state.parent_verification_email}
              onChange={this.toggleSendParentVerificationEmail}
              description={parentEmailVerificationDescription}
            />
            {SMTPSecuritySelect}
            <Row>
              <div className="text-center">
                <ButtonToolbar>
                  <Button onClick={this.pushUpdates}>Update</Button>
                </ButtonToolbar>
              </div>
            </Row>
          </Col>
          <Col xs={6}>
            <EmailWhitelist
              pushUpdates={this.pushUpdates}
              emails={this.props.emailFilterSettings}
            />
          </Col>
        </Row>
      </Well>
    );
  }
});

const ShardingTab = React.createClass({
  propTypes: {
    refresh: React.PropTypes.func.isRequired,
    shardingSettings: React.PropTypes.object.isRequired
  },

  getInitialState() {
    return this.props.shardingSettings;
  },

  updateSteps(e) {
    this.setState(
      update(this.state, {
        $set: {
          steps: e.target.value
            .replace(/, +/g, ",")
            .split(",")
            .map(Number)
        }
      })
    );
  },

  updateDefaultStepping(e) {
    this.setState(
      update(this.state, {
        $set: {
          default_stepping: parseInt(e.target.value)
        }
      })
    );
  },

  toggleSharding() {
    this.setState(
      update(this.state, {
        $set: {
          enable_sharding: !this.state.enable_sharding
        }
      })
    );
  },

  toggleLimitRange() {
    this.setState(
      update(this.state, {
        $set: {
          limit_added_range: !this.state.limit_added_range
        }
      })
    );
  },

  pushUpdates(makeChange) {
    let pushData = {
      shell_servers: {
        enable_sharding: this.state.enable_sharding,
        default_stepping: this.state.default_stepping,
        steps: this.state.steps,
        limit_added_range: this.state.limit_added_range
      }
    };

    if (typeof makeChange === "function") {
      pushData = makeChange(pushData);
    }

    apiCall("PATCH", "/api/v1/settings", pushData)
      .done(data => {
        apiNotify({ status: 1, message: "Settings updated successfully" });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  assignServerNumbers() {
    confirmDialog(
      "This will assign server_numbers to all unassigned teams. This may include teams previously defaulted to server_number 1 and already given problem instances!",
      "Assign Server Numbers Confirmation",
      "Assign Server Numbers",
      "Cancel",
      () =>
        apiCall("POST", "/api/v1/shell_servers/update_assignments", {})
          .done(data =>
            apiNotify({ status: 1, message: "Server assignments updated" })
          )
          .fail(jqXHR =>
            apiNotify({ status: 0, message: jqXHR.responseJSON.message })
          ),
      function() {}
    );
  },

  reassignServerNumbers() {
    confirmDialog(
      "This will reassign all teams. Problem instances will be randomized for any teams that change servers!",
      "Reassign Server Numbers Confirmation",
      "Reassign Server Numbers",
      "Cancel",
      () =>
        apiCall("POST", "/api/v1/shell_servers/update_assignments", {
          include_assigned: true
        })
          .done(data =>
            apiNotify({ status: 1, message: "Server assigments updated" })
          )
          .fail(jqXHR =>
            apiNotify({ status: 0, message: jqXHR.responseJSON.message })
          ),
      function() {}
    );
  },

  render() {
    const shardingDescription =
      "Sharding splits teams to different shell_servers based on stepping";
    const defaultSteppingDescription =
      "Default stepping, applied after defined steps";
    const stepsDescription =
      "Comma delimited list of stepping (e.g. '1000,1500,2000')";
    const limitRangeDescription =
      "Limit assignments to the highest added server_number";

    return (
      <Well>
        <Row>
          <Col sm={8}>
            <BooleanEntry
              name="Enable Sharding"
              value={this.state.enable_sharding}
              onChange={this.toggleSharding}
              description={shardingDescription}
            />
            <TextEntry
              name="Defined Steps"
              value={this.state.steps}
              type="text"
              onChange={this.updateSteps}
              description={stepsDescription}
            />
            <TextEntry
              name="Default Stepping"
              value={this.state.default_stepping}
              type="text"
              onChange={this.updateDefaultStepping}
              description={defaultSteppingDescription}
            />
            <BooleanEntry
              name="Limit to Added Range"
              value={this.state.limit_added_range}
              onChange={this.toggleLimitRange}
              description={limitRangeDescription}
            />
            <br />
            <Button onClick={this.assignServerNumbers}>
              Assign Server Numbers
            </Button>{" "}
             {" "}
            <Button onClick={this.reassignServerNumbers}>
              Reassign All Server Numbers
            </Button>
            <br />
            <br />
            <Row>
              <div className="text-center">
                <ButtonToolbar>
                  <Button onClick={this.pushUpdates}>Update</Button>
                </ButtonToolbar>
              </div>
            </Row>
          </Col>
        </Row>
      </Well>
    );
  }
});

const CaptchaTab = React.createClass({
  propTypes: {
    refresh: React.PropTypes.func.isRequired,
    captchaSettings: React.PropTypes.object.isRequired
  },

  getInitialState() {
    return this.props.captchaSettings;
  },

  toggleEnableCaptcha() {
    this.setState(
      update(this.state, {
        $set: {
          enable_captcha: !this.state.enable_captcha
        }
      })
    );
  },

  updateCaptchaURL(e) {
    this.setState(
      update(this.state, {
        $set: {
          captcha_url: e.target.value
        }
      })
    );
  },

  updateRecaptchaPublicKey(e) {
    this.setState(
      update(this.state, {
        $set: {
          reCAPTCHA_public_key: e.target.value
        }
      })
    );
  },

  updateRecaptchaPrivateKey(e) {
    this.setState(
      update(this.state, {
        $set: {
          reCAPTCHA_private_key: e.target.value
        }
      })
    );
  },

  pushUpdates(makeChange) {
    let pushData = {
      captcha: {
        enable_captcha: this.state.enable_captcha,
        captcha_url: this.state.captcha_url,
        reCAPTCHA_public_key: this.state.reCAPTCHA_public_key,
        reCAPTCHA_private_key: this.state.reCAPTCHA_private_key
      }
    };

    if (typeof makeChange === "function") {
      pushData = makeChange(pushData);
    }

    apiCall("PATCH", "/api/v1/settings", pushData)
      .done(data => {
        apiNotify({ status: 1, message: "Settings updated successfully" });
        this.props.refresh();
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  render() {
    const enableCaptchaDescription =
      "Require users to solve a CAPTCHA when registering an account. Does not apply to invited or batch-registered accounts";
    const captchaURLDescription = "URL to request a CAPTCHA";
    const reCaptchaPublicKeyDescription = "Public key for the reCAPTCHA API";
    const reCaptchaPrivateKeyDescription = "Private key for the reCAPTCHA API";

    return (
      <Well>
        <Row>
          <Col sm={8}>
            <BooleanEntry
              name="Enable CAPTCHA"
              value={this.state.enable_captcha}
              onChange={this.toggleEnableCaptcha}
              description={enableCaptchaDescription}
            />
            <TextEntry
              name="CAPTCHA URL"
              type="text"
              value={this.state.captcha_url}
              onChange={this.updateCaptchaURL}
              description={captchaURLDescription}
            />
            <TextEntry
              name="reCAPTCHA Public Key"
              type="textarea"
              value={this.state.reCAPTCHA_public_key}
              onChange={this.updateRecaptchaPublicKey}
              description={reCaptchaPublicKeyDescription}
            />
            <TextEntry
              name="reCAPTCHA Private Key"
              type="textarea"
              value={this.state.reCAPTCHA_private_key}
              onChange={this.updateRecaptchaPrivateKey}
              description={reCaptchaPrivateKeyDescription}
            />
            <Row>
              <div className="text-center">
                <ButtonToolbar>
                  <Button onClick={this.pushUpdates}>Update</Button>
                </ButtonToolbar>
              </div>
            </Row>
          </Col>
        </Row>
      </Well>
    );
  }
});

const SettingsTab = React.createClass({
  getInitialState() {
    return {
      settings: {
        start_time: "Tue, 21 May 2019 17:59:12 GMT",
        end_time: "Mon, 27 May 2019 17:59:12 GMT",
        competition_name: "",
        competition_url: "",
        enable_feedback: true,
        max_team_size: 1,
        username_blacklist: [],
        email: {
          email_verification: false,
          parent_verification_email: false,
          max_verification_emails: 3,
          enable_email: false,
          from_addr: "",
          smtp_url: "",
          smtp_port: 0,
          email_username: "",
          email_password: "",
          from_name: ""
        },
        email_filter: [],
        shell_servers: {
          enable_sharding: false,
          default_stepping: 1,
          steps: "",
          limit_added_range: false
        },
        captcha: {
          enable_captcha: false,
          captcha_url: "",
          reCAPTCHA_public_key: "",
          reCAPTCHA_private_key: ""
        },
        max_batch_registrations: 250,
        enable_rate_limiting: true,
        group_limit: 20
      },

      tabKey: "general"
    };
  },

  onTabSelect(tab) {
    this.setState(
      update(this.state, {
        tabKey: {
          $set: tab
        }
      })
    );
  },

  refresh() {
    apiCall("GET", "/api/v1/settings").done(data => {
      this.setState(
        update(this.state, {
          $set: {
            settings: data
          }
        })
      );
    });
  },

  componentDidMount() {
    this.refresh();
  },

  render() {
    const generalSettings = {
      enable_feedback: this.state.settings.enable_feedback,
      competition_name: this.state.settings.competition_name,
      competition_url: this.state.settings.competition_url,
      start_time: this.state.settings.start_time,
      end_time: this.state.settings.end_time,
      max_team_size: this.state.settings.max_team_size,
      username_blacklist: this.state.settings.username_blacklist,
      max_batch_registrations: this.state.settings.max_batch_registrations,
      enable_rate_limiting: this.state.settings.enable_rate_limiting,
      group_limit: this.state.settings.group_limit
    };
    return (
      <Well>
        <Grid>
          <Row>
            <h4>
              {" "}
              Configure the competition settings by choosing a tab below{" "}
            </h4>
          </Row>
          <Tabs activeKey={this.state.tabKey} onSelect={this.onTabSelect}>
            <Tab eventKey="general" title="General">
              <GeneralTab
                refresh={this.refresh}
                settings={generalSettings}
                key={Math.random()}
              />
            </Tab>
            <Tab eventKey="sharding" title="Sharding">
              <ShardingTab
                refresh={this.refresh}
                shardingSettings={this.state.settings.shell_servers}
                key={Math.random()}
              />
            </Tab>
            <Tab eventKey="email" title="Email">
              <EmailTab
                refresh={this.refresh}
                emailSettings={this.state.settings.email}
                emailFilterSettings={this.state.settings.email_filter}
                key={Math.random()}
              />
            </Tab>
            <Tab eventKey="captcha" title="CAPTCHA">
              <CaptchaTab
                refresh={this.refresh}
                captchaSettings={this.state.settings.captcha}
                key={Math.random()}
              />
            </Tab>
          </Tabs>
        </Grid>
      </Well>
    );
  }
});
