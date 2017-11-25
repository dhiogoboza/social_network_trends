/**
 * Created by dhiogoboza on 24/11/17.
 * From: TODO: publish
 * A jquery plugin to create a simple horizontal timeline.
 */
 Date.prototype.formatString = (function() {
    if (arguments.length < 1) {
        return "";
    }
    
    var format = arguments[0];
    // TODO: use format
    var str = this.getUTCDate() + "-" + (this.getUTCMonth() + 1) + "-" + this.getUTCFullYear();
    
    return str;
});

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

Date.prototype.convertToUTC = (function() { 
    return new Date(this.getUTCFullYear(), this.getUTCMonth(), this.getUTCDate(), this.getUTCHours(), this.getUTCMinutes(), this.getUTCSeconds()); 
});

Array.prototype.contains = (function () {
    if (arguments.length < 2) {
        console.log("Array.prototype.contains requires two arguments");
        return false;
    }
    
    for (var i = 0, len = this.length; i < len; i++) {
        if (arguments[1](this[i], arguments[0])) {
            return true;
        }
    }

    return false;
});

(function ($) {
    
    $.fn.timeline = function (options) {
        var settings = $.extend({
            start_date: undefined,
            end_date: undefined,
            dates: null,
            main_class: "hr-timeline",
            items_container_class: "items-container",
            items_class: "item",
            circle_class: "circle",
            circle_selected_class: "selected"
        }, options );
        
        function date_comparator(date1, date2) {
            return date1.getUTCDate() == date2.getUTCDate() &&
                    date1.getUTCMonth() == date2.getUTCMonth() &&
                    date1.getUTCFullYear() == date2.getUTCFullYear();
        }
        
        return this.each(function() {
            var $this = $(this);
            var items = [];
            var current = 0;
            var oldWidth = 0;
            var first = true;
            var $line;
            
            function selectDate($item) {
                // Remove selction class from last circle
                $("#item-" + items[current]).removeClass(settings.circle_selected_class);
                current = $item.data("index");
                updateSelectedItem();
            }
            
            function addItem($items_container, date, index) {
                var str_date = date? date.formatString("D-m-YYYY") : "";
                
                var $item = $("<div/>").addClass(settings.items_class);
                
                if (date) {
                    var $circle = $("<span/>")
                            .attr("title", str_date)
                            .addClass(settings.circle_class)
                            .attr("id", "item-" + str_date)
                            .data("index", index)
                            .on("click", function() {
                                selectDate($(this));
                            });
                            
                    $item.append($circle);
                    items.push(str_date);
                } else {
                    $item.append($("<div/>").html("a").css("visibility", "hidden"));
                }
                
                $items_container.append($item);
            }
            
            function init() {
                $this.empty().addClass(settings.main_class);
                
                var index = 0;
                var $items_container = $("<div/>").addClass(settings.items_container_class);
                
                if (settings.start_date && settings.end_date) {
                    var start = settings.start_date;
                    var end = settings.end_date;
                    while (start <= end) {
                        addItem($items_container, start, index);
                        
                        var startClone = new Date(start);
                        start = new Date(startClone.setUTCDate(startClone.getUTCDate() + 1));
                        index++;
                    }
                } else {
                    var start = settings.dates[0];
                    var end = settings.dates[settings.dates.length - 1];
                    
                    console.log(start);
                    console.log(end);
                    
                    console.log("\n\n");
                    
                    while (start <= end) {
                        var date = settings.dates.contains(start, date_comparator)? start : null;
                        
                        addItem($items_container, date, index);
                        
                        var startClone = new Date(start);
                        start = new Date(startClone.setUTCDate(startClone.getUTCDate() + 1));
                        
                        if (date) {
                            index++;
                        }
                    }
                }
                
                var $line_bg = $("<div/>").addClass("line-bg");
                $line = $("<div/>").addClass("line");
                
                $this.append($line_bg);
                $this.append($line);
                $this.append($items_container);
            }
            
            function updateSelectedItem() {
                var $current = $("#item-" + items[current]);
                var offset = $("." + settings.items_container_class + " ." + settings.circle_class).width() / 2;
                var width = offset + $current.offset().left - $line.offset().left;
                
                if (first) {
                    $line.css('width', width);
                    
                    first = false;
                    oldWidth = width;
                    
                    $current.addClass(settings.circle_selected_class);
                    options.onSelection(items[current]);
                } else {
                    var ds = Math.abs(oldWidth - width);
                    $line.animate({
                        'width': width
                    }, ds, function() {
                        first = false;
                        oldWidth = width;
                        
                        $current.addClass(settings.circle_selected_class);
                        options.onSelection(items[current]);
                    });
                }
            }
            
            init();
            updateSelectedItem();
        });
    };
})(jQuery);

