const apiOffline = { News: "/news" };

const teacherLoggedIn = {
  "Challenge Problems": "/problems",
  Shell: "/shell",
  Scoreboards: "/scoreboard",
  Classroom: "/classroom",
  News: "/news"
};

const teacherLoggedInNoCompetition = {
  Scoreboards: "/scoreboard",
  Classroom: "/classroom",
  News: "/news"
};

const userLoggedIn = {
  "Challenge Problems": "/problems",
  Shell: "/shell",
  Scoreboards: "/scoreboard",
  News: "/news"
};

const userLoggedInNoCompetition = {
  Scoreboards: "/scoreboard",
  News: "/news"
};

const userNotLoggedIn = {
  Login: "/",
  News: "/news"
};

const adminLoggedIn = { Management: "/management" };

const loadNavbar = function(renderNavbarLinks, renderNestedNavbarLinks) {
  const navbarLayout = {
    renderNavbarLinks,
    renderNestedNavbarLinks
  };

  addAjaxListener("loadNavBar", "/api/v1/user", userData => {   // onsuccess
    addAjaxListener("loadNavBar", "/api/v1/status", competitionData => {  // onsuccess
        navbarLayout.links = userNotLoggedIn;
        navbarLayout.status = userData;
        navbarLayout.topLevel = true;
        if (userData["logged_in"]) {
          if (userData["teacher"]) {
            if (competitionData["competition_active"]) {
              navbarLayout.links = teacherLoggedIn;
            } else {
              navbarLayout.links = teacherLoggedInNoCompetition;
            }
          } else {
            if (competitionData["competition_active"]) {
              navbarLayout.links = userLoggedIn;
            } else {
              navbarLayout.links = userLoggedInNoCompetition;
            }
          }
          if (userData["admin"]) {
            $.extend(navbarLayout.links, adminLoggedIn);
          }
        } else {
          $(".show-when-logged-out").css("display", "inline-block");
        }
        $("#navbar-links").html(renderNavbarLinks(navbarLayout));
        $("#navbar-item-logout").on("click", logout);
      }, () => {     // on fail
        navbarLayout.links = apiOffline;
        $("#navbar-links").html(renderNavbarLinks(navbarLayout));
      })
  }, () => {   // on fail
      navbarLayout.links = apiOffline;
      $("#navbar-links").html(renderNavbarLinks(navbarLayout));
    });
};

$(function() {
  const renderNavbarLinks = _.template(
    $("#navbar-links-template")
      .remove()
      .text()
  );
  const renderNestedNavbarLinks = _.template(
    $("#navbar-links-dropdown-template")
      .remove()
      .text()
  );

  loadNavbar(renderNavbarLinks, renderNestedNavbarLinks);
  window.scoreUpdateTimer = setInterval(() => {
    apiCall("GET", "/api/v1/user").done(() => {
      loadNavbar(renderNavbarLinks, renderNestedNavbarLinks);
    })
  }, 60 * 1000)
});
