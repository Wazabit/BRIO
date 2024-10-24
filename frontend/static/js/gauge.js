var gauge = function(container, configuration) {
	const that = {};
	const config = {
		size: 400,
		clipWidth: 400,
		clipHeight: 220,
		ringInset: 20,
		ringWidth: 20,

		pointerWidth: 20,
		pointerTailLength: 10,
		pointerHeadLengthPercent: 0.9,

		minValue: 0,
		maxValue: 100,

		minAngle: -90,
		maxAngle: 90,

		transitionMs: 750,

		majorTicks: 5,
		labelFormat: d3.format('d'),
		labelInset: 10,

		arcColorFn: d3.interpolateHsl(d3.rgb('#eecc00'), d3.rgb('#FF0000'))
	};
	let range = undefined;
	let r = undefined;
	let pointerHeadLength = undefined;
	const value = 0;

	let svg = undefined;
	let arc = undefined;
	let scale = undefined;
	let ticks = undefined;
	let tickData = undefined;
	let pointer = undefined;

	const donut = d3.pie();

	function deg2rad(deg) {
		return deg * Math.PI / 180;
	}

	function newAngle(d) {
		const ratio = scale(d);
		const newAngle = config.minAngle + (ratio * range);
		return newAngle;
	}

	function configure(configuration) {
		let prop = undefined;
		for ( prop in configuration ) {
			config[prop] = configuration[prop];
		}

		range = config.maxAngle - config.minAngle;
		r = config.size / 2;
		pointerHeadLength = Math.round(r * config.pointerHeadLengthPercent);

		// a linear scale that maps domain values to a percent from 0..1
		scale = d3.scaleLinear()
			.range([0,1])
			.domain([config.minValue, config.maxValue]);

		ticks = scale.ticks(config.majorTicks);
		tickData = d3.range(config.majorTicks).map(function() {return 1/config.majorTicks;});

		arc = d3.arc()
			.innerRadius(r - config.ringWidth - config.ringInset)
			.outerRadius(r - config.ringInset)
			.startAngle(function(d, i) {
				var ratio = d * i;
				return deg2rad(config.minAngle + (ratio * range));
			})
			.endAngle(function(d, i) {
				var ratio = d * (i+1);
				return deg2rad(config.minAngle + (ratio * range));
			});
	}
	that.configure = configure;

	function centerTranslation() {
		return 'translate('+r +','+ r +')';
	}

	function isRendered() {
		return (svg !== undefined);
	}
	that.isRendered = isRendered;

	function render(newValue) {
		svg = d3.select(container)
			.append('svg:svg')
				.attr('class', 'gauge')
				.attr('width', config.clipWidth)
				.attr('height', config.clipHeight);

		var centerTx = centerTranslation();

		var arcs = svg.append('g')
				.attr('class', 'arc')
				.attr('transform', centerTx);

		arcs.selectAll('path')
				.data(tickData)
			.enter().append('path')
				.attr('fill', function(d, i) {
					return config.arcColorFn(d * i);
				})
				.attr('d', arc);

		var lg = svg.append('g')
				.attr('class', 'label')
				.attr('transform', centerTx);
		lg.selectAll('text')
				.data(ticks)
			.enter().append('text')
				.attr('transform', function(d) {
					var ratio = scale(d);
					var newAngle = config.minAngle + (ratio * range);
					return 'rotate(' +newAngle +') translate(0,' +(config.labelInset - r) +')';
				})
				.text(config.labelFormat);

		var lineData = [ [config.pointerWidth / 2, 0],
						[0, -pointerHeadLength],
						[-(config.pointerWidth / 2), 0],
						[0, config.pointerTailLength],
						[config.pointerWidth / 2, 0] ];
		var pointerLine = d3.line().curve(d3.curveLinear)
		var pg = svg.append('g').data([lineData])
				.attr('class', 'pointer')
				.attr('transform', centerTx);

		pointer = pg.append('path')
			.attr('d', pointerLine/*function(d) { return pointerLine(d) +'Z';}*/ )
			.attr('transform', 'rotate(' +config.minAngle +')');

		update(newValue === undefined ? 0 : newValue);
	}
	that.render = render;
	function update(newValue, newConfiguration) {
		if ( newConfiguration  !== undefined) {
			configure(newConfiguration);
		}
		var ratio = scale(newValue);
		var newAngle = config.minAngle + (ratio * range);
		pointer.transition()
			.duration(config.transitionMs)
			.ease(d3.easeElastic)
			.attr('transform', 'rotate(' +newAngle +')');
	}
	that.update = update;

	configure(configuration);

	return that;
};
var powerGauge;
function onDocumentReady() {
	powerGauge = gauge('#power-gauge', {
		size: 250,
		clipWidth: 250,
		clipHeight: 150,
		ringWidth: 30,
		maxValue: 100,
		transitionMs: 2000,
	});
	powerGauge.render();
	
	function updateReadings() {
		// just pump in random data here...
		powerGauge.update(document.getElementById("power-gauge").getAttribute("val"));
	}
	
	// every few seconds update reading values
	updateReadings();
	setInterval(function() {
		updateReadings();
	}, 5 * 1000);
}

function updateGauge() {
	// just pump in random data here...
	powerGauge.update(document.getElementById("power-gauge").getAttribute("val"));
}

if ( !window.isLoaded ) {
	window.addEventListener("load", function() {
		onDocumentReady();
	}, false);
} else {
	onDocumentReady();
}