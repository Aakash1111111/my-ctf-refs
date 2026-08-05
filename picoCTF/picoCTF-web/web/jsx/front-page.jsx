const { Input } = ReactBootstrap;
const { Row } = ReactBootstrap;
const { Col } = ReactBootstrap;
const { Button } = ReactBootstrap;
const { Panel } = ReactBootstrap;
const { Glyphicon } = ReactBootstrap;
const { ButtonInput } = ReactBootstrap;
const { ButtonGroup } = ReactBootstrap;
const { Alert } = ReactBootstrap;

const { update } = React.addons;

const Recaptcha = ReactRecaptcha;

const LoginForm = React.createClass({
  render() {
    let q;
    const userGlyph = <Glyphicon glyph="user" />;
    const lockGlyph = <Glyphicon glyph="lock" />;

    const formButton = this.props.status === "Login" ? (q = "'") : undefined; //My syntax highlighting can't handle literal quotes in jsx. :(
    if (this.props.status === "Reset") {
      return (
        <Panel>
          <form onSubmit={this.props.onPasswordReset}>
            <p>
              <i>A password reset link will be sent the user{q}s email.</i>
            </p>
            <Input
              type="text"
              name="username"
              valueLink={this.props.username}
              addonBefore={userGlyph}
              placeholder="Username"
              required={true}
            />
            <div style={{ height: "70px" }} />
            <Row>
              <Col md={6}>
                <ButtonInput type="submit">Reset Password</ButtonInput>
              </Col>
              <Col md={6}>
                <span className="pull-right pad">
                  Go back to{" "}
                  <a onClick={this.props.setPage.bind(null, "Login")}>Login</a>.
                </span>
              </Col>
            </Row>
          </form>
        </Panel>
      );
    } else {
      const showGroupMessage = () => {
        return (
          <Alert bsStyle="info">
            You are registering as a member of <strong>{this.props.groupName}</strong>
          </Alert>
        );
      };

      const showEmailFilter = () => {
        return (
          <p className="alert alert-info">
            You can register provided you have an email for one of these domains:
            <strong>{this.props.emailFilter.join(", ")}</strong>
          </p>
        );
      };

      const generateRecaptcha = () => {
        if (this.props.reCAPTCHA_public_key) {
          return (
            <Recaptcha
              sitekey={this.props.reCAPTCHA_public_key}
              verifyCallback={this.props.onRecaptchaSuccess}
              expiredCallback={this.props.onRecaptchaExpire}
              render="explicit"
            />
          );
        }
      };

      // Toggle input fields according to user type
      const showOrHide = (prop, inputName) => {
        const inputs = {
          firstname: false,
          lastname: false,
          url: false,
          grade: false,
          teacherlevel: false,
          subjectstaught: false,
          schoolcountry: false,
          residencecountry: true,
          affiliation: true,
          zipcode: false,
          studentOnly: false,
          teacherOnly: false,
          referrer: false,
          gender: true
        };
        switch (this.props.usertype.value) {
          case "student":
            inputs.grade = true;
            inputs.schoolcountry = true;
            inputs.zipcode = true;
            inputs.studentOnly = true;
            inputs.referrer = true;
            inputs.url = true;
            break;
          case "college":
            inputs.schoolcountry = true;
            inputs.zipcode = true;
            inputs.url = true;
            break;
          case "teacher":
            inputs.teacherlevel = true;
            inputs.subjectstaught = true;
            inputs.schoolcountry = true;
            inputs.zipcode = true;
            inputs.teacherOnly = true;
            inputs.referrer = true;
            inputs.url = true;
            break;
          case "other":
            inputs.url = true;
            break;
          default:
            inputs.affiliation = false;
        }
        const show = inputs[inputName];
        if (prop === "class") {
          if (show) {
            return "show";
          } else {
            return "hide";
          }
        } else if (prop === "disabled") {
          if (show) {
            return false;
          } else {
            return true;
          }
        }
      };

      const generateCountries = function() {
        const countryList = {
          "United States": "US",
          Canada: "CA",
          Afghanistan: "AF",
          Albania: "AL",
          Algeria: "DZ",
          Andorra: "AD",
          Angola: "AO",
          "Antigua and Barbuda": "AG",
          Argentina: "AR",
          Armenia: "AM",
          Aruba: "AW",
          Australia: "AU",
          Austria: "AT",
          Azerbaijan: "AZ",
          "Bahamas, The": "BS",
          Bahrain: "BH",
          Bangladesh: "BD",
          Barbados: "BB",
          Belarus: "BY",
          Belgium: "BE",
          Belize: "BZ",
          Benin: "BJ",
          Bhutan: "BT",
          Bolivia: "BO",
          "Bosnia and Herzegovina": "BA",
          Botswana: "BW",
          Brazil: "BR",
          Brunei: "BN",
          Bulgaria: "BG",
          "Burkina Faso": "BF",
          Burma: "MM",
          Burundi: "BI",
          "Cabo Verde": "CV",
          Cambodia: "KH",
          Cameroon: "CM",
          "Central African Republic": "CF",
          Chad: "TD",
          Chile: "CL",
          China: "CN",
          Colombia: "CO",
          Comoros: "KM",
          "Congo (Brazzaville)": "CG",
          "Congo (Kinshasa)": "CD",
          "Costa Rica": "CR",
          "Côte d'Ivoire": "CI",
          Croatia: "HR",
          Cuba: "CU",
          Curacao: "CW",
          Cyprus: "CY",
          Czechia: "CZ",
          Denmark: "DK",
          Djibouti: "DJ",
          Dominica: "DM",
          "Dominican Republic": "DO",
          Ecuador: "EC",
          Egypt: "EG",
          "El Salvador": "SV",
          "Equatorial Guinea": "GQ",
          Eritrea: "ER",
          Estonia: "EE",
          Eswatini: "SZ",
          Ethiopia: "ET",
          Fiji: "FJ",
          Finland: "FI",
          France: "FR",
          Gabon: "GA",
          "Gambia, The": "GM",
          Georgia: "GE",
          Germany: "DE",
          Ghana: "GH",
          Greece: "GR",
          Grenada: "GD",
          Guatemala: "GT",
          Guinea: "GN",
          "Guinea-Bissau": "GW",
          Guyana: "GY",
          Haiti: "HT",
          "Holy See": "VA",
          Honduras: "HN",
          "Hong Kong": "HK",
          Hungary: "HU",
          Iceland: "IS",
          India: "IN",
          Indonesia: "ID",
          Iran: "IR",
          Iraq: "IQ",
          Ireland: "IE",
          Israel: "IL",
          Italy: "IT",
          Jamaica: "JM",
          Japan: "JP",
          Jordan: "JO",
          Kazakhstan: "KZ",
          Kenya: "KE",
          Kiribati: "KI",
          "Korea, North": "KP",
          "Korea, South": "KR",
          Kosovo: "XK",
          Kuwait: "KW",
          Kyrgyzstan: "KG",
          Laos: "LA",
          Latvia: "LV",
          Lebanon: "LB",
          Lesotho: "LS",
          Liberia: "LR",
          Libya: "LY",
          Liechtenstein: "LI",
          Lithuania: "LT",
          Luxembourg: "LU",
          Macau: "MO",
          Macedonia: "MK",
          Madagascar: "MG",
          Malawi: "MW",
          Malaysia: "MY",
          Maldives: "MV",
          Mali: "ML",
          Malta: "MT",
          "Marshall Islands": "MH",
          Mauritania: "MR",
          Mauritius: "MU",
          Mexico: "MX",
          Micronesia: "FM",
          Moldova: "MD",
          Monaco: "MC",
          Mongolia: "MN",
          Montenegro: "ME",
          Morocco: "MA",
          Mozambique: "MZ",
          Namibia: "NA",
          Nauru: "NR",
          Nepal: "NP",
          Netherlands: "NL",
          "New Zealand": "NZ",
          Nicaragua: "NI",
          Niger: "NE",
          Nigeria: "NG",
          Norway: "NO",
          Oman: "OM",
          Pakistan: "PK",
          Palau: "PW",
          Palestine: "PS",
          Panama: "PA",
          "Papua New Guinea": "PG",
          Paraguay: "PY",
          Peru: "PE",
          Philippines: "PH",
          Poland: "PL",
          Portugal: "PT",
          Qatar: "QA",
          Romania: "RO",
          Russia: "RU",
          Rwanda: "RW",
          "Saint Kitts and Nevis": "KN",
          "Saint Lucia": "LC",
          "Saint Vincent and the Grenadines": "VC",
          Samoa: "WS",
          "San Marino": "SM",
          "Sao Tome and Principe": "ST",
          "Saudi Arabia": "SA",
          Senegal: "SN",
          Serbia: "RS",
          Seychelles: "SC",
          "Sierra Leone": "SL",
          Singapore: "SG",
          "Sint Maarten": "SX",
          Slovakia: "SK",
          Slovenia: "SI",
          "Solomon Islands": "SB",
          Somalia: "SO",
          "South Africa": "ZA",
          "South Sudan": "SS",
          Spain: "ES",
          "Sri Lanka": "LK",
          Sudan: "SD",
          Suriname: "SR",
          Sweden: "SE",
          Switzerland: "CH",
          Syria: "SY",
          Taiwan: "TW",
          Tajikistan: "TJ",
          Tanzania: "TZ",
          Thailand: "TH",
          "Timor-Leste": "TL",
          Togo: "TG",
          Tonga: "TO",
          "Trinidad and Tobago": "TT",
          Tunisia: "TN",
          Turkey: "TR",
          Turkmenistan: "TM",
          Tuvalu: "TV",
          Uganda: "UG",
          Ukraine: "UA",
          "United Arab Emirates": "AE",
          "United Kingdom": "GB",
          Uruguay: "UY",
          Uzbekistan: "UZ",
          Vanuatu: "VU",
          Venezuela: "VE",
          Vietnam: "VN",
          Yemen: "YE",
          Zambia: "ZM",
          Zimbabwe: "ZW"
        };

        const result = [];
        let i = 0;
        for (let country in countryList) {
          const abbrev = countryList[country];
          result.push(<option key={i} value={abbrev}>{country}</option>);
          i++;
        }
        return result;
      };

      const registrationForm =
        this.props.status === "Register" ? (
          <div>
            <Row>
              <div>
                {this.props.groupName.length > 0 ? (
                  showGroupMessage()
                ) : (
                  <span />
                )}
                {this.props.emailFilter.length > 0 && !this.props.rid ? (
                  showEmailFilter()
                ) : (
                  <span />
                )}
                <br />
              </div>
              <Col md={6} className={showOrHide("class", "firstname")}>
                <Input
                  type="text"
                  id="firstname"
                  valueLink={this.props.firstname}
                  label="First Name"
                  placeholder="Jane"
                />
              </Col>
              <Col md={6} className={showOrHide("class", "lastname")}>
                <Input
                  type="text"
                  id="lastname"
                  valueLink={this.props.lastname}
                  label="Last Name"
                  placeholder="Doe"
                />
              </Col>
              <Col md={12}>
                <Input
                  type="email"
                  name="email"
                  id="email"
                  valueLink={this.props.email}
                  label="E-mail *"
                  placeholder="email@example.com"
                  required={true}
                />
              </Col>
            </Row>
            <Row>
              <Col md={12} className={showOrHide("class", "residencecountry")}>
                <Input
                  type="select"
                  name="residencecountry"
                  id="residencecountry"
                  defaultValue=""
                  valueLink={this.props.residencecountry}
                  label="Country/Region of Residence *"
                  placeholder="Country of Residence"
                  required={true}
                  autoComplete="off"
                >
                  <option value="" disabled={true}>
                    -Select-
                  </option>
                  {generateCountries()}
                </Input>
              </Col>
            </Row>
            <Row>
              <Col md={12}>
                <Input
                  type="select"
                  name="usertype"
                  id="usertype"
                  defaultValue=""
                  label="Status *"
                  required={true}
                  valueLink={this.props.usertype}
                >
                  <option value="" disabled={true}>
                    -Select Category-
                  </option>
                  <option value="student">Middle/High School Student</option>
                  <option value="teacher">Teacher/Instructor</option>
                  <option value="college">College Student</option>
                  <option value="other">Other</option>
                </Input>
              </Col>
            </Row>
            <Row>
              <Col md={6} className={showOrHide("class", "affiliation")}>
                <Input
                  type="text"
                  name="affiliation"
                  id="affiliation"
                  valueLink={this.props.affiliation}
                  label={
                    this.props.usertype.value === "other"
                      ? "Organization Name *"
                      : "School Name *"
                  }
                  placeholder="Example School, Pittsburgh, PA"
                  maxLength="50"
                  required={true}
                />
                <p className="alert alert-warning">Your school or organization name may be visible to other users.</p>
              </Col>
              <Col md={6} className={showOrHide("class", "url")}>
                <Input
                  type="text"
                  name="url"
                  disabled={showOrHide("disabled", "url")}
                  id="url"
                  valueLink={this.props.url}
                  label={
                    this.props.usertype.value === "other"
                      ? "Organization URL (optional)"
                      : "School URL (optional)"
                  }
                  placeholder={
                    this.props.usertype.value === "other"
                      ? "Organization URL"
                      : "School URL"
                  }
                />
              </Col>
            </Row>
            <Row>
              <Col md={6} className={showOrHide("class", "grade")}>
                <Input
                  type="number"
                  min="1"
                  max="12"
                  name="grade"
                  disabled={showOrHide("disabled", "grade")}
                  id="grade"
                  valueLink={this.props.grade}
                  label="Your Current Grade/Year (1-12) *"
                  placeholder="Your Current Grade/Year"
                  required={true}
                />
              </Col>
              <Col md={6} className={showOrHide("class", "teacherlevel")}>
                <label>I teach *</label>
                <Input
                  type="checkbox"
                  checkedLink={this.props.teacher_middleschool}
                  label="Middle School"
                />
                <Input
                  type="checkbox"
                  checkedLink={this.props.teacher_highschool}
                  label="High School"
                />
                <Input
                  type="checkbox"
                  checkedLink={this.props.teacher_afterschoolclub}
                  label="After School or Club"
                />
                <Input
                  type="checkbox"
                  checkedLink={this.props.teacher_homeschool}
                  label="Home School"
                />
              </Col>
              <Col md={6} className={showOrHide("class", "subjectstaught")}>
                <Input
                  type="text"
                  name="subjectstaught"
                  disabled={showOrHide("disabled", "subjectstaught")}
                  id="subjectstaught"
                  valueLink={this.props.subjectstaught}
                  label="Subjects Taught *"
                  required={true}
                />
              </Col>
            </Row>
            <Row>
              <Col md={6} className={showOrHide("class", "zipcode")}>
                <Input
                  type="text"
                  name="zipcode"
                  disabled={showOrHide("disabled", "zipcode")}
                  id="zipcode"
                  valueLink={this.props.zipcode}
                  label="School Zip Code/Postal Code *"
                  placeholder="School Zipcode/Postal Code"
                  required={true}
                />
              </Col>
              <Col md={6} className={showOrHide("class", "schoolcountry")}>
                <Input
                  type="select"
                  name="schoolcountry"
                  disabled={showOrHide("disabled", "schoolcountry")}
                  defaultValue=""
                  id="schoolcountry"
                  valueLink={this.props.schoolcountry}
                  label="School Country *"
                  required={true}
                  autoComplete="off"
                >
                  <option value="" disabled={true}>
                    -Select-
                  </option>
                  {generateCountries()}
                </Input>
              </Col>
            </Row>
            <Row className={showOrHide("class", "referrer")}>
              <Col md={12}>
                <Input
                  className={showOrHide("disabled", "referrer")}
                  type="select"
                  name="referrer"
                  defaultValue=""
                  id="referrer"
                  label="How did you hear about picoCTF?"
                  valueLink={this.props.referrer}
                >
                  <option value="" disabled={true}>
                    -Select-
                  </option>
                  <option value="socialmedia">Social Media</option>
                  <option
                    className={showOrHide("class", "studentOnly")}
                    value="friends"
                  >
                    Friends
                  </option>
                  <option
                    className={showOrHide("class", "studentOnly")}
                    value="teacher"
                  >
                    Teacher
                  </option>
                  <option
                    className={showOrHide("class", "teacherOnly")}
                    value="students"
                  >
                    Students
                  </option>
                  <option
                    className={showOrHide("class", "teacherOnly")}
                    value="colleagues_groupemail"
                  >
                    Colleagues or group email
                  </option>
                </Input>
              </Col>
            </Row>
            <Row className={showOrHide("class", "gender")}>
              <Col md={12}>
                <Input
                  type="select"
                  id="gender"
                  name="gender"
                  defaultValue=""
                  label="Which gender identity do you most identify with?"
                  valueLink={this.props.gender}
                >
                  <option value="">-Select-</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="nb/gf">Non-Binary/Gender-Fluid</option>
                  <option value="nl/no">Not Listed/Prefer not to answer</option>
                </Input>
              </Col>
            </Row>
            <Row>
              <Col md={12}>
                <Input
                  type="select"
                  name="age"
                  id="age"
                  defaultValue=""
                  label="What is your age? *"
                  valueLink={this.props.age}
                  required={true}
                >
                  <option value="">-Select-</option>
                  <option value="13-17">
                    I am between 13 and 17 years of age
                  </option>
                  <option value="18+">I am 18 years of age or older</option>
                </Input>
              </Col>
            </Row>
            <Row className={this.props.age.value === "13-17" ? "show" : "hide"}>
              <Col md={12}>
                <p className="help-block">
Parent or legal guardian must insert contact email address.  By inserting email address and finalizing
registration, parent/legal guardian is hereby consenting to their child’s registration under the Terms of
 Use, Privacy Statement and any applicable Competition Rules.</p>
                <Input
                  type="email"
                  name="parentemail"
                  disabled={this.props.age.value === "13-17" ? false : true}
                  id="parentemail"
                  valueLink={this.props.parentemail}
                  label="Parent's E-mail *"
                  required={true}
                  placeholder="email@example.com"
                />
              </Col>
            </Row>
            <Row>
              <Col md={8}>{generateRecaptcha()}</Col>
              <Col md={4} className="text-right">
                <ButtonInput className="btn-primary" type="submit">
                  Register
                </ButtonInput>
              </Col>
            </Row>
          </div>
        ) : (
          <span />
        );
      return (
        <Panel>
          <form
            key={this.props.status}
            onSubmit={
              this.props.status === "Login"
                ? this.props.onLogin
                : this.props.onRegistration
            }
          >
            <Input
              type="text"
              id="username"
              valueLink={this.props.username}
              addonBefore={userGlyph}
              label="Username"
              required={true}
            />
            <p
              className={this.props.status === "Login" ? "hide" : "alert alert-warning"}
            >{`Your username may be visible to other users.
Do not include your real name or any other personal information.`}</p>
            <Input
              type="password"
              id="password"
              valueLink={this.props.password}
              addonBefore={lockGlyph}
              label="Password"
              required={true}
            />
            <Row>
              <Col md={6}>
                {this.props.status === "Register" ? (
                  <span className="pad">
                    Go back to{" "}
                    <a onClick={this.props.setPage.bind(null, "Login")}>
                      Login
                    </a>
                    .
                  </span>
                ) : (
                  <span>
                    <Button type="submit">Login</Button>
                    <Button
                      id="set-register"
                      onClick={this.props.setPage.bind(null, "Register")}
                    >
                      Register
                    </Button>
                  </span>
                )}
              </Col>
              <Col md={6}>
                <a
                  className="pad"
                  onClick={this.props.setPage.bind(null, "Reset")}
                >
                  Need to reset your password?
                </a>
              </Col>
            </Row>
            {registrationForm}
          </form>
        </Panel>
      );
    }
  }
});

const TeamManagementForm = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  getInitialState() {
    return {
      team_name: "",
      team_password: ""
    };
  },

  onTeamRegistration(e) {
    e.preventDefault();
    if (!this.state.team_name || !this.state.team_password) {
      apiNotify({
        status: 0,
        message: "Invalid team name or password."
      });
    } else {
      const data = {
        team_name: this.state.team_name,
        team_password: this.state.team_password
      };
      apiCall("POST", "/api/v1/teams", data, "Team", "CreateTeamOnReg")
        .done(data => (document.location.href = "/profile"))
        .fail(jqXHR =>
          apiNotify({ status: 0, message: jqXHR.responseJSON.message })
        );
    }
  },

  onTeamJoin(e) {
    e.preventDefault();
    const data = {
      team_name: this.state.team_name,
      team_password: this.state.team_password
    };
    apiCall("POST", "/api/v1/team/join", data, "Team", "JoinTeamOnReg")
      .done(data => (document.location.href = "/profile"))
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  render() {
    const towerGlyph = <Glyphicon glyph="tower" />;
    const lockGlyph = <Glyphicon glyph="lock" />;

    return (
      <Panel>
        <p className="alert alert-warning">Your team name may be visible to other users. Do not include your real name or any other personal information.
          Also, to avoid confusion on the scoreboard, you may not create a team that shares the same name as an existing user.</p>
        <form onSubmit={this.onTeamJoin}>
          <Input type="text" valueLink={this.linkState("team_name")} addonBefore={towerGlyph} label="Team Name" required/>
          <Input type="password" valueLink={this.linkState("team_password")} addonBefore={lockGlyph} label="Team Password" required/>
          <Col md={6}>
            <span> <Button type="submit">Join Team</Button>
              <Button onClick={this.onTeamRegistration}>Register Team</Button>
            </span>
          </Col>
          <Col md={6}>
            <a href="#" onClick={() => document.location.href = "/profile"}>Play as an individual.</a>
          </Col>
        </form>
      </Panel>
    );
  }
});

const AuthPanel = React.createClass({
  mixins: [React.addons.LinkedStateMixin],
  getInitialState() {
    const params = $.deparam($.param.fragment());

    return {
      page: "Login",
      settings: {},
      gid: params.g,
      rid: params.r,
      status: params.status,
      groupName: "",
      captcha: "",
      regStats: {}
    };
  },

  componentWillMount() {
    if (this.state.status === "verified") {
      gtag('event', 'Verification', {
        'event_category': 'Registration',
        'event_label': 'Success'
      });
      apiNotify({
        status: 1,
        message: "Your account has been successfully verified. Please login."
      });
    } else if (this.state.status === "verification_error") {
      apiNotify({
        status: 0,
        message: "Invalid verification code. Please contact an administrator."
      });
    }
    apiCall("GET", "/api/v1/settings").done(data => {
      this.setState({ settings: data });
      if (this.state.gid) {
        apiCall("GET", `/api/v1/groups/${this.state.gid}`).done(data => {
          this.setState(
            update(this.state, {
              groupName: { $set: data.name },
              affiliation: { $set: data.name },
              settings: { $merge: data.settings },
              page: { $set: "Register" }
            })
          );
        });
      }
    });

    apiCall("GET", "/api/v1/stats/registration").done(data => {
      this.setState(update(this.state, { regStats: { $set: data } }));
    });
  },

  onRegistration(e) {
    e.preventDefault();

    if (this.state.settings.enable_captcha && this.state.captcha === "") {
      apiNotify({ status: 0, message: "ReCAPTCHA required." });
      return;
    }

    const form = {};
    form.gid = this.state.gid;
    form.rid = this.state.rid;
    form.username = this.state.username;
    form.password = this.state.password;
    form.firstname = this.state.firstname;
    form.lastname = this.state.lastname;
    form.email = this.state.email;
    form.affiliation = this.state.affiliation;
    form.usertype = this.state.usertype;
    form.demo = {};

    for (let k in this.state) {
      const v = this.state[k];
      if (k.substr(0, 5) === "demo_") {
        form.demo[k.substr(5)] = v;
      }
    }

    if (["student", "teacher"].includes(this.state.usertype)) {
      form.country = form.demo.schoolcountry;
    } else {
      form.country = form.demo.residencecountry;
    }

    form["g-recaptcha-response"] = this.state.captcha;

    apiCall("POST", "/api/v1/users", form, "Registration", "Form")
      .done(data => {
        const verificationAlert = {
          status: 1,
          message:
            "You have been sent a verification email. You will need to complete this step before logging in."
        };

        const successAlert = {
          status: 1,
          message: `User ${this.state.username} registered successfully!`
        };

        if (this.state.settings.email_verification && !this.state.rid) {
          apiNotify(verificationAlert);
          this.setPage("Login");
          if (this.state.settings.max_team_size > 1) {
            document.location.hash = "#team-builder";
          }
        } else {
          apiCall("POST", "/api/v1/user/login", {
            username: this.state.username,
            password: this.state.password
          }, "User", "LoginOnReg")
            .done(loginData => {
              apiCall("GET", "/api/v1/user")
                .done(userData => {
                  if (userData.teacher) {
                    apiNotify(successAlert, "/classroom");
                  } else if (this.state.settings.max_team_size > 1) {
                    apiNotify(successAlert);
                    this.setPage("Team Management");
                  } else {
                    apiNotify(successAlert, "/profile");
                  }
                })
                .fail(jqXHR =>
                  apiNotify({ status: 0, message: jqXHR.responseJSON.message })
                );
            })
            .fail(jqXHR =>
              apiNotify({ status: 0, message: jqXHR.responseJSON.message })
            );
        }
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  onPasswordReset(e) {
    e.preventDefault();
    apiCall("POST", "/api/v1/user/reset_password/request", {
      username: this.state.username
    }, "Authentication", "ResetPasswordRequest")
      .done(resp => {
        apiNotify({
          status: 1,
          message:
            "A password reset link has been sent to the email address provided during registration."
        });
        this.setPage("Login");
      })
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  onLogin(e) {
    e.preventDefault();
    apiCall("POST", "/api/v1/user/login", {
      username: this.state.username,
      password: this.state.password
    }, "Authentication", "Login")
      .done(() =>
        // Get teacher status
        apiCall("GET", "/api/v1/user").done(data => {
          if (document.location.hash === "#team-builder" && !data.teacher) {
            this.setPage("Team Management");
          } else {
            if (data.teacher) {
              document.location.href = "/classroom";
            } else {
              document.location.href = "/profile";
            }
          }
        })
      )
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  setPage(page) {
    this.setState(update(this.state, { page: { $set: page } }));
  },

  onRecaptchaSuccess(captcha) {
    this.setState(update(this.state, { captcha: { $set: captcha } }));
  },

  onRecaptchaExpire() {
    this.setState(update(this.state, { captcha: { $set: "" } }));
  },

  render() {
    const links = {
      username: this.linkState("username"),
      password: this.linkState("password"),
      lastname: this.linkState("lastname"),
      firstname: this.linkState("firstname"),
      email: this.linkState("email"),
      affiliation: this.linkState("affiliation"),
      usertype: this.linkState("usertype"),
      age: this.linkState("demo_age"),
      url: this.linkState("demo_url"),
      residencecountry: this.linkState("demo_residencecountry"),
      schoolcountry: this.linkState("demo_schoolcountry"),
      zipcode: this.linkState("demo_zipcode"),
      grade: this.linkState("demo_grade"),
      referrer: this.linkState("demo_referrer"),
      gender: this.linkState("demo_gender"),
      teacher_middleschool: this.linkState("demo_teacher_middleschool"),
      teacher_highschool: this.linkState("demo_teacher_highscool"),
      teacher_afterschoolclub: this.linkState("demo_teacher_afterschool"),
      teacher_homeschool: this.linkState("demo_teacher_homeschool"),
      subjectstaught: this.linkState("demo_subjectstaught"),
      parentemail: this.linkState("demo_parentemail")
    };

    const showRegStats = () => {
      if (this.state.regStats) {
        return (
          <Panel>
            <h4>
              <strong>Registration Statistics</strong>
            </h4>
            <p>
              <strong>{this.state.regStats.users}</strong> users have
              registered,<strong> {this.state.regStats.teamed_users} </strong>
              of which have formed<strong> {this.state.regStats.teams} </strong>teams.
              <br />
              <strong>{this.state.regStats.groups} </strong>
              classrooms have been created by <strong>{this.state.regStats.teachers}</strong> teachers.
            </p>
          </Panel>
        );
      }
    };

    if (this.state.page === "Team Management") {
      return (
        <div>
          <Row>
            <Col md={6} mdOffset={3}>
              <TeamManagementForm />
            </Col>
          </Row>
        </div>
      );
    } else {
      return (
        <div>
          <Row>
            <Col md={6} mdOffset={3}>
              <LoginForm
                {...Object.assign(
                  {
                    setPage: this.setPage,
                    onRecaptchaSuccess: this.onRecaptchaSuccess,
                    onRecaptchaExpire: this.onRecaptchaExpire,
                    status: this.state.page,
                    reCAPTCHA_public_key: this.state.settings
                      .reCAPTCHA_public_key,
                    onRegistration: this.onRegistration,
                    onLogin: this.onLogin,
                    onPasswordReset: this.onPasswordReset,
                    emailFilter: this.state.settings.email_filter,
                    groupName: this.state.groupName,
                    rid: this.state.rid,
                    gid: this.state.gid
                  },
                  links
                )}
              />
              {showRegStats()}
            </Col>
          </Row>
        </div>
      );
    }
  }
});

$(function() {
  redirectIfLoggedIn();
  ReactDOM.render(<AuthPanel />, document.getElementById("auth-box"));
});
