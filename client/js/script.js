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

function openChart(chart) {
    $.ajax({
        url: "http://localhost:8080/charts/" + chart + ".html",
        type: 'GET',
        success: function(result){
            $mainContent.html(result);
    }});
}

function requestData(type, data, callback) {
    $.ajax({
        url: "http://localhost:8080",
        type: "POST",
        dataType: "json",
        data: "type=" + type + "&" + data,
        success: function(result) {
            //$("#chart-result").attr("src", "data:image/png;base64," + result);
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
        
        
        /*var data = google.visualization.arrayToDataTable([
            ['Country', 'Popularity'],
            ['Germany', 200],
            ['United States', 300],
            ['Brazil', 400],
            ['Canada', 500],
            ['France', 600],
            ['RU', 700]
        ]);*/
        
        var data = new google.visualization.DataTable(json);
        
        drawRegionsMap(data);
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
        
        openChart($selectedMenu.attr("id"));
        
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