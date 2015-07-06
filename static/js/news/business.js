
$(document).ready(function(){
  $('#Sub-Category').change(function(event){
    window.open($('#Sub-Category').val(),'_self');
  });
});