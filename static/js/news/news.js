(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','gaFollow');

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


  $('.follow-us-intent').click(function(event){
    page = window.location.href;
    gaFollow('create', 'UA-65081439-1', 'auto');
    gaFollow('send', 'event', 'click', 'follow us on twitter', page);
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

   $('.toggle').click(function(event){
      event.preventDefault();
      var dropdown = $(this).attr('id');
      $('.' + dropdown).toggle('slow');
   });

});