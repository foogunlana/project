
$(document).ready(function(){
  $('.business-nav-container').hide();
  $($('.article-paragraph').find('a')).attr('target', '_blank');
  $('.article-paragraph').find('.hidden-s').html('<em>Stears</em>');

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

   $(".dropdown-tab").mouseenter(function () {
      var className = $(this).data('subs');
      $('.' + className).addClass('hovered');
      $('.' + className).stop(true, true).slideDown('medium');
    });

   $(".dropdown-tab").mouseleave(function () {
      var className = $(this).data('subs');
      $('.' + className).removeClass('hovered');
      setTimeout(
        function(){
          if(!$('.' + className).hasClass('hovered')){
            $('.' + className).stop(true, true).slideUp('medium');
          }
        }, 50);
    });

   $('.business-nav-container').mouseenter(function(){
      var className = $(this).data('main');
      $('.' + className).addClass('hovered');
      $(this).addClass('hovered');
   });

   $('.business-nav-container').mouseleave(function(){
      var className = $(this).data('main');
      $('.' + className).removeClass('hovered');
      $(this).removeClass('hovered');
      var self = $(this);
      setTimeout(
        function(){
          if(!$(self).hasClass('hovered')){
            $(self).slideUp('medium');
          }
        }, 50);
   });


});