$(document).ready(function(event){
	$(".delete_photo_form").submit(function(event){
		event.preventDefault();
		var pk = this.pk.value;
		var delete_photo_url = $(this).data('url');

		$.ajax({
		url : delete_photo_url,
        type: "post",
        data: {'pk':pk},

        success: function(responseData, textStatus, jqXHR) {
            var msg = JSON.parse(responseData);
            if(msg.success){
				var pk = msg.pk;
				$('#photo_' + pk).remove();
			}else{
				alert('Error: ' + msg.errors);
			}
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
        },});

    return false;

	});

});
