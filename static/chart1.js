var updateChart1 = function(abv) {
    var margin = {top: 10, right: 10, bottom: 100, left: 40},
        margin2 = {top: 330, right: 10, bottom: 20, left: 40},
        width = 768 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom,
        height2 = 400 - margin2.top - margin2.bottom;

    var parseDate = d3.time.format("%Y%m%d").parse;

    var x = d3.time.scale().range([0, width]),
        x2 = d3.time.scale().range([0, width]),
        y = d3.scale.linear().range([height, 0]),
        y2 = d3.scale.linear().range([height2, 0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom")
                .ticks(0);   
    var xAxis2 = d3.svg.axis().scale(x2).orient("bottom"),
        yAxis = d3.svg.axis()
        .scale(y).orient("left")
        .tickFormat(d3.format("s"))
        .ticks(10);///limits texts;

    var brush = d3.svg.brush()
        .x(x2)
      .extent([0,.16])///////// fixed width
        .on("brush", brushed);

    var area = d3.svg.area()
        .interpolate("monotone")
        .x(function(d) { return x(d.DATE); })
        .y0(height)
        .y1(function(d) { return y(d.STORAGE); });

    var area2 = d3.svg.area()
        .interpolate("monotone")
        .x(function(d) { return x2(d.DATE); })
        .y0(height2)
        .y1(function(d) { return y2(d.STORAGE); });

    var svg = d3.select("#chart1").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);

    var focus = svg.append("g")
        .attr("class", "focus")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var context = svg.append("g")
        .attr("class", "context")
        .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

    var curDataUrl = dataUrl.replace('ABV', abv);
    d3.csv(curDataUrl, type, function(error, data) {
      x.domain(d3.extent(data.map(function(d) { return d.DATE; })));
     /// y.domain([0, maxiumum])
      y.domain([0, d3.max(data.map(function(d) { return d.STORAGE; }))]);
      x2.domain(x.domain());
      y2.domain(y.domain());

      focus.append("path")
          .datum(data)
          .attr("class", "area")
          .attr("d", area);

      focus.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      focus.append("text")
        .attr("transform", "rotate(-90)")
        .attr("class", "shadow")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Cubic Feet");
  
   focus.append("text")
       .attr("transform", "rotate(-90)")
       .attr("y", 6)
       .attr("dy", ".71em")
       .style("text-anchor", "end")
       .text("Cubic Feet");

      focus.append("g")
          .attr("class", "y axis")
          .call(yAxis);

      context.append("path")
          .datum(data)
          .attr("class", "area")
          .attr("d", area2);

      context.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height2 + ")")
          .call(xAxis2);

      context.append("g")
          .attr("class", "x brush")
        .call(brush)
        .selectAll("rect")
          .attr("y", -6)
          .attr("height", height2 + 7);
    });

    function brushed() {
      x.domain(brush.empty() ? x2.domain() : brush.extent());
      focus.select(".area").attr("d", area);
      focus.select(".x.axis").call(xAxis);
    /////////remove////////

    }

    function type(d) {
      d.DATE = parseDate(d.DATE);
      d.STORAGE = +d.STORAGE;
      return d;
    }
};
