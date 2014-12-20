

$( document ).ready(function() {
	$( ".confirm-submission" ).click(function( event ) {
		if(!confirm( "Are you sure you want to post" )){
			event.preventDefault();
		};
	});
	
	$('#btn').click(function() {
		$('#wizard').toggle();
	});

	$('#comment_area_button').click(function() {
		$('#comment_area').toggle();
	});

	$('.comment_body_toggle').on('click',function(){
		var id = $(this).attr('id')
		$("#summary".concat(id.toString())).toggle();
		$("#body".concat(id.toString())).toggle();
		return false;
	});

});