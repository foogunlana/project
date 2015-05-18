$(document).ready(function(){
	$('.section').click(function(event){
		if($(this).hasClass('highlighted')){
			$(this).removeClass('highlighted');
		}else{
			$('.highlighted').each(function(){
				$(this).removeClass('highlighted');
			});
			$(this).addClass('highlighted');
			if(!$(this).hasClass('choose_article')){
				return false;
			}else{
				$('#id_article_options').focus();
			}
		}
	});

	$('.submit_article_option').click(function(){
		if(!$('.highlighted').hasClass('choose_article')){
			return false;
		}
		var section = $('.highlighted').data('title');
		var article_id = $('#id_article_options').val();
		var allocator_url = $('#id_article_options').data('url');
		var allocator_page = $('.highlighted').parent().data('page');

		if((!section)||(!article_id)||(article_id==='None')){
			alert('Please select a section and an article to allocate');
			return false;
		}else{
			$.ajax({
			url : allocator_url,
            type: "post",
            data: {
                'article_id':article_id,
                'page':allocator_page,
                'section':section,
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    alert(responseData);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
		}
	});
});