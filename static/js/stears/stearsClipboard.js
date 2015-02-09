// main.js
$(document).ready(function(){
	$('.copy-button').each(function(){
		var client = new ZeroClipboard( this );
		client.on( "ready", function( readyEvent ) {
		// alert( "ZeroClipboard SWF is ready!" );
		client.on( "aftercopy", function( event ) {
		// `this` === `client`
		// `event.target` === the element that was clicked
		event.target.style.display = "none";
		alert("Copied text to clipboard: " + event.data["text/plain"] );
		} );
	} );
	});
});