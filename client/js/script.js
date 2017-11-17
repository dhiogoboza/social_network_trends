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
    var options = {};

    var chart = new google.visualization.GeoChart(document.getElementById('gchart'));

    chart.draw(data, options);
}

function updateLayout($container) {
    $container.css("height", ($(window).height() - $container.offset().top - 40) + "px");
}

function showReachChart() {
    requestData("reach", "subject=" + $("#reach-subject").val(), function(json) {
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
    
    for (var i = 0; i < json.length; i++){
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
        'packages': ['geochart'],
        // Note: you will need to get a mapsApiKey for your project.
        // See: https://developers.google.com/chart/interactive/docs/basic_load_libs#load-settings
        'mapsApiKey': 'AIzaSyA3yqnlgXnfqj3Los7Rn2S6Ncs6t8z8Pxk'
    });

    //google.charts.setOnLoadCallback(drawRegionsMap);*/
    
});
