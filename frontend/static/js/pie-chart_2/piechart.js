function _chart(d3,data)
{
  // Specify the chart’s dimensions.
  const width = 400;
  const height = 344;

  // Create the color scale.
  const color = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range(d3.quantize(t => d3.interpolateCool(t * 0.8 + 0.1), data.length).reverse()) // Create the color scale.

  const textcolor = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range(d3.quantize(t => d3.interpolateGreys(t * 0.8 + 0.1), data.length).reverse())

  // Create the pie layout and arc generator.
  const pie = d3.pie()
      .sort(null)
      .value(d => d.value);

  const arc = d3.arc()
      .innerRadius(0)
      .outerRadius(Math.min(width, height) / 2 - 1);

  const labelRadius = arc.outerRadius()() * 0.8;

  // A separate arc generator for labels.
  const arcLabel = d3.arc()
      .innerRadius(labelRadius)
      .outerRadius(labelRadius);

  const arcs = pie(data);

  // Create the SVG container.
  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto; font: 16px sans-serif;");

  // Add a sector path for each value.
  svg.append("g")
      .attr("stroke", "#0A3B5A")
    .selectAll()
    .data(arcs)
    .join("path")
      .attr("fill", d => color(d.data.name))
      .attr("d", arc)
    .append("title")
      .text(d => `${d.data.name}: ${d.data.value.toLocaleString("en-US")}`);

  // Create a new arc generator to place a label close to the edge.
  // The label shows the value if there is enough room.
  svg.append("g")
      .attr("text-anchor", "middle")
    .selectAll()
    .data(arcs)
    .join("text")
      .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
      .call(text => text.append("tspan")
          .attr("y", "-0.4em")
          .attr("font-weight", "bold")
          .attr("fill", d => textcolor(d.data.name))
          .text(d => d.data.name))
      .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan")
          .attr("x", 0)
          .attr("y", "0.7em")
          .attr("fill", d => textcolor(d.data.name))
          .text(d => d.data.value.toLocaleString("en-US")));

  return svg.node();
}


function _data(FileAttachment){return(
FileAttachment("project-by-client.csv").csv({typed: true})
)}

export default function definepie(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["project-by-client.csv", {url: new URL("./files/bee673b386dd058ab8d2cf353acbedc6aa01ebd1e6f63e2a9ab1b4273c7e6efd1eeea526345e4be7f0012d5db3ec743ef39ad9e6a043c196670bf9658cb02e79.csv", import.meta.url), mimeType: "text/csv", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer("chart")).define("chart", ["d3","data"], _chart);
  main.variable(observer("data")).define("data", ["FileAttachment"], _data);
  return main;
}
