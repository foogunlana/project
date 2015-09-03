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
					if(msg.message instanceof Object ){
						var keys = Object.keys(msg.message);
						message = '';
						for(i = 0; i < keys.length; i++){
							message += '('+ keys[i] + ')' + ': ' + msg.message[keys[i]] + '\n';
						}
						alert(message);
					}else{
						alert(JSON.stringify(msg.message));
					}
				}
				if(msg.success){
					if(msg.result){
						var update = msg.result;
						for(var prop in update){
							$('#' + result).text(update[prop]);
							$('#' + result).addClass('updated');
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