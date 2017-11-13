var configs = {
    sidebar: "#mySidebar",
    overlay: "#myOverlay",
    main: ".w3-main",
    menu: ".w3-bar-block",
    menuWidth: "300px",
    menuSelector: 'w3-blue'
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

function open(option, path) {
    $.ajax({
        url: "/" + path + "/" + option + ".html",
        type: 'GET',
        success: function(result){
            $mainContent.html(result);
    }});
}

function requestData(type, data, callback) {
    $.ajax({
        url: "/data",
        type: "POST",
        dataType: "json",
        data: "type=" + type + "&" + data,
        success: function(result) {
            callback(result);
        },
        error: function(xhr, error) {
            console.log(error);
            console.log(xhr);
        }
    });
}

function drawRegionsMap(data) {
    var options = {};

    var chart = new google.visualization.GeoChart(document.getElementById('gchart'));

    chart.draw(data, options);
}

function updateLayout() {
    var $gchart = $("#gchart");
    
    $gchart.css("height", ($(window).height() - $gchart.offset().top - 40) + "px");
}

function showReachChart() {
    requestData("reach", "subject=" + $("#reach-subject").val(), function(json) {
        updateLayout();
        
        var data = new google.visualization.DataTable(json);
        
        drawRegionsMap(data);
    });
}

function showLocations() {
    requestData("locations", "", function(json) {
        var $locations_table = $("#locations_table");
        console.log(json)
        
        $("tr:not(first)", $locations_table).remove();
    });
}

$(function() {
    $mySidebar = $(configs.sidebar);
    $overlayBg = $(configs.overlay);
    $mainContent = $(configs.main);
    $selectedMenu = $(configs.menu + " ." + configs.menuSelector);
    
    $(configs.menu + ' a:not(.w3-hide-large)').on("click", function () {
        $selectedMenu.removeClass(configs.menuSelector);
        $selectedMenu = $(this);
        
        open($selectedMenu.attr("id"), $selectedMenu.data("path"));
        
        $selectedMenu.addClass(configs.menuSelector);
    });
    
    
    google.charts.load('current', {
        'packages': ['geochart'],
        // Note: you will need to get a mapsApiKey for your project.
        // See: https://developers.google.com/chart/interactive/docs/basic_load_libs#load-settings
        'mapsApiKey': 'AIzaSyA3yqnlgXnfqj3Los7Rn2S6Ncs6t8z8Pxk'
    });

    //google.charts.setOnLoadCallback(drawRegionsMap);*/
    
});
