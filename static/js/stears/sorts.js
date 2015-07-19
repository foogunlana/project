$( document ).ready(function() {
	$('.article_button_sorter').change(function() {

		$('.article_button').each(function(){
				$(this).parent().show();
			});

		var sorts = [];
		$('.article_button_sorter').each(function(){
			sorts.push($(this).val());
		});

		sorts.map(function(sort){
			if(sort==='all'){
				return false;
			} else{
				$('.article_button').each(function(){
					if(!$(this).hasClass(sort)){
						$(this).parent().hide();
					}
				});
			}
		});
	});

	$('.onsite_filter').click(function(event) {
		event.preventDefault();
		var filter = $(this).data('filter');
		$('#onsite_sorter').val(filter).change();
	});
});
