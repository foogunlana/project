

$( document ).ready(function() {
	$( ".confirm-submission" ).click(function( event ) {
		if(!confirm( "Are you sure you want to post" )){
			event.preventDefault();
		};
	});

	$('.standard-choice').click(function() {
		$('.other-choice').val('None');
	});

	$( ".delete" ).click(function( event ) {
		if(!confirm( "Are you sure you want to delete?" )){
			event.preventDefault();
		};
	});
	
	$('#btn').click(function() {
		$('#wizard').toggle();
	});

	$('#comment_area_button').click(function() {
		$('#comment_area').toggle();
		$('#keyword_area').hide();
	});

	$('#article_form_toggle').click(function() {
		$('#hidden_article_form').toggle();
	});

	$('#keyword_area_button').click(function() {
		$('#keyword_area').toggle();
		$('#comment_area').hide();
	});

	$('.comment_body_toggle').on('click',function(){
		var id = $(this).attr('id');
		$("#summary".concat(id.toString())).toggle();
		$("#body".concat(id.toString())).toggle();
		return false;
	});

	$('.toggles_div').click(function() {
		var div_class = $(this).attr('id');
		$(".".concat(div_class.toString())).toggle();
	});

	$('.toggles_on_hover').hover(function() {
		var div_class = $(this).attr('id');
		$(".".concat(div_class.toString())).toggle();
	});

});