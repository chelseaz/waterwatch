// function myData() {
//     var series1 = [];
//     for(var i =1; i < 100; i ++) {
//         series1.push({
//             x: i, y: 100 / i
//         });
//     }
// 
//     return [
//         {
//             key: "Series #1",
//             values: series1,
//             color: "#0000ff"
//         }
//     ];
// }

// Use data.js script
// var data = 
// [ 
//     { 
//     "key" : "INFLOW (CF)", 
//     "values" : [[1325404800000, 950400],[1325494080000, 60912000],[1325583360000, 56505600],[1325672640000, 55900800],[1325761920000, 55987200],[1325851200000, 56419200],[1325940480000, 55123200],[1326029760000, 950400],[1326119040000, 950400],]
//     }, 
// 
//     { 
//     "key" : "OUTFLOW (CF)", 
//     "values" : [[1325404800000, 28857600],[1325494080000, 28771200],[1325583360000, 28857600],[1325672640000, 28771200],[1325761920000, 28771200],[1325851200000, 28771200],[1325940480000, 28684800],[1326029760000, 28684800],[1326119040000, 28771200],]
//     }
// ]

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
    ;

    chart.xAxis
        .axisLabel("Date")
//         Changes to date format
        .tickFormat(function(d) {return d3.time.format('%x')(new Date(d))
    });

    chart.yAxis
        .axisLabel("Cubic Feet")
//         Choose tick format ("d" or ",.2f")
        .tickFormat(d3.format("d"))
        ;

// "#chart svg" doesn't work
    d3.select("svg")
        .datum(data)
        .transition().duration(500).call(chart);

    nv.utils.windowResize(
            function() {
                chart.update();
            }
        );

    return chart;
});
