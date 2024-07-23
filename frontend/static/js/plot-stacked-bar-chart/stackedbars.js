function _1(Plot,tidy){return(
Plot.plot({
  width: 928,
  height: 300,
  x: {label: null},
  y: {tickFormat: "s", tickSpacing: 50},
  color: {scheme: "Cool", legend: "ramp", width: 928, label: "Clients"},
  marks: [
    Plot.barY(tidy, {
      x: "month",
      y: "population",
      fill: "age",
      sort: {color: null, x: "x"}
    })
  ]
})
)}

function _population(FileAttachment){return(
FileAttachment("clients-over-time.csv").csv({typed: true})
)}

function _tidy(population){return(
population.columns.slice(1).flatMap((age) => population.map(d => ({month: d.name, age, population: d[age]})))
)}

export default function definition(runtime, observer) {
  const main = runtime.module();
  function toString() { return this.url; }
  const fileAttachments = new Map([
    ["clients-over-time.csv", {url: new URL("./files/testbutta.csv", import.meta.url), mimeType: "text/csv", toString}]
  ]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["Plot","tidy"], _1);
  main.variable(observer("population")).define("population", ["FileAttachment"], _population);
  main.variable(observer("tidy")).define("tidy", ["population"], _tidy);
  return main;
}
