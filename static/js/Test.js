
var xhr = new XMLHttpRequest();

var XXXR = function showplot(data1) {
	var ExpP = document.getElementById("epf");
	// Plotly.plot( ExpP, );
	var data1 = JSON.parse(xhr.responseText)
	console.log(data1)
	console.log(data1.x)

	var trace1 = {
		x: data1.x,
		y: data1.y,
		mode: 'lines',
		name: '回測',
	};
	var data = [ trace1 ];
	var layout = {
		// title:'回測線圖',
		yaxis: {
			title: 'Percent %',
			showline: true
		},
		xaxis: {
			title: 'Date',
			showline: true
		}  
	};

	Plotly.newPlot(ExpP, data, layout);

		
};


xhr.open('GET','/api/plot',true);
xhr.send();

xhr.onload = XXXR;
		         

// alert(List);