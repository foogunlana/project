

$( document ).ready(function() {
    $( "p" ).click(function( event ) {           
        alert( "Thanks for visiting!" );
    });

    $( "a" ).click(function( event ) {
        if(!confirm( "Are you sure you want to visit this link" )){
        	event.preventDefault();
        };
    });

    $( ".confirm-submission" ).click(function( event ) {
        if(!confirm( "Are you sure you want to post" )){
        	event.preventDefault();
        };
    });
});
