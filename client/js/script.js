var configs = {
    sidebar: "#mySidebar",
    overlay: "#myOverlay",
    main: ".w3-main",
    menu: ".w3-bar-block",
    menuWidth: "300px",
    menuSelector: "w3-blue",
	serverUrl: "http://localhost:8080"
}

var $mySidebar, $overlayBg, $mainContent, $selectedMenu;

function toggleMenu() {
    if ($mySidebar.css("display") === 'block') {
        $mySidebar.hide();
        $overlayBg.hide();
    } else {
        $mySidebar.show();
        $overlayBg.show();
    }
}

function open(path) {
    $.ajax({
        url: "/" + path,
        type: 'GET',
        success: function(result){
            $mainContent.html(result);
    	},
		error: function(xhr, status, error) {
            console.log(error + " - " + status);
        }
	});
}

function requestData(type, data, callback) {
    $.ajax({
        url: configs.serverUrl + "/data",
        type: "POST",
        dataType: "json",
        data: "type=" + type + "&" + data,
        success: function(result) {
            callback(result);
        },
        error: function(xhr, status, error) {
            console.log(error + " - " + status);
        }
    });
}

function drawRegionsMap(data) {
    var container = document.getElementById('gchart');
    
    console.log(container.clientWidth)
    
    var options = {};
    options['dataMode'] = 'regions';
    options['width'] = container.clientWidth;
    options['height'] = container.clientHeight;
    
    //var chart = new google.visualization.GeoChart(document.getElementById('gchart'));
    //chart.draw(data, options);
    
    var geomap = new google.visualization.GeoMap(container);
    geomap.draw(data, options);
    
    return geomap;
}

function updateLayout($container, offset) {
    $container.css("height", ($(window).height() - $container.offset().top - 40 - offset) + "px");
}

function updateLayout($container) {
    $container.css("height", ($(window).height() - $container.offset().top - 40) + "px");
}

function convertDateToUTC(date) { 
    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds()); 
}

function showSubjectInPlacesHistoryChart() {
    var start_date = $("#starts").val();
    var end_date = $("#ends").val();

    requestData("subjectinplaceshistory", "subject=" + $("#subject").val() +
            "&starts=" + start_date + "&ends=" + end_date, function(json) {
        updateLayout($("#gchart"), 50);
        
        //console.log(json);
        
        for (var key in json){
            var value = json[key];
            console.log(key);
            //console.log(value);
        }
        
        var start = convertDateToUTC(new Date(start_date));
        var end = convertDateToUTC(new Date(end_date));
        
        $("#timeline").timeline({
            start_date: start,
            end_date: end,
            onSelection: function(date) {
                updateLayout($("#gchart"), 50);
                var data = new google.visualization.DataTable(json[date]);
                drawRegionsMap(data);
            }
        });

        /*while(start <= end){
           console.log(start.getDate() + "-" + (start.getMonth() + 1) + "-" + start.getFullYear());

           var newDate = start.setDate(start.getDate() + 1);
           start = new Date(newDate);
        }*/
        
        //var data = new google.visualization.DataTable(json);
        //drawRegionsMap(data);
    });
}


function showSubjectInPlacesChart() {
    requestData("subjectinplaces", "subject=" + $("#subject").val(), function(json) {
        updateLayout($("#gchart"));
        
        var data = new google.visualization.DataTable(json);
        drawRegionsMap(data);
    });
}

function scrollToParent(parentId) {
    var $container = $('.container');
    var offset = $container.offset().top;
    
    $container.animate({
        scrollTop: $("#" + parentId).offset().top - offset - 40
    }, 200);
}

function refreshLocations() {
    requestData("refreshlocations", "", function(json) {
        showLocations(json);
    });
}

function loadLocations() {
    requestData("locations", "", function(json) {
        showLocations(json);
    });
}

function showLocations(json) {
    var $locations_table = $("#locations_table");
    $("tr:gt(0)", $locations_table).remove();
    
    for (var i = 0; i < json.length; i++) {
      var obj = json[i];
      
      $tr = $("<tr />").html("<td><a id=" + obj["woeid"] +
            "></a>" + obj["woeid"] + "</td>" +
            "<td>" + obj["name"] + "</td>" +
            "<td>" + obj["countryCode"] + "</td>" +
            "<td>" + obj["country"] + "</td>" +
            "<td>" + (obj["parentid"] !== "0"? "<a onClick='scrollToParent(\"" + obj["parentid"] + "\")' href='#'>" : "") +
            obj["parentid"] + (obj["parentid"] !== "0"? "</a>" : "") + "</td>"
      );
      
      $locations_table.append($tr);
    }
}

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

$(function() {
    $mySidebar = $(configs.sidebar);
    $overlayBg = $(configs.overlay);
    $mainContent = $(configs.main);
    $selectedMenu = $(configs.menu + " ." + configs.menuSelector);
    
    $(configs.menu + ' a:not(.w3-hide-large)').on("click", function (e) {
        $selectedMenu.removeClass(configs.menuSelector);
        $selectedMenu = $(this);
        
        open($selectedMenu.attr("href"));
        
        $selectedMenu.addClass(configs.menuSelector);
        
        e.preventDefault();
    });
        
    google.charts.load('current', {
        'packages': ['geochart', 'geomap'],
        // Note: you will need to get a mapsApiKey for your project.
        // See: https://developers.google.com/chart/interactive/docs/basic_load_libs#load-settings
        'mapsApiKey': 'AIzaSyA3yqnlgXnfqj3Los7Rn2S6Ncs6t8z8Pxk'
    });

    //google.charts.setOnLoadCallback(drawRegionsMap);*/
    
});
