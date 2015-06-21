$(document).ready(function(){
	$('.section').click(function(event){
		var quote_form = $('.toggle_quote_form');
		if(quote_form.is(':visible') && !$(this).hasClass('quote_entry')){
			quote_form.toggle();
		}
		if($(this).hasClass('highlighted')){
			$(this).removeClass('highlighted');
		}else{
			$('.highlighted').each(function(){
				$(this).removeClass('highlighted');
			});
			if(!$(this).hasClass('derived')){
				$(this).addClass('highlighted');
			}
			if(!$(this).hasClass('choose_article')){
				return false;
			}else{
				$('#id_article_options').focus();
			}
		}
	});

	$('.submit_article_option').click(function(){
		if(!$('.highlighted').hasClass('choose_article')){
			alert('You have not chosen a valid position on the site');
			return false;
		}

		var category = $(this).data('cat');
		var cat_id = '#id_article_options_' + category;
		
		var section = $('.highlighted').data('title');
		var article_id = $(cat_id).val();
		var allocator_url = $(cat_id).data('url');
		var allocator_page = $('.highlighted').parent().data('page');

		if((!section)||(!article_id)||(article_id==='None')){
			alert('Please select a section and an article to allocate');
			return false;
		}else{
			if(!confirm('Put this article in ' + section + '?')){
				return false;
			}
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
		var new_quote_url = $('#new_quote').data('url');
		var quote = $('#id_quote').val();
		var author = $('#id_author').val();

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

	});
});