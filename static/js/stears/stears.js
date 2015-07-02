

$( document ).ready(function() {

    $('body').each(function(){
        var $bgobj = $(this); // assigning the object
        var xPos = $(this).css('backgroundPosition').split(' ')[0];
        $(window).scroll(function() {
            var yPos = -($(window).scrollTop() / 10*$bgobj.data('speed'));
            // Put together our final background position
            var coords = xPos + ' ' + yPos + 'px';
            // Move the background
            $bgobj.css({ backgroundPosition: coords });
        });
    });


	$( ".confirm-submission" ).click(function( event ) {
		if(!confirm( "Are you sure you want to do this?" )){
			event.preventDefault();
			console.log('prevent');
		}
	});

	$( ".confirm-revive" ).click(function( event ) {
		if(!confirm( "Are you sure you want to revive this article" )){
			event.preventDefault();
		}
	});

	$(".cancel_button").click(function (event) {
		event.preventDefault();
		ajax = $.ajax().abort();
		return false;
	});

	$('.standard-choice').click(function() {
		$('.other-choice').val('None');
	});

	$( ".delete" ).click(function( event ) {
		if(!confirm( "Are you sure you want to delete?" )){
			event.preventDefault();
		}
	});
	
	$('#btn').click(function() {
		$('#wizard').toggle();
	});

	$('#comment_area_button').click(function() {
		$('#comment_area').toggle();
		$('#comment_form').focus();
		$('#keyword_area').hide();
	});

	$('#article_form_toggle').click(function() {
		$('#hidden_article_form').toggle();
	});

	$('#keyword_area_button').click(function() {
		$('#keyword_area').toggle();
		$('#id_tags').focus();
		$('#comment_area').hide();
	});

	$('.comment_body_toggle').click(function(){
		var id = $(this).attr('id');
		$("#summary".concat(id.toString())).toggle();
		$("#body".concat(id.toString())).toggle();
		return false;
	});

	$('.toggles_div').click(function() {
		var div_class = $(this).attr('id');
		var the_div = ".".concat(div_class.toString());
		$(the_div).toggle();
		$('html, body').animate({ scrollTop: $(the_div).offset().top - 100}, 'fast');
	});

	$('.toggles_div2').click(function() {
		var div_class = $(this).attr('id');
		var the_div = ".".concat(div_class.toString());
		if($(the_div).is(':visible')){
			$(the_div).hide();
		} else {
			var group_class = $(this).data('group');
			var the_group = ".".concat(group_class.toString());
			$(the_group).each(function(){
				$(this).hide();
			});
			$(the_div).show();
		}
		$('html, body').animate({ scrollTop: $(the_div).offset().top - 100}, 'fast');
	});

	$('.toggles_on_hover').hover(function() {
		var div_class = $(this).attr('id');
		$(".".concat(div_class.toString())).toggle();
	});

});