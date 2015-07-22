var get_main_features = function(){
	$('#top-gif-loader').show();
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
	$('#features-gif-loader').show();
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

   (function($) {
		if($(window).width() < 991){
			return false;
		}
		var element = $('.follow-scroll'),
			originalY = element.offset().top + 250;

		// Space between element and top of screen (when scrolling)
		var topMargin = 0;

		// Stop at end of article content
		var par = $('.article-paragraph');
		var stop = par.offset().top + par.outerHeight() - 200;

		// Should probably be set in CSS; but here just for emphasis
		element.css('position', 'relative');
		var lastScrollTop = 0;
		$(window).on('scroll', function(event) {
			var st = $(window).scrollTop();
			if (st > lastScrollTop){
			// downscroll code
				var scrollTop = st - (element.outerHeight() - $(window).height());

				// if(((scrollTop + element.outerHeight()) < stop) && (Math.abs(scrollTop - element.position().top) > 30)){
				if(((scrollTop + element.outerHeight()) < stop)){
					element.stop(false, false).animate({
						top: scrollTop < originalY ? 0: scrollTop - originalY
					}, 400);
				}
			} else {
			// upscroll code

				// if(((st + element.outerHeight()) < stop) && (Math.abs(st - element.position().top) > 30)){
				if(((st + element.outerHeight()) < stop)){
					element.stop(false, false).animate({
						top: st < originalY ? 0: st - originalY
					}, 400);
				}
			}
			lastScrollTop = st;
		});
	})(jQuery);

});