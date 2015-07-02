$(document).ready(function(){
	$.validator.addMethod("tagRegex", function(value, element) {
	return this.optional(element) || ($('#id_tags').val() != 'None') || (/^\w[\w\-\s]+$/i.test(value) && (value != 'None'));
	}, "Please choose a tag, or create one");

	$("#tag_form").validate({
		rules: {
			"other": { tagRegex: true},
		},
	});

	$('#tag_form').submit(function(event){
		event.preventDefault();

		var formData = {
			'tags': this.tags.value,
			'other': this.other.value
		};

		$.ajax({
            type: "post",
            url: $(this).data('url'),
            data: formData,
            success: function(responseData, textStatus, jqXHR) {
                var msg = JSON.parse(responseData);
                if(msg.success){
					var tag = msg.tag;
					var tag_clone = $('#example_tag').clone(true);
					tag_clone.find('a').attr('data-tag', tag);
					tag_clone.find('a').text(tag);
					tag_clone.prependTo('.tag_container');
				}
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
	});

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
                'tag':$(this).data('tag'),
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    // alert(responseData);
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