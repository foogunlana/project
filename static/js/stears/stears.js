

$( document ).ready(function() {
    $( ".confirm-submission" ).click(function( event ) {
        if(!confirm( "Are you sure you want to post" )){
        	event.preventDefault();
        };
    }); 
});


// $(document).ready(function(){
// 	$(document).on('.button','click','')

// });

// var mylist = $('#myUL');
// var listitems = mylist.children('li').get();
// listitems.sort(function(a, b) {
//    return $(a).text().toUpperCase().localeCompare($(b).text().toUpperCase());
// })
// $.each(listitems, function(idx, itm) { mylist.append(itm); });