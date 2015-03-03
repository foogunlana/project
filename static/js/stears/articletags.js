$(document).ready(function(){
	$('.tag_button').click(function(event){
        
        if(!confirm( "Do you want to delete this tag?" )){
            event.preventDefault();
            return false;
        }

        var self = $(this);

        $.ajax({
            type: "post",
            url: $(this).data('url'),
            data: {
                'data':$(this).data('tag'),
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    alert(responseData);
                    self.parent().remove();
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
    });

});
