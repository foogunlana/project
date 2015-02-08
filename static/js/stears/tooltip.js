$(document).ready(function() {
// Tooltip only Text
	$('.standard-choice').each(function(){
		tipId = "#" + $(this).attr('id') + "_stearsTips";
		$(tipId).attr('title',$(this).attr('title'));
		$(this).removeAttr('title');
	});

	$('.masterTooltip').hover(function(){
	// Hover over code
		var title = $(this).attr('title');
		$(this).data('tipText', title).removeAttr('title');
		$('<div class="tooltip"></div>')
		.html(title)
		.appendTo('body')
		.fadeIn('slow');
	}, function() {
	// Hover out code
		$(this).attr('title', $(this).data('tipText'));
		$('.tooltip').remove();
		}).mousemove(function(e) {
		var mousex = e.pageX + 20; //Get X coordinates
		$('.tooltip')
		.css({ top: 200, left: mousex });
	});
});