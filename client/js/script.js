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
        
        $mainContent.css("margin-left", "0px");
    } else {
        $mySidebar.show();
        $overlayBg.show();
        
        $mainContent.css("margin-left", configs.menuWidth);
    }
}

function openChart(chartId) {
    switch (chartId) {
        case "reach":
            requestData("reach", function() {
                alert('asd')
            })
            break;
    }
}

function requestData(type, callback) {
    $.ajax({
        url: "http://localhost:8080",
        type: 'POST',
        data: "type=" + type,
        success: function(result){
            $mainContent.html(result);
            callback();
    }});
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
    
    
    
});