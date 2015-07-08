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

	$(".edit_photo_form").submit(function(event){
		event.preventDefault();
		var pk = this.pk.value;
		
		var edit_photo_url = $(this).data('url');
		formData = {
			'pk': pk,
			'title': this.title.value,
			'source': this.source.value,
			'description': this.description.value,
		};

		$.ajax({
		url : edit_photo_url,
        type: "post",
        data: formData,

        success: function(responseData, textStatus, jqXHR) {
            var msg = JSON.parse(responseData);
            if(msg.success){
				var pk = msg.pk;
				$('.photo_' + pk + '_description').text(msg.kwargs.description);
				$('.photo_' + pk + '_title').text(msg.kwargs.title);
				$('.photo_' + pk + '_source').text(msg.kwargs.source);
			}else{
				var keys = Object.keys(msg.errors);
                message = '';
                for(i = 0; i < keys.length; i++){
                    message += '('+ keys[i] + ')' + ': ' + msg.errors[keys[i]] + '\n';
                }
                alert(message);
			}
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert(errorThrown);
        },});

    return false;

	});

});
