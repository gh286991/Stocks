// 從HTML傳入值
    
function DefaultParmeters(){
    
    var Parmeters = {
        'MarkCap' : 1e10,
        'FCF' : 18,
        'ROE' : 0,
        'OPM' : 0,
        'PSR' : 5,
        'RSV' : 0.7,
        'price' : 40,
        'startD' : "2018-11-01",
        'endD' : "2018-12-10",
        'period' : 28,
    };
    
    document.getElementById("MarkCap").value = Parmeters.MarkCap;
    document.getElementById("FCF").value = Parmeters.FCF;
    document.getElementById("ROE").value = Parmeters.ROE ;
    document.getElementById("OPM").value = Parmeters.OPM;
    document.getElementById("PSR").value = Parmeters.PSR;
    document.getElementById("RSV").value = Parmeters.RSV ;
    document.getElementById("price").value = Parmeters.price;
    document.getElementById("startD").value = Parmeters.startD;
    document.getElementById("endD").value = Parmeters.endD ;
    document.getElementById("period").value = Parmeters.period;

    
    
    
};

function GetResult(Data){
    

    document.getElementById("result").innerHTML= '結果'
   

    var resulttext = document.getElementById("resulttext");
    var maxmintext = document.getElementById("resultmaxmin");
    var selection =  document.getElementById("selection");

// '-----------------------重置----------------'
    resulttext.innerHTML = "";
    maxmintext.innerHTML = "";
    selection.innerHTML = "";

// '-----------------------重置----------------'
    for(let i = 0; i < Data['ED'].length ; i++) {
        var text = Data['SD'][i] + '---'+ Data['ED'][i] + ' 報酬率:' + Data['Returns'][i] +'%'+' nstocks:'+ Data['NS'][i]+'</br>'
        resulttext.innerHTML= resulttext.innerHTML +  text;
        console.log(Data['ED'][i]);
    };
    
    var maxmin = "每次換手最大報酬: " + Data['maxreturn'] +"%" + "</br>" +"每次換手最小報酬: "+ Data['minreturn'] +"%";
    maxmintext.innerHTML= maxmin;

    for(let i = 0;i < Data['SelectStocks'].length;i++){

        document.getElementById("selectionT").innerHTML = "選出的股票為: ";
        

        selection.innerHTML= selection.innerHTML + Data['SelectStocks'][i] +'</br>';
    }


    
};



function GetFigure(Data){
    var Fig = document.getElementById("figure");
    var trace1 = {
        x: Data['z'],
        y: Data['g'],
        mode: 'lines',
        name: '回測',
    };
    var trace2 = {
        x: Data['z'],
        y:  Data['Tw50'],
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
			  },
        };
        
    Plotly.newPlot(Fig, data, layout);		
};

function HeightChange(id){
    var myDiv = document.getElementById(id); 
    var computedStyle = document.defaultView.getComputedStyle(myDiv, null); 
    var ContentHeight = parseInt(computedStyle.height)
    var bodyheight = document.getElementsByTagName('body')[0]
    bodyheight.style.height = ContentHeight + 250 +'px'
    // console.log(ContentHeight)
    // console.log(bodyheight.style.height )
};

function GetData(){
    loadingbar();
    DisShowResult();
    HeightChange('StocksBox');

    var xhr = new XMLHttpRequest();

    var input = {
        MarkCap : Number(document.getElementById('MarkCap').value),
        FCF :  Number(document.getElementById('FCF').value),
        ROE :  Number(document.getElementById('ROE').value),
        OPM :  Number(document.getElementById('OPM').value),
        PSR :  Number(document.getElementById('PSR').value),
        RSV :  Number(document.getElementById('RSV').value),
        price : Number(document.getElementById('price').value),
        startD : document.getElementById('startD').value,
        endD :  document.getElementById('endD').value,
        period : Number( document.getElementById('period').value),
    }
    
    var data = JSON.stringify(input);
    
    xhr.open('post','http://127.0.0.1:8000/stocks/api',true);
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'),"application/x-www-form-urlencoded");
    xhr.send(data);

    console.log('傳送資料 ' + data);


    xhr.onload = function() {
            Disloadingbar();
            ShowResult();

            var Result = JSON.parse(xhr.responseText);
            console.log('Result =' + Result['ED']);
            console.log(Result['ED'].length);
            GetResult(Result);
            GetFigure(Result);
            HeightChange('StocksBox');
            return 
            };

    console.log('test');
    console.log(data);

};
    
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// '----------------Loading 動畫----------------'

function Disloadingbar(){
	var Loading = document.getElementById('LoadingBar');
	Loading.setAttribute("class", "LoadingBar2");
};

function loadingbar(){
	var Loading = document.getElementById('LoadingBar');
	Loading.setAttribute("class", "LoadingBar");
};

//----------結果顯示


function DisShowResult(){
    var Loading = document.getElementById('results');
    document.getElementById("result").innerHTML= "";
	Loading.setAttribute("class", "results2");
};

function ShowResult(){
	var Loading = document.getElementById('results');
	Loading.setAttribute("class", "results");
};

// function DisResult(){
// 	var Loading = document.getElementById('ResultArea');
// 	Loading.setAttribute("class", "ResultArea2");
// };

// function Result(){
// 	var Loading = document.getElementById('ResultArea');
// 	Loading.setAttribute("class", "ResultArea");
// };


//---main function-----
// HeightChange('StocksBox');
window.onload=Disloadingbar();
window.onload=DefaultParmeters();


// GetHeight("StocksBox")
// Postdata(test)
// GetValues()
    
    
    
    