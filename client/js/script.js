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

function showSubjectInPlacesHistoryChart() {
    var start_date = $("#starts").val();
    var end_date = $("#ends").val();

    requestData("subjectinplaceshistory", "subject=" + $("#subject").val() +
            "&starts=" + start_date + "&ends=" + end_date, function(json) {
        updateLayout($("#gchart"), 50);
        
        var start = new Date(start_date).convertToUTC();
        var end = new Date(end_date).convertToUTC();
        
        var date_str;
        var dates = [];
        while (start <= end) {
            date_str = start.formatString("D-m-YYYY");
            
            if (date_str in json && json[date_str]["rows"].length > 0) {
                dates.push(start);
            }
            
            var startClone = new Date(start);
            start = new Date(startClone.setUTCDate(startClone.getUTCDate() + 1));
        }
        
        $("#timeline").timeline({
            dates: dates,
            onSelection: function(date) {
                updateLayout($("#gchart"), 50);
                var data = new google.visualization.DataTable(json[date]);
                drawRegionsMap(data);
            }
        });
    });
}

function showSubjectInPlacesChart() {
    requestData("subjectinplaces", "subject=" + $("#subject").val(), function(json) {
        updateLayout($("#gchart"));
        
        var data = new google.visualization.DataTable(json);
        drawRegionsMap(data);
    });
}

function showAllSubjectsInPlace() {
    requestData("subjectsinplace", "location=" + $("#location").val(), function(json) {
        updateLayout($("#gchart"));
        
        console.log(json);
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
    
    $(document)
        .ajaxStart(function(){
            $("#loader").show();
        })
        .ajaxStop(function(){
            $("#loader").hide();
        });
});
