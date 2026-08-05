const { Input, Row, Col, Button, Panel,
        Glyphicon, ButtonInput, ButtonGroup } = ReactBootstrap;
const { update } = React.addons;

const updatePassword = function(e) {
  e.preventDefault();
  const data = {
    current_password: $("#current-password").val(),
    new_password: $("#new-password").val(),
    new_password_confirmation: $("#new-password-confirmation").val()
  };
  apiCall(
    "POST",
    "/api/v1/user/update_password",
    data,
    "Authentication",
    "UpdatePassword"
  )
    .done(data =>
      apiNotify(
        { status: 1, message: "Your password has been successfully updated!" },
        "/profile"
      )
    )
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );
};

const resetPassword = function(e) {
  e.preventDefault();
  const data = {
    reset_token: window.location.hash.substring(1),
    new_password: $("#password-reset-form input[name=new-password]").val(),
    new_password_confirmation: $(
      "#password-reset-form input[name=new-password-confirmation]"
    ).val()
  };
  apiCall(
    "POST",
    "/api/v1/user/reset_password",
    data,
    "Authentication",
    "ResetPassword"
  )
    .done(function(data) {
      apiNotify(
        { status: 1, message: "Your password has been reset" },
        "/"
      );
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );
};

const disableAccount = function(e) {
  e.preventDefault();
  confirmDialog(
    "This will delete your account, drop you from your team, and prevent you from playing!",
    "Delete Account Confirmation",
    "Delete Account",
    "Cancel",
    function() {
      const data = {
        password: $("#disable-account-form input[name=current-password]").val()
      };
      apiCall(
        "POST",
        "/api/v1/user/disable_account",
        data,
        "Authentication",
        "DisableAccount"
      )
        .done(data =>
          apiNotify(
            { status: 1, message: "Your account has been deleted." },
            "/"
          )
        )
        .fail(jqXHR =>
          apiNotify({ status: 0, message: jqXHR.responseJSON.message })
        );
    }
  );
};

const downloadData = function(e) {
  e.preventDefault();
  apiCall("GET", "/api/v1/user/export")
    .done(data =>
      download(
        JSON.stringify(data, null, 2),
        "Account Data.txt",
        "application/json"
      )
    )
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );
};

// Should figure out how we want to share components.
const TeamManagementForm = React.createClass({
  mixins: [React.addons.LinkedStateMixin],

  getInitialState() {
    return {
      user: {},
      scoreboards: [],
      team: {},
      team_name: "",
      team_password: ""
    };
  },

  componentWillMount() {
    addAjaxListener("teamManagementFormState", "/api/v1/user", data => {
      this.setState({ user: data });
    });
    apiCall("GET", "/api/v1/team").done(data => {
      this.setState({ team: data });
    });
    apiCall("GET", "/api/v1/scoreboards").done(data => {
      this.setState({ scoreboards: data });
    });
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
      apiCall("POST", "/api/v1/teams", data, "Team", "CreateTeam")
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
    apiCall("POST", "/api/v1/team/join", data, "Team", "JoinTeam")
      .done(data => (document.location.href = "/profile"))
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  },

  toggleAllowIneligibleMembers(e) {
    e.preventDefault();
    const data = {
      allow_ineligible_members: !this.state.team.allow_ineligible_members
    };
    let dialogMsg = (this.state.team.allow_ineligible_members) ?
      "This will allow users to join your team ONLY if doing so would keep " +
      "your team ELIGIBLE for all of its current scoreboards." :
      "This will allow users to join your team even if doing so would cause " +
      "your team to become INELIGIBLE for any of its current scoreboards.";
    confirmDialog(
      dialogMsg,
      "Scoreboard Eligibility Lock",
      "Confirm",
      "Cancel",
      ()=> {
        apiCall("PATCH", "/api/v1/team", data)
          .done(response => {
            let toggleState = data.allow_ineligible_members ? 'Allow' : 'Disallow' ;
            gtag('event', 'EligibilityLock', {
              'event_category': 'Team',
              'event_label': toggleState
            });
            this.setState(update(this.state, {team: {$merge: data}}));
            apiNotify(
              {
                status: 1,
                message: "Settings updated successfully"
              }
            )
          })
          .fail(jqXHR =>
            apiNotify({status: 0, message: jqXHR.responseJSON.message})
          );
      }
    );
  },

  onTeamPasswordChange(e) {
    e.preventDefault();
    if (this.state.team_password !== this.state.confirm_team_password) {
      apiNotify({ status: 0, message: "Passwords do not match." });
    } else {
      const newpass = this.state.team_password;
      const newpass_confirm = this.state.confirm_team_password;
      confirmDialog(
        "This will change the password needed to join your team.",
        "Team Password Change Confirmation",
        "Confirm",
        "Cancel",
        function() {
          const data = {
            new_password: newpass,
            new_password_confirmation: newpass_confirm
          };
          apiCall("POST", "/api/v1/team/update_password", data, "Team", "UpdatePassword")
            .done(data =>
              apiNotify(
                {
                  status: 1,
                  message: "Your team password has been successfully updated!"
                },
                "/profile"
              )
            )
            .fail(jqXHR =>
              apiNotify({ status: 0, message: jqXHR.responseJSON.message })
            );
        }
      );
    }
  },

  removeMember(e) {
    e.preventDefault();
    apiCall("DELETE", "/api/v1/team/members/" + e.target.dataset.uid)
    .done(function() {
      document.location.href = "/profile";
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );
  },

  listMembers() {
    return this.state.team["members"].map((member, i) => (
      <li key={i} style={{marginBottom: '10px'}}>
        {member.uid == this.state.team.creator && (
          <span className="label label-default" style={{marginRight: '5px'}}>Captain</span>
          )}
        {member.username} (
        <span className="capitalize">
          {member.usertype} - {member.country}) {
            (this.state.user.uid === this.state.team['creator'] || member.uid == this.state.user.uid) && member.can_leave && (
              <Button
                style={{marginLeft: '5px'}}
                data-uid={member.uid}
                onClick={this.removeMember}
              >{member.uid === this.state.user.uid ? (this.state.user.uid === this.state.team['creator'] ? "Delete Team" : "Leave Team") : "Kick Member"}</Button>
            )}
        </span>
      </li>
    ));
  },

  listEligibleScoreboards() {
    const eligibleScoreboards = this.state.scoreboards.filter((scoreboard) =>
      this.state.team.eligibilities.indexOf(scoreboard.sid) != -1)
    const scoreboardList = eligibleScoreboards.map((scoreboard, i) =>
        <li key={i}>{scoreboard.name}</li>
    )
    return scoreboardList
  },

  renderIneligibleMemberToggle() {
    return (
      <Col className="form-group">
        <p>Currently, users are <b>{this.state.team.allow_ineligible_members ? 'allowed to join' : 'prevented from joining'}</b> your team if doing so would cause your team to become ineligible for any of its current scoreboards.</p>
        <Button onClick={this.toggleAllowIneligibleMembers}>
        {this.state.team.allow_ineligible_members ? 'Prevent Ineligible Users From Joining Team' : 'Allow Ineligible Users To Join Team'}
        </Button>
      </Col>
    )
  },

  render() {
    if (this.state.team.max_team_size > 1 && !this.state.user.teacher) {
      const towerGlyph = <Glyphicon glyph="tower" />;
      const lockGlyph = <Glyphicon glyph="lock" />;

      const teamCreated =
        this.state.user &&
        this.state.user.username !== this.state.team.team_name;
      if (teamCreated) {
        return (
          <Panel header="Team Management">
            <p>
              <strong>Team Name:</strong> {this.state.team.team_name}
            </p>
            <p>
              <strong>Members</strong> ({this.state.team.members.length}/
              {this.state.team.max_team_size}):
            </p>
            {this.state.user.uid === this.state.team.creator &&
              (<div>
                <p><i>Members who have submitted flags cannot be removed.</i></p>
                <p><i>All other members must be removed in order to delete the team.</i></p>
              </div>)}
            <ul>{this.listMembers()}</ul>
            <hr />
            <form onSubmit={this.onTeamPasswordChange}>
              <Input
                type="password"
                valueLink={this.linkState("team_password")}
                addonBefore={lockGlyph}
                label="New Team Password"
                required={true}
              />
              <Input
                type="password"
                valueLink={this.linkState("confirm_team_password")}
                addonBefore={lockGlyph}
                label="Confirm New Team Password"
                required={true}
              />
              <Button type="submit">Change Team Password</Button>
            </form>

            <hr/>
            <p><strong>Scoreboard Eligibility</strong></p>
            <p>Your team is eligible to appear on these scoreboards:</p>
            <ul>{this.listEligibleScoreboards()}</ul>
            {this.renderIneligibleMemberToggle()}
          </Panel>
        );
      } else {
        return (
          <Panel header="Team Management">
            <p className="alert alert-warning">{`Your team name may be visible to other users. Do not include your real name or any other personal information.
Also, to avoid confusion on the scoreboard, you may not create a team that shares the same name as an existing user.`}</p>
            <form onSubmit={this.onTeamJoin}>
              <Input
                type="text"
                valueLink={this.linkState("team_name")}
                addonBefore={towerGlyph}
                label="Team Name"
                required={true}
              />
              <Input
                type="password"
                valueLink={this.linkState("team_password")}
                addonBefore={lockGlyph}
                label="Team Password"
                required={true}
              />
              <Col md={6}>
                <span>
                  <Button type="submit">Join Team</Button>
                  <Button onClick={this.onTeamRegistration}>
                    Register Team
                  </Button>
                </span>
              </Col>
            </form>
          </Panel>
        );
      }
    } else {
      return <div />;
    }
  }
});

// Begin classroom panel. TODO: convert to react components

const load_group_info = () =>
  apiCall("GET", "/api/v1/groups", null, "Team", "GroupLoad")
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    )
    .done(function(data) {
      $("#group-info").html(renderGroupInformation({ data }));

      $("#join-group").on("click", group_request);
      $("#group-request-form").on("submit", join_group_request);
      $(".leave-group-span").on("click", e =>
        leave_group($(e.target).data("gid"))
      );
    });

const join_group = function(group_name, group_owner) {
  const data = { group_name: group_name, group_owner: group_owner };
  apiCall("POST", "/api/v1/team/join_group", data, "Group", "JoinGroup")
    .done(function(data) {
      apiNotify({ status: 1, message: "Successfully joined classroom" });
      load_group_info();
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );
};

const leave_group = gid =>
  apiCall(
    "GET",
    `/api/v1/groups/${gid}/remove_team`,
    null,
    "Team",
    "LeaveGroup"
  )
    .done(function(data) {
      apiNotify({ status: 1, message: "Successfully left classroom" });
      load_group_info();
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );

const group_request = function(e) {
  e.preventDefault();
  const form = $(this).closest("form");
  confirmDialog(
    "By joining a class you are allowing the instructor to see statistics concerning your team's performance, " +
    "as well as information on your team members such as username and email. Are you sure you want to join this class?",
    "Class Confirmation",
    "Join",
    "Cancel",
    e => form.trigger("submit"),
    e => gtag('event', 'JoinGroup', { 'event_category': 'Group', 'event_label': 'RejectPrompt' })
  );
};

const join_group_request = function(e) {
  e.preventDefault();

  const group_name = $("#group-name-input").val();
  const group_owner = $("#group-owner-input").val();
  join_group(group_name, group_owner);
};

const renderGroupInformation = _.template(
  $("#group-info-template")
    .remove()
    .text()
);

$(function() {
  $("#password-update-form").on("submit", updatePassword);
  $("#password-reset-form").on("submit", resetPassword);
  $("#disable-account-form").on("submit", disableAccount);
  $("#download-data-form").on("submit", downloadData);

  ReactDOM.render(
    <TeamManagementForm />,
    document.getElementById("team-management")
  );
  addAjaxListener("isTeacher", "/api/v1/user", function (data) {
    window.isTeacher = data.teacher;
    window.username = data.username;
  });
  load_group_info();
});
