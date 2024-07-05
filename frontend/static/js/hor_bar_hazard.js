var plot_data = document.getElementById("bubble_chart").getAttribute("val");
var h_min = document.getElementById("bubble_chart").getAttribute("h_min");
var h_max = document.getElementById("bubble_chart").getAttribute("h_max");
var d_min = document.getElementById("bubble_chart").getAttribute("d_min");
var d_max = document.getElementById("bubble_chart").getAttribute("d_max");

// set the dimensions and margins of the graph

var margin = {top: 40, right: 50, bottom: 60, left: 150},
    width = document.getElementById("hazard_chart").getBoundingClientRect().width - margin.left - margin.right,
    height = 850 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#hazard_chart")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// Parse the Data
//d3.csv("https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/7_OneCatOneNum_header.csv", function(data) {
data = d3.csvParse(plot_data);

// Add X axis
  var x = d3.scaleLinear()
    .domain([0, h_max])
    .range([ 0, width]);
  svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .attr("stroke", "#13DCF2")
    .attr("fill", "#13DCF2")
    .call(d3.axisBottom(x))
    .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");

// Add X axis label:
svg.append("text")
    .attr("text-anchor", "end")
    .attr("x", width)
    .attr("y", height+50 )
  .attr("stroke", "#13DCF2")
    .text("Hazard");

  // Y axis
  var y = d3.scaleBand()
    .range([ 0, height ])
    .domain(data.map(function(d) { return d.condition; }))
    .padding(.1);
  svg.append("g")
    .attr("stroke", "#13DCF2")
    .attr("fill", "#13DCF2")
    .call(d3.axisLeft(y))

// Add Y axis label:
svg.append("text")
  .attr("text-anchor", "end")
  .attr("x", 0)
  .attr("y", -20 )
  .attr("stroke", "#13DCF2")
  .text("Condition")
  .attr("text-anchor", "start")

// -1- Create a tooltip div that is hidden by default:
var tooltip_bar = d3.select("#hazard_chart")
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
  tooltip_bar
    .transition()
    .duration(200)
  tooltip_bar
    .style("opacity", 1)
    .html("Condition: " + d.condition + "<br>" + "Hazard: " + d.hazard + "<br>" + "Observations: " + d.num_observations + "<br>" + "Distance: " + d.distance  )
    .style("left", (d3.mouse(this)[0]+100) + "px")
    .style("top", (d3.mouse(this)[1]+100) + "px")
}
var moveTooltip = function(d) {
  tooltip_bar
    .style("left", (d3.mouse(this)[0]+100) + "px")
    .style("top", (d3.mouse(this)[1]+100) + "px")
}
var hideTooltip = function(d) {
  tooltip_bar
    .transition()
    .duration(200)
    .style("opacity", 0)
}


  //Bars
  svg.selectAll("myRect")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bars")
    .attr("x", x(0) )
    .attr("y", function(d) { return y(d.condition); })
    .attr("width", function(d) { return x(d.hazard); })
    .attr("height", y.bandwidth() )
    .attr("fill", "#D91EBA")
    .style("opacity", "0.7")
    // -3- Trigger the functions for hover
    .on("mouseover", showTooltip )
    .on("mousemove", moveTooltip )
    .on("mouseleave", hideTooltip )

