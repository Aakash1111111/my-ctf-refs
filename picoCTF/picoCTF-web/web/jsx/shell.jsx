const renderShellServers = _.template(
  $("#shell-servers-template")
    .remove()
    .text()
);

$(() =>
  apiCall("GET", "/api/v1/shell_servers")
    .done(function(data) {
      if (data.length > 0) {
        $("#shell-servers").html(renderShellServers({ servers: data }));
      }
    })
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    )
);
