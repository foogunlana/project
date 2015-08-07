$(document).ready(function(){
	$('.weal_ajax_form').submit(function(event){
		event.preventDefault();
		var data = JSON.parse(JSON.stringify($(this).serializeArray()));
		var result = $(this).data('result');
		var alertmsg = $(this).data('alert');
		if(alertmsg){
			alert(alertmsg);
		}

		$.ajax({
			url : this.action,
			type: this.method,
			data: data,
			success: function(responseData, textStatus, jqXHR) {
				msg = JSON.parse(responseData);
				if(msg.message){
					alert(msg.message);
				}
				if(msg.success){
					if(msg.result){
						var update = msg.result;
						for(var prop in update){
							$('#' + result).text(update[prop]);
						}
					}
				}else{

				}
			},
			error: function(jqXHR, textStatus, errorThrown) {
			console.log("error");
			}
		});
		return false;
    });
});