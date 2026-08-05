const numDataPoints = 720;

const divFromSelector = selector => _.first($(selector));

const borderColors = [
  "rgba(156,99,169,1)",
  "rgba(151,187,205,1)",
  "rgba(230,22,22,1)",
  "rgba(22,230,57,1)",
  "rgba(230,22,210,1)",
  "rgba(220,220,220,1)",
  "rgba(204,104,0,1)"
];

const backgroundColors = [
  "rgba(156,99,169,0.2)",
  "rgba(151,187,205,0.2)",
  "rgba(230,22,22,0.2)",
  "rgba(22,230,57,0.2)",
  "rgba(230,22,210,0.2)",
  "rgba(220,220,220,0.2)",
  "rgba(204,104,0,0.2)"
];

const scoreboardChartSettings = {
  scales: {
    yAxes: [
      {
        gridLines: {
          display: false
        }
      }
    ],
    xAxes: [
      {
        gridLines: {
          display: false
        }
      }
    ]
  }
};

const teamChartSettings = {
  scales: {
    yAxes: [
      {
        gridLines: {
          display: false
        }
      }
    ],
    xAxes: [
      {
        gridLines: {
          display: false
        }
      }
    ]
  }
};

const timestampsToBuckets = function(samples, key, min, max, seconds) {
  const bucketNumber = number => Math.floor((number - min) / seconds);

  const continuousBucket = {};
  const maxBuckets = bucketNumber(max);

  for (let i = 0; i < maxBuckets; i++) {
    continuousBucket[i] = [];
  }

  const buckets = _.groupBy(samples, sample => bucketNumber(sample[key]));

  return _.extend(continuousBucket, buckets);
};

const maxValuesFromBucketsExtended = function(buckets, sampleKey) {
  const maxValues = [];

  let lastInsertedValue = 0;

  _.each(buckets, function(samples) {
    const values = _.pluck(samples, sampleKey);

    if (values.length > 0) {
      const maxValue = _.max(values);
      maxValues.push(maxValue);
      lastInsertedValue = maxValue;
    } else {
      maxValues.push(lastInsertedValue);
    }
  });

  return maxValues;
};

const progressionDataToPoints = function(data, dataPoints, currentDate) {
  if (currentDate == null) {
    currentDate = 0;
  }
  const sortedData = _.sortBy(_.flatten(data), submission => submission.time);

  const min = _.first(sortedData).time - 60 * 5;
  const lastTime = _.last(sortedData).time;
  const max =
    currentDate === 0 ? lastTime : Math.min(lastTime + 3600 * 24, currentDate);
  const bucketWindow = Math.max(Math.floor((max - min) / dataPoints), 1);

  const dataSets = [];

  _.each(data, function(teamData) {
    const buckets = timestampsToBuckets(
      teamData,
      "time",
      min,
      max,
      bucketWindow
    );
    let steps = maxValuesFromBucketsExtended(buckets, "score");

    if (steps.length > dataPoints) {
      steps = _.rest(steps, steps.length - dataPoints);
    }

    dataSets.push(steps);
  });

  //Avoid returning a two dimensional array with 1 element
  if (dataSets.length > 1) {
    return dataSets;
  } else {
    return _.first(dataSets);
  }
};

window.drawTopTeamsProgressionGraph = function(selector, key) {
  const div = divFromSelector(selector);

  const drawgraph = data =>
    addAjaxListener("drawTopTeamsProgressionGraph", "/api/v1/status", statusdata => {
        let i;
        if (data.length >= 2 && $(selector).is(":visible")) {
          const scoreData = data.map(
            team => team.score_progression
          );

          //Ensure there are submissions to work with
          if (_.max(_.map(scoreData, submissions => submissions.length)) > 0) {
            let chart;
            const dataPoints = progressionDataToPoints(
              scoreData,
              numDataPoints,
              statusdata.time
            );

            const datasets = [];
            for (i = 0; i < dataPoints.length; i++) {
              const points = dataPoints[i];
              datasets.push({
                label: data[i].name,
                data: points,
                pointBackgroundColor: borderColors[i % borderColors.length],
                borderColor: borderColors[i % borderColors.length],
                backgroundColor: backgroundColors[i % backgroundColors.length],
                pointHitRadius: 0,
                pointRadius: 1,
                lineTension: 0
              });
            }
            const result = [];
            for (i = 1; i < numDataPoints; i++) {
              result.push("");
            }
            data = {
              labels: result,
              datasets
            };

            $(div).empty();
            const canvas = $("<canvas>").appendTo(div);

            canvas.attr("width", $(div).width());
            canvas.attr("height", $(div).height());

            chart = new Chart(_.first(canvas).getContext("2d"), {
              type: "line",
              data,
              options: scoreboardChartSettings
            });
          }
        }
      }
    );
  if (key.hasOwnProperty('scoreboard_id') != 0) {
    apiCall("GET", "/api/v1/scoreboards/" + key.scoreboard_id + "/score_progressions")
      .done(drawgraph)
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  }
  else if (key.hasOwnProperty('group_id') != 0) {
    apiCall("GET", "/api/v1/groups/" + key.group_id + "/score_progressions")
      .done(drawgraph)
      .fail(jqXHR =>
        apiNotify({ status: 0, message: jqXHR.responseJSON.message })
      );
  }
};

window.renderTeamRadarGraph = function(selector, tid) {
  const div = divFromSelector(selector);
  $(div).empty();
  const radarData = window.generateRadarData(tid);
  if (radarData.labels.length > 0) {
    let chart;
    const canvas = $("<canvas>").appendTo(div);
    canvas.attr("width", $(div).width());
    canvas.attr("height", 400);

    return (chart = new Chart(_.first(canvas).getContext("2d"), {
      type: "radar",
      data: radarData,
      options: { scale: { ticks: { beginAtZero: true } } }
    }));
  } else {
    return $("<p>Waiting for solved problems.</p>").appendTo(div);
  }
};

window.renderTeamProgressionGraph = function(selector, data) {
  const div = divFromSelector(selector);
  addAjaxListener("renderTeamProgressionGraph", "/api/v1/status", statusdata => {
      if (data.length > 0) {
        let chart;
        const dataPoints = progressionDataToPoints(
          [data],
          numDataPoints,
          statusdata.time
        );

        const datasets = [
          {
            label: "Score",
            data: dataPoints,
            pointBackgroundColor: borderColors[0],
            borderColor: borderColors[0],
            backgroundColor: backgroundColors[0],
            pointHitRadius: 0,
            pointRadius: 0,
            lineTension: 0
          }
        ];

        data = {
          labels: __range__(1, numDataPoints, true).map(i => ""),
          datasets
        };

        $(div).empty();
        const canvas = $("<canvas>").appendTo(div);

        canvas.attr("width", $(div).width());
        canvas.attr("height", $(div).height());

        return (chart = new Chart(_.first(canvas).getContext("2d"), {
          type: "line",
          data,
          options: teamChartSettings
        }));
      } else {
        return $(selector).html("<p>No problems have been solved.</p>");
      }
    });
};

window.drawTeamProgressionGraph = (selector) =>
  apiCall("GET", "/api/v1/team/score_progression")
    .done(data => renderTeamProgressionGraph(selector, data))
    .fail(jqXHR =>
      apiNotify({ status: 0, message: jqXHR.responseJSON.message })
    );

function __range__(left, right, inclusive) {
  let range = [];
  let ascending = left < right;
  let end = !inclusive ? right : ascending ? right + 1 : right - 1;
  for (let i = left; ascending ? i < end : i > end; ascending ? i++ : i--) {
    range.push(i);
  }
  return range;
}
