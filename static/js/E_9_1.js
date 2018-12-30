window.addEventListener("load", function() {
    	showplot();
})
function showplot() {
    	var ExpP = document.getElementById("epf");
		// Plotly.plot( ExpP, );
		
		var trace1 = {
			x: x,
			y: y,
			mode: 'lines',
			name: '回測'
		};
		
		var trace2 = {
			x: x,
			y: Tw50,
			mode: 'lines',
			name: 'TW50',
			line: {
				color: 'rgb(192, 192, 192)',
				width: 1
			  }
		};
		
		var data = [ trace1, trace2 ];
		
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


// alert(List);