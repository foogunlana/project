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

	$('.submit_quote').click(function(event){
		event.preventDefault();
		if(!$('.highlighted').hasClass('quote_entry')){
			alert('Please reselect the quote option first');
			return false;
		}
		var section = $('.highlighted').data('title');
		var new_quote_url = $('#new_quote').data('url');
		var quote = $('#id_quote').val();
		var author = $('#id_author').val();
		if(section != 'quote'){
			alert('Please reselect the quote option first');
			return false;
		}else{
			$.ajax({
			url : new_quote_url,
            type: "post",
            data: {
                'quote':quote,
                'author':author,
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