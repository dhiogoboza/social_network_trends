/**
 * Created by dhiogoboza on 24/11/17.
 * From: TODO: publish
 * A jquery plugin to create a simple horizontal timeline.
 */
;(function ($) {
    $.fn.timeline = function (options) {
        return this.each(function() {
            var $this = $(this);
            var items = [];
            var current = 0;
            var oldWidth = 0;
            var first = true;
            var $line;
            
            function selectDate($item) {
                $("#item-" + items[current] + " span").removeClass("selected");
                current = $item.data("index");
                updateSelectedItem();
            }
            
            function init() {
                $this.empty().addClass("hr-timeline");
                var start = options.start_date;
                var end = options.end_date;
                var index = 0;
                var $items_container = $("<div/>").addClass("items-container");
                
                console.log("start: " + start);
                console.log("end: " + end);
                
                while(start <= end){
                    var date = start.getDate() + "-" + (start.getMonth() + 1) + "-" + start.getFullYear();
                    console.log("date: " + date);

                    var $item = $("<div/>").addClass("item")
                            .on("click", function() {
                                selectDate($(this));
                            })
                            .attr("id", "item-" + date)
                            .data("date", date)
                            .data("index", index);

                    $item.append($("<span/>").attr("title", date).addClass("circle"));
                    $items_container.append($item);

                    items.push(date);

                    start = new Date(start.setDate(start.getDate() + 1));
                    index++;
                }
                
                var $line_bg = $("<div/>").addClass("line-bg");
                $line = $("<div/>").addClass("line");
                
                $this.append($line_bg);
                $this.append($line);
                $this.append($items_container);
            }
            
            function updateSelectedItem() {
                var $current = $("#item-" + items[current]);
                var offset = $(".items-container .item").width() / 2;
                var width = offset + $current.offset().left - $line.offset().left;
                
                if (first) {
                    $line.css('width', width);
                    
                    first = false;
                    oldWidth = width;
                    
                    $("span", $current).addClass("selected");
                    options.onSelection(items[current]);
                } else {
                    var ds = Math.abs(oldWidth - width);
                    $line.animate({
                        'width': width
                    }, ds, function() {
                        first = false;
                        oldWidth = width;
                        
                        $("span", $current).addClass("selected");
                        options.onSelection(items[current]);
                    });
                }
            }
            
            init();
            updateSelectedItem();
        });
    };
})(jQuery);

