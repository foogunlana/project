
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

   $("#b_e_nav").mouseenter(function () {
      $('.business-nav-container').addClass('hovered');
      $('.business-nav-container').slideDown('medium');
    });

   $("#b_e_nav").mouseleave(function () {
      $('.business-nav-container').removeClass('hovered');
      setTimeout(
        function(){
          if(!$('.business-nav-container').hasClass('hovered')){
            $('.business-nav-container').slideUp('medium');
          }
        }, 300);
    });

   $('.business-nav-container').mouseenter(function(){
      $("#b_e_nav").addClass('hovered');
      $(this).addClass('hovered');
   });

   $('.business-nav-container').mouseleave(function(){
      $("#b_e_nav").removeClass('hovered');
      $(this).removeClass('hovered');
      setTimeout(
        function(){
          if(!$('.business-nav-container').hasClass('hovered')){
            $('.business-nav-container').slideUp('medium');
          }
        }, 300);
   });


});