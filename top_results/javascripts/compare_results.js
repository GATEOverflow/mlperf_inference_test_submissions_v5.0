function construct_table(scenario, models, data1, data2, isPower, results1, results2) {
    let html = ``;
    html += `<thead><tr>`;
    let tableHeader = `
        <th>Model</th>
        <th>${data1}</th>
        <th>${data2}</th>
        <th>Performance Delta</th>`;

 
    if (isPower) {
        console.log(results1[0]);
        const power_unit = results1[models[0]].Power_Units;
        tableHeader += `
        <th>System 1 ${power_unit} </th>
        <th>System 2 ${power_unit}</th>
        <th>Power Delta</th>
        <th>System 1 Samples/J</th>
        <th>System 2 Samples/J</th>
        <th>Samples/J Delta</th>`;
    }
    tableHeader += `</tr>`;
    html += tableHeader + "</thead>";
    //html += `<tfoot><tr>${tableHeader}</tr></tfoot>`;

    models.forEach((row) => {
        html += "<tr>";
        html += `<td class='model'>${row}</td>`;
        const perf1 = Math.round(results1[row].Performance_Result, 1);
        const perf2 = Math.round(results2[row].Performance_Result, 1);
        let perfdelta = 0;
        if (perf2) {
            perfdelta = Math.round((1 - perf1 / perf2) * 10000) / 100;
        }
        html += `<td class="col-result">${perf1}</td>`;
        html += `<td class="col-result">${perf2}</td>`;
        html += `<td class="col-result">${perfdelta}%</td>`;

        if (isPower) {
            const pow1 = Math.round(results1[row].Power_Result, 1);
            const pow2 = Math.round(results2[row].Power_Result, 1);
            let powdelta = 0;
            let peff1 = "";
            let peff2 = "";
            let peffdelta = "";

            if (pow2) {
                powdelta = Math.round((1 - pow1 / pow2) * 10000) / 100;
            }
            if (pow1) {
                peff1 = Math.round((perf1 / pow1) * 100000) / 100000;
            }
            if (pow2) {
                peff2 = Math.round((perf2 / pow2) * 100000) / 100000;
            }
            if (peff2) {
                peffdelta = Math.round((1 - peff1 / peff2) * 10000) / 100;
            }
            html += `<td class="col-result">${pow1}</td>`;
            html += `<td class="col-result">${pow2}</td>`;
            html += `<td class="col-result">${powdelta}%</td>`;
            html += `<td class="col-result">${peff1}</td>`;
            html += `<td class="col-result">${peff2}</td>`;
            html += `<td class="col-result">${peffdelta}%</td>`;
        }
        html += "</tr>";
    });

    html += "";
    return html;
}




$( document ).on( "click", "#results_Offline thead th", function() {
    drawCompareCharts_("Offline");
});
$( document ).on( "click", "#results_Server thead th", function() {
    drawCompareCharts_("Server");
});
$( document ).on( "click", "#results_SingleStream thead th", function() {
    drawCompareCharts_("SingleStream");
});
$( document ).on( "click", "#results_MultiStream thead th", function() {
    drawCompareCharts_("MultiStream");
});


$(document).ready(function() {
    //if(!is_power) 
    {
        $('.power-content').hide();
    }
    tableSorterInit();
    $('#compareform').submit(function(event) {
        event.preventDefault(); // This will cancel the form submission

        // Your custom logic here
        //console.log('Form submission canceled.');
        var system1 = $('#system1 option:selected').text();
        var system2 = $('#system2 option:selected').text();
        var selected_models = $('#models option:selected').map(function() {
            return $(this).text();
        }).get();

        //console.log(system1);
        //console.log(system2);
        //console.log(selected_models);
        //scenario = "Offline";
        //getSummaryData();
        /*   constructTable(scenario, models, system1, system2, False, results1, results2) {

        // Optionally, you can handle the form data yourself
        */
        readAllData().then(function(allData) {
//            console.log(allData);
            sysversion1 = results_version;
            sysversion2 = results_version;
            reConstructTables(system1, sysversion1, system2, sysversion2, selected_models, allData);
        }).catch(function(error) {
            console.error(error);
        });
      }
    );

        //fetchSummaryData();
});

// scenarios, system1, sysversion1, system2, sysversion2, data, ytitle_scenarios
function reConstructTables(system1, sysversion1, system2, sysversion2, selected_models, data) {
    myscenarios = [ "Offline", "Server", "SingleStream", "MultiStream"];

    myscenarios.forEach(function(scenario) {

    let keys = ["Scenario", "Platform", "version"];
    let values = [scenario, system1, sysversion1];
    //console.log(scenario);    

    //console.log(selected_models);

    let result1 = filterData(data, keys, values);
    if(!selected_models.includes("All models")) {
        result1 = filterDataFromValues(result1, "Model", selected_models);
        console.log(result1);
        console.log(result1);
    }
    if (result1.length === 0) {
        $("#"+scenario).hide();
        //console.log(scenario +" is getting hidden")
        return; // Continue to the next scenario
    }

    values = [scenario, system2, sysversion2];
    let result2 = filterData(data, keys, values);
    if(!selected_models.includes("All models")) {
        result2 = filterDataFromValues(result2, "Model", selected_models);
    }
    //console.log(result1);
    //console.log(result2);
    if (result2.length === 0) {
        $("#"+scenario).hide();
        //console.log(scenario +" is getting hidden")
        return; // Continue to the next scenario
    }
    $("#"+scenario).show();

    let is_power = result1[0]['has_power'] && result2[0]['has_power'];
    //console.log("is_power " + is_power);

    let data1_str = `${sysversion1}: ${system1}`;
    let data2_str = `${sysversion2}: ${system2}`;
    //let ytitle = ytitle_scenarios[scenario];

    let models = [];
    let result2_models = result2.map(row => row['Model']);

    result1.forEach(function(row) {
        if (selected_models == "All models") {
            if (!models.includes(row['Model']) && result2_models.includes(row['Model'])) {
                models.push(row['Model']);
            }
        }
        else {
            if (!models.includes(row['Model']) && result2_models.includes(row['Model']) && selected_models.includes(row['Model']) ) {
                models.push(row['Model']);
            }
        }
    });

    let results1 = {};
    let results2 = {};

    models.forEach(function(model) {
        results1[model] = result1.find(row => row['Model'] === model);
        results2[model] = result2.find(row => row['Model'] === model);
    });

    //console.log(results1);
    //console.log(results2);
    $("#table_header_"+scenario).text(`Comparing ${scenario} scenario for ${data1_str} and ${data2_str}`);
    //is_power = (result2[0]['has_power'])
    //is_power = false
    //console.log(scenario);    
        
    data1[scenario] = data1_str, data2[scenario] = data2_str, draw_power[scenario] = is_power, draw_power_efficiency[scenario] = is_power;

    let htmltable = construct_table(scenario, models, data1_str, data2_str, is_power, results1, results2);
    html = htmltable;
    if(is_power) {
        $('.power-content').show();
    }
    else{
        $('.power-content').hide();
    }

    //console.log(html);

    // Assuming you want to append this HTML to a specific element on your page
    var elemId = "results_" + scenario
    //console.log(elemId);
    document.getElementById(elemId).innerHTML = html;
    $('table').tablesorter();
    var resort = true, // re-apply the current sort
        callback = function() {
          // do something after the updateAll method has completed
        };

      // let the plugin know that we made a update, then the plugin will
      // automatically sort the table based on the header settings
      $("table").trigger("updateAll", [ resort, callback ]);
    drawCompareCharts();
});
}
