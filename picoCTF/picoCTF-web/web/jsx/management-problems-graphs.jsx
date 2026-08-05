const ProblemSubmissionDoughnut = React.createClass({
  componentDidMount() {
    if (this.props.visible) {
      let chart;
      const ctx = this.context;

      const data = {
        datasets: [
          {
            data: [this.props.invalid, this.props.valid],
            backgroundColor: ["#F7464A", "#46BFBD"],
            hoverBackgroundColor: ["#FF5A5E", "#5AD3D1"]
          }
        ],
        labels: ["Invalid Submissions", "Valid Submissions"]
      };
      return (chart = new Chart(ctx, {
        type: "doughnut",
        data,
        options: {
          animation: { animateRotate: false, animateScale: false }
        }
      }));
    }
  },

  render() {
    const style = {
      padding: 0,
      margin: "auto",
      display: "block"
    };

    return (
      <canvas
        height="200"
        ref={c => {
          return (this.context = c.getContext("2d"));
        }}
        width="200"
        style={style}
      />
    );
  }
});
