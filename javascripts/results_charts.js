function reConstructAccvsPerfChart(category) {
    availabilities = [ "Available", "Preview", "RDI" ]; 
    availabilities.forEach(function(availability) {
        // filtered data as per the user choice
        //console.log(filteredResults.length);
        drawAccvsPerfPlot(category, availability);
    });
}

function drawAccvsPerfPlot(category, availability) {
    // the data here is the preprocessed data through function preprocessData
    models = []
    if (category == "datacenter") {
        models = models_datacenter;
    }
    else{
        models = models_edge;
    }
    models.forEach(function(model, index) {
        let accuracyMetric = ``;
        // Currently the first accuracy matrix is used to construct the scatter plot
        if (accuracyUnits.hasOwnProperty(model)) {
            accuracyMetric = accuracyUnits[model].split(",")[0].trim();
        }
        if (category === "datacenter") {
            let extractedData = extractTableDataForAccVsPerf(model, availability);
            const chartContainer = document.getElementById(`AccVsPerfScatterPlot_${model}_open_${category}_${availability}`);
            if (extractedData.length === 0) {
                if (chartContainer) {
                    chartContainer.style.display = 'none'; // hide the div
                }
                return;
            }
            if (chartContainer) {
                chartContainer.style.display = 'block'; // Show the div
            }
            // let filteredData = filterForAccvsPerfPlot(data, model, category, division, accuracyMetric);
            if (extractedData.length !== 0) {
                let chart = new CanvasJS.Chart(`AccVsPerfScatterPlot_${model}_open_${category}_${availability}`, {
                    animationEnabled: true,
                    theme: "light2",
                    title:{
                      text: `Accuracy vs Performance for ${model}`
                    },
                    axisX:{
                      title: "Performance"
                    },
                    axisY:{
                      title: "Accuracy",
                      includeZero: false
                    },
                    data: [{
                      type: "scatter",
                      toolTipContent: "<b>ID:</b> {id}<br/><b>Submitter:</b> {submitter}<br/><b>System:</b> {system}<br/><b>Accelerator:</b> {accelerator}<br/><b>Scenario:</b> {scenario}<br/><b>Performance:</b> {x}<br/><b>Accuracy:</b> {y}",
                      dataPoints: extractedData
                    }]
                  });
                chart.render();
            }
        }
    });
}

function extractTableDataForAccVsPerf(model, availability) {
    let mylocation = [], system_names = [], submitter = [], accelerator = [], offline_accuracy = [], offline_performance = [], server_accuracy = [], server_performance = [];
    let locationIndex = {}, locCount = 0;
    let extractedData = [];
    let childTag = `#results_${model}_${availability}`
    const escapedChildTag = childTag.replace(/\./g, '\\.');
    // console.log(`#results_${model}_${availability}`)
    $(`${escapedChildTag} tbody tr td:nth-child(1)`).each( function(){
		if (!($(this).is(":hidden")) ){
			var x = $(this).text();
			mylocation.push(x );
			if (! (x in locationIndex)) {
				locationIndex[x] = locCount++;
			}
		}
	});

    $(`${escapedChildTag} tbody tr td:nth-child(2)`).each( function(){
		if (!($(this).is(":hidden")) )
			system_names.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(3)`).each( function(){
		if (!($(this).is(":hidden")) )
			submitter.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(4)`).each( function(){
		if (!($(this).is(":hidden")) )
			accelerator.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(6)`).each( function(){
		if (!($(this).is(":hidden")) )
			server_accuracy.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(7)`).each( function(){
		if (!($(this).is(":hidden")) )
			server_performance.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(8)`).each( function(){
		if (!($(this).is(":hidden")) )
			offline_accuracy.push( $(this).text() );       
	});

    $(`${escapedChildTag} tbody tr td:nth-child(9)`).each( function(){
		if (!($(this).is(":hidden")) )
			offline_performance.push( $(this).text() );       
	});

    Object.entries(locationIndex).forEach(([id, index]) => {
        let tmpDict = {};
        tmpDict["id"] = id;
        tmpDict["system"] = system_names[index];
        tmpDict["submitter"] = submitter[index];
        tmpDict["accelerator"] = accelerator[index];
        if (offline_accuracy[index] !== '' && offline_accuracy[index] !== undefined) {
            tmpDict["scenario"] = "Offline";
            tmpDict["markerType"] = "circle";
            // the accuracy value is in the format " 42.0595, 19.8530, 26.7729, 1194.4000  "
            // using to fixed, returns a string, which we have to convert to float again
            tmpDict["y"] = parseFloat(parseFloat(offline_accuracy[index].trim().split(',')[0].trim()).toFixed(4));
            tmpDict["x"] = parseFloat(parseFloat(offline_performance[index].trim()).toFixed(4));
            // copy of tmpDict object is pushed to the returning array as only reference to the object is pushed
            // this results in modification of already pushed content
            extractedData.push({ ...tmpDict });
        }
        if (server_accuracy[index] !== '' && server_accuracy[index] !== undefined) {
            tmpDict["scenario"] = "Server";
            tmpDict["markerType"] = "triangle";
            // the accuracy value is in the format " 42.0595, 19.8530, 26.7729, 1194.4000  "
            tmpDict["y"] = parseFloat(parseFloat(server_accuracy[index].trim().split(',')[0].trim()).toFixed(4));
            tmpDict["x"] = parseFloat(parseFloat(server_performance[index].trim()).toFixed(4));
            extractedData.push({ ...tmpDict });
        }
    });

    // console.log(extractedData);

    return extractedData;

}