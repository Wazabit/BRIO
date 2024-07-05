var plot_data = document.getElementById("bubble_chart").getAttribute("val");
var h_min = document.getElementById("bubble_chart").getAttribute("h_min");
var h_max = document.getElementById("bubble_chart").getAttribute("h_max");
var d_min = document.getElementById("bubble_chart").getAttribute("d_min");
var d_max = document.getElementById("bubble_chart").getAttribute("d_max");

if (d_max*1.2 > 1) d_max = 1;
else d_max = d_max*1.2;

// set the dimensions and margins of the graph
var margin = {top: 40, right: 180, bottom: 60, left: 50},
    width = document.getElementById("bubble_chart").getBoundingClientRect().width - margin.left - margin.right,
    height = 420 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#bubble_chart")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");


// Add X axis
var x = d3.scaleLinear()
  .domain([d_min/1.2, d_max])
  .range([ 0, width ]);
svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .attr("stroke", "#13DCF2")
  .attr("fill", "#13DCF2")
  .call(d3.axisBottom(x));

// Add X axis label:
svg.append("text")
    .attr("text-anchor", "end")
    .attr("x", width)
    .attr("y", height+50 )
  .attr("stroke", "#13DCF2")
    .text("Distance");

// Add Y axis
var y = d3.scaleLinear()
  .domain([h_min/1.2, h_max*1.2])
  .range([ height, 0]);
svg.append("g")
  .attr("stroke", "#13DCF2")
  .attr("fill", "#13DCF2")
  .call(d3.axisLeft(y));

// Add Y axis label:
svg.append("text")
  .attr("text-anchor", "end")
  .attr("x", 0)
  .attr("y", -20 )
  .attr("stroke", "#13DCF2")
  .text("Hazard")
  .attr("text-anchor", "start")

// Add a scale for bubble size
var z = d3.scaleLinear()
  .domain([1, 10000])
  .range([ 1, 100]);


  // -1- Create a tooltip div that is hidden by default:
var tooltip = d3.select("#bubble_chart")
  .append("div")
    .style("opacity", 0)
    .style("pointer-events", "none")
    .attr("class", "tooltip")
    .style("background-color", "black")
    .style("border-radius", "5px")
    .style("padding", "10px")
    .style("color", "white")

// -2- Create 3 functions to show / update (when mouse move but stay on same circle) / hide the tooltip
var showTooltip = function(d) {
  tooltip
    .transition()
    .duration(200)
  tooltip
    .style("opacity", 1)
    .html("Condition: " + d.condition + "<br>" + "Observations: " + d.num_observations + "<br>" + "Hazard: " + d.hazard + "<br>" + "Distance: " + d.distance)
    .style("left", (d3.mouse(this)[0]+80) + "px")
    .style("top", (d3.mouse(this)[1]+80) + "px")
}
var moveTooltip = function(d) {
  tooltip
    .style("left", (d3.mouse(this)[0]+80) + "px")
    .style("top", (d3.mouse(this)[1]+80) + "px")
}
var hideTooltip = function(d) {
  tooltip
    .transition()
    .duration(200)
    .style("opacity", 0)
}



data = d3.csvParse(plot_data);

svg.append('g')
  .selectAll("dot")
  .data(data)
  .enter()
  .append("circle")
    .attr("class", "bubbles")
    .attr("cx", function (d) { return x(d.distance); } )
    .attr("cy", function (d) { return y(d.hazard); } )
    .attr("r", function (d) { return z(d.num_observations); } )
    .style("fill", "#D91EBA")
    .style("opacity", "0.7")
    .attr("stroke", "#13DCF2")
  // -3- Trigger the functions for hover
  .on("mouseover", showTooltip )
  .on("mousemove", moveTooltip )
  .on("mouseleave", hideTooltip )


// Add legend: circles
    var valuesToShow = [100, 1000, 5000]
    var xCircle = width + 60
    var xLabel = width + 120
    var yoffset = 200
    svg
      .selectAll("legend")
      .data(valuesToShow)
      .enter()
      .append("circle")
        .attr("cx", xCircle)
        .attr("cy", function(d){ return height - yoffset - z(d) } )
        .attr("r", function(d){ return z(d) })
        .style("fill", "none")
        .attr("stroke", "#13DCF2")

    // Add legend: segments
    svg
      .selectAll("legend")
      .data(valuesToShow)
      .enter()
      .append("line")
        .attr('x1', function(d){ return xCircle + z(d) } )
        .attr('x2', xLabel)
        .attr('y1', function(d){ return height - yoffset - z(d) } )
        .attr('y2', function(d){ return height - yoffset - z(d) } )
        .attr('stroke', '#13DCF2')
        .style('stroke-dasharray', ('2,2'))

    // Add legend: labels
    svg
      .selectAll("legend")
      .data(valuesToShow)
      .enter()
      .append("text")
        .attr('x', xLabel)
        .attr('y', function(d){ return height - yoffset - z(d) } )
        .attr('stroke', '#13DCF2')
        .text( function(d){ return d } )
        .style("font-size", 10)
        .attr('alignment-baseline', 'middle')

    // Legend title
    svg.append("text")
      .attr('x', xCircle)
      .attr("y", height - yoffset +30)
      .text("Observations")
      .attr("text-anchor", "middle")
      .attr('stroke', '#13DCF2')

