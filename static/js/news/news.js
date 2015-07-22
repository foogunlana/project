
$(document).ready(function(){
  $($('.article-paragraph').find('a')).attr('target', '_blank');
    $('.article-paragraph').find('.hidden-s').html('<em>Stears</em>');
    });
  $('#Sub-Category').change(function(event){
    window.open($('#Sub-Category').val(), '_self');
  });

  $('.nest-anchor').click(function(event){
    event.preventDefault();
    var a = $(this).find('.target-anchor');
    var url = a.attr('href');
    var target = a.attr('target');
    if(!target){
      target = '_self';
    }
    window.open($(this).find('.target-anchor').attr('href'), target);
  });
});