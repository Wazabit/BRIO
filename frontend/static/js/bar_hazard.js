var plot_data = document.getElementById("bubble_chart").getAttribute("val");
var h_min = document.getElementById("bubble_chart").getAttribute("h_min");
var h_max = document.getElementById("bubble_chart").getAttribute("h_max");
var d_min = document.getElementById("bubble_chart").getAttribute("d_min");
var d_max = document.getElementById("bubble_chart").getAttribute("d_max");

container = document.getElementById("hazard_chart");
// set the dimensions and margins of the graph

var margin = {top: 40, right: 50, bottom: 60, left: 50},
    width = container.getBoundingClientRect().width - margin.left - margin.right,
    height = 420 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select(container)
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// Parse the Data
//d3.csv("https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/7_OneCatOneNum_header.csv", function(data) {
data = d3.csvParse(plot_data);
// X axis
var x = d3.scaleBand()
  .range([ 0, width ])
  .domain(data.map(function(d) { return d.condition; }))
  .padding(0.2);
svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .attr("stroke", "#13DCF2")
  .attr("fill", "#13DCF2")
  .call(d3.axisBottom(x))
  .selectAll("text")
    .attr("transform", "translate(-10,0)rotate(-45)")
    .style("text-anchor", "end");

svg.append("text")
    .attr("text-anchor", "end")
    .attr("x", width)
    .attr("y", height+50 )
  .attr("stroke", "#13DCF2")
    .text("Condition");

// Add Y axis
var y = d3.scaleLinear()
  .domain([0, h_max])
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

// Bars
svg.selectAll("mybar")
  .data(data)
  .enter()
  .append("rect")
    .attr("x", function(d) { return x(d.condition); })
    .attr("width", x.bandwidth())
    .attr("fill", "#D91EBA")
    // no bar at the beginning thus:
    .attr("height", function(d) { return height - y(0); }) // always equal to 0
    .attr("y", function(d) { return y(0); })

// Animation
svg.selectAll("rect")
  .transition()
  .duration(800)
  .attr("y", function(d) { return y(d.hazard); })
  .attr("height", function(d) { return height - y(d.hazard); })
  .delay(function(d,i){console.log(i) ; return(i*100)})

//})
