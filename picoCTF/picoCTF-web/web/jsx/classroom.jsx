const renderGroupInformation = _.template(
  $("#group-info-template")
    .remove()
    .text()
);

const renderTeamSelection = _.template(
  $("#team-selection-template")
    .remove()
    .text()
);

String.prototype.hashCode = function () {
  let hash = 0;
  for (let i = 0; i < this.length; i++) {
    const char = this.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return hash;
};

window.getName = function(first, last, user) {
  let name = (first + " " + last).trim();
  if (name) {
    name += ` (${user})`;
  } else {
    name = user;
  }
  return name;
};

const createGroupSetup = function() {
  const formDialogContents = _.template($("#new-group-template").html())({});
  formDialog(
    formDialogContents,
    "Create a New Classroom",
    "OK",
    "new-group-name",
    () => createGroup($("#new-group-name").val())
  );
};

window.exportProblemCSV = (groupName, teams) =>
  apiCall("GET", "/api/v1/problems?unlocked_only=false")
    .done(function(data) {
      // problems = _.filter resp.data.problems, (problem) -> !problem.disabled
      const problems = data; // non-admin API only returns non-disabled problems as top level data array
      const outputData = [
        ["Teamname", "Member Name(s)"].concat(
          _.map(problems, problem => `"${problem.name}"`),
          ["Total"]
        )
      ];
      _.each(teams, function(team) {
        const members = `"${team.members
          .map(function(member) {
            return getName(
              member.firstname,
              member.lastname,
              member.username
            );
          })
          .join(", ")}"`;
        let teamData = [team.team_name, members];
        teamData = teamData.concat(
          _.map(problems, function(problem) {
            const solved = _.find(
              team.solved_problems,
              solvedProblem => solvedProblem.name === problem.name
            );
            if (solved) {
              return problem.score;
            } else {
              return 0;
            }
          })
        );
        teamData = teamData.concat([team.score]);
        outputData.push(teamData);
      });
      const csvData = _.map(outputData, fields => fields.join(",")).join("\n");
      download(csvData, `${groupName}.csv`, "text/csv");
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );

const loadGroupOverview = function(groups, showFirstTab, callback) {
  $("#group-overview").html(renderGroupInformation({ data: groups }));

  $("#new-class-tab").on("click", e => createGroupSetup());

  $("#new-class-button").on("click", e => createGroupSetup());

  $("#class-tabs").on("shown.bs.tab", 'a[data-toggle="tab"]', function(e) {
    const tabBody = $(this).attr("href");
    const groupName = $(this).data("groupName");

    apiCall("GET", `/api/v1/groups/${$(this).data("gid")}`).done(
      data => {
        for (let group of groups) {
          if (group.name == groupName) {
            // less strict number type comparison
            $(tabBody).html(
              renderTeamSelection({
                teams: data.members,
                groupName,
                owner: group.owner,
                gid: group.gid
              })
            );
          }
        }
        $(".team-visualization-enabler").on("click", function(e) {
          const gid = $(e.target).data("gid");
          const tid = $(e.target).data("tid");
          const result = [];
          for (let team of data.members) {
            if (tid === team.tid) {
              window.renderTeamProgressionGraph(
                `#visualizer-${gid}-${tid}`,
                 team.progression
              );
              //hack
              result.push(
                _.delay(
                  window.renderTeamRadarGraph,
                  150,
                  `#radar-visualizer-${gid}-${tid}`,
                  tid
                )
              );
            } else {
              result.push(undefined);
            }
          }
          return result;
        });
      }
    );
  });

  if (showFirstTab) {
    $("#class-tabs a:first").tab("show");
  }

  $("ul.nav-tabs a").click(function(e) {
    e.preventDefault();
    $(this).tab("show");
  });

  $("#group-request-form").on("submit", groupRequest);
  $(".delete-group-span").on("click", e =>
    deleteGroup($(e.target).data("gid"))
  );

  if (callback) {
    callback();
  }
};

const loadGroupInfo = (showFirstTab, callback) =>
  apiCall("GET", "/api/v1/groups", null, "Group", "GroupListLoad")
    .done(function(data) {
      loadGroupOverview(data, showFirstTab, callback);
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );

const createGroup = function(groupName) {
  const data = { name: groupName };
  apiCall("POST", "/api/v1/groups", data, "Group", "CreateGroup")
    .done(function(data) {
      closeDialog();
      apiNotify({ status: 1, message: "Successfully created classroom." });
      loadGroupInfo(false, () =>
        $("#class-tabs li:eq(-2) a").tab("show")
      );
    })
    .fail(jqXHR =>
      apiNotifyElement($("#new-group-name"), {
        status: 0,
        message: jqXHR.responseJSON.message
      })
    );
};

const deleteGroup = gid =>
  confirmDialog(
    "You are about to permanently delete this class. This will automatically remove your students from this class. Are you sure you want to delete this class?",
    "Class Confirmation",
    "Delete Class",
    "Cancel",
    () =>
      apiCall(
        "DELETE",
        `/api/v1/groups/${gid}`,
        null,
        "Group",
        "DeleteGroup"
      ).done(function(data) {
        apiNotify({ status: 1, message: "Successfully deleted classroom" });
        loadGroupInfo(true);
      })
      .fail(jqXHR =>
        apiNotify({
          status: 0,
          message: jqXHR.responseJSON.message
        })
      ),
    () => gtag('event', 'DeleteGroup', { 'event_category': 'Group',  'event_label': 'RejectPrompt' })
  );

//Could be simplified without this function
const groupRequest = function(e) {
  e.preventDefault();
  const groupName = $("#group-name-input").val();
  createGroup(groupName);
};

$(function() {
  addAjaxListener("updateTeacherStatus", "/api/v1/user", function (data) {
    if (data.teacher) {
      window.isTeacher = true;
    }
    if (data.admin) {
      window.isAdmin = true;
    }
  });
  loadGroupInfo(true);
  $(document).on("shown.bs.tab", 'a[href="#group-overview-tab"]', () => {
    loadGroupInfo(true);
  });
});
