var get_main_features = function(){
	$('.gif-loader').show();
	$.ajax({
	url : '/articles/mfeatures/',
    type: "get",
    data: {},

    success: function(responseData, textStatus, jqXHR) {
        msg = JSON.parse(responseData);
        if(msg.success){
			main_features = msg.articles;
			for(var i = 0; i < main_features.length; i++){
				if(main_features[i] != null){
					var mfo = main_features[i];
					var mf = $('#example_main_feature').clone(true);
					mf.removeAttr('id');
					var summary = mf.find('.top-story-summary');
					var link = '/article/10' + mfo.article_id.toString();

					var headline = '<a href=' + '"' + link + '"' + '>'
									+ mfo.headline + '</a>';
					mf.find('.top-story-headline').html(headline);
					if(i === 0){
						summary.text(mfo.par1.slice(0, 150) + '...');
					}else{
						summary.text(mfo.par1.slice(0, 50) + '...');
					}	
					mf.appendTo('.top-stories-body');
					$('.gif-loader').hide();
				}
			}
			$('#example_main_feature').remove();
        }else{
			alert('Failed');
        }
    },
		error: function(jqXHR, textStatus, errorThrown) {
			alert(errorThrown);
		},
	});
    return false;
};

var get_features = function(){
	$('.gif-loader').show();
	$.ajax({
	url : '/articles/homefeatures/',
    type: "get",
    data: {},

    success: function(responseData, textStatus, jqXHR) {
        msg = JSON.parse(responseData);
        if(msg.success){
			features = msg.articles;
			for(var i = 0; i < features.length; i++){
				if(features[i] != null){
					var fo = features[i];
					var f = $('#example_feature').clone(true);
					f.removeAttr('id');
					var summary = f.find('.feature-summary');
					var link = '/article/10' + fo.article_id.toString();

					var headline = '<a href=' + '"' + link + '"' + '>'
									+ fo.headline + '</a>';
					f.find('.feature-headline').html(headline);
					f.find('img').attr('src', fo.photo);
					if(i === 0){
						summary.text(fo.par1.slice(0, 150) + '...');
					}else{
						summary.text(fo.par1.slice(0, 50) + '...');
					}	
					f.appendTo('.features-body');
					$('.gif-loader').hide();
				}
			}
			$('#example_feature').remove();
        }else{
			alert('Failed');
        }
    },
		error: function(jqXHR, textStatus, errorThrown) {
			alert(errorThrown);
		},
	});
    return false;
};



$(document).ready(function(){
   $($('.article-paragraph').find('a')).attr('target', '_blank');
   $('.article-paragraph').find('.hidden-s').html('<em>Stears</em>');

   get_main_features();
   $('.top-story').click(function(event){
		event.preventDefault();
		var link = $(this).find('a').attr('href');
		window.open(link, '_self');
   });

   get_features();
   $('.feature').click(function(event){
		event.preventDefault();
		var link = $(this).find('a').attr('href');
		window.open(link, '_self');
   });
});