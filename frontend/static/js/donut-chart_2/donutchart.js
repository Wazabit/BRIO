function _chart(width,d3,data)
{
  width = 400;
  const height = 344;
  const radius = Math.min(width, height) / 2;

  const arc = d3.arc()
      .innerRadius(radius * 0.67)
      .outerRadius(radius - 1);

  const pie = d3.pie()
      .padAngle(1 / radius)
      .sort(null)
      .value(d => d.value);

  const color = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range(d3.quantize(t => d3.interpolateCool(t * 0.8 + 0.1), data.length).reverse());

  const textcolor = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range(d3.quantize(t => d3.interpolateGreys(t * 0.8 + 0.1), data.length).reverse())


  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto;");

  svg.append("g")
    .selectAll()
    .data(pie(data))
    .join("path")
      .attr("fill", d => color(d.data.name))
      .attr("d", arc)
    .append("title")
      .text(d => `${d.data.name}: ${d.data.value.toLocaleString()}`);

  svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 16)
      .attr("text-anchor", "middle")
    .selectAll()
    .data(pie(data))
    .join("text")
      .attr("transform", d => `translate(${arc.centroid(d)})`)
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
FileAttachment("analysis-by-client.csv").csv({typed: true})
)}

export default function definedonut(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["analysis-by-client.csv", {url: new URL("./files/bee673b386dd058ab8d2cf353acbedc6aa01ebd1e6f63e2a9ab1b4273c7e6efd1eeea526345e4be7f0012d5db3ec743ef39ad9e6a043c196670bf9658cb02e79.csv", import.meta.url), mimeType: "text/csv", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer("chart")).define("chart", ["width","d3","data"], _chart);
  main.variable(observer("data")).define("data", ["FileAttachment"], _data);
  return main;
}
