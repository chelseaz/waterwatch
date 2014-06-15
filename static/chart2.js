
var updateChart2 = function(abv) {
    // retrieve data. TODO: only call API once for both charts
    var curDataUrl = dataUrl.replace('ABV', abv);
    var inflows = [];
    var outflows = [];
    var parseDate = d3.time.format("%Y%m%d").parse
    $.get(curDataUrl, function(data) {
        var rows = data.split("\n");
        for (var i = 1; i < rows.length; i++) {  // ignore header
            var row = rows[i].split(",");
            var unixTime = parseDate(row[0]).getTime();
            inflows[inflows.length] = [unixTime, parseInt(row[1])];
            outflows[outflows.length] = [unixTime, parseInt(row[2])];
        }

        var data = [
            {"key": "OUTFLOW (CF)", "values": outflows},
            {"key": "INFLOW (CF)", "values": inflows},
        ];

        nv.addGraph(function() {
            var chart = nv.models.stackedAreaChart()
                          .margin({right: 100})
                          .x(function(d) { return d[0] })   //We can modify the data accessor functions...
                          .y(function(d) { return d[1] })   //...in case your data is formatted differently.
                          .useInteractiveGuideline(true)    //Tooltips which show all data points. Very nice!
                          .rightAlignYAxis(true)      //Let's move the y-axis to the right side.
                          .transitionDuration(500)
                          .showControls(true)       //Allow user to choose 'Stacked', 'Stream', 'Expanded' mode.
                          .clipEdge(true);

            chart.xAxis
                .axisLabel("Date")
        //         Changes to date format
                .tickFormat(function(d) {return d3.time.format('%x')(new Date(d))
            });

            chart.yAxis
                .axisLabel("Cubic Feet")
        //         Choose tick format ("d" or ",.2f")
                .tickFormat(d3.format("s"))
                ;

        // "#chart svg" doesn't work
            d3.select("#chart2").append("svg")
                .attr("width", 768)
                .attr("height", 500)
                .datum(data)
                .transition().duration(500).call(chart);

            nv.utils.windowResize(
                    function() {
                        chart.update();
                    }
                );

            return chart;
        });
    });
};