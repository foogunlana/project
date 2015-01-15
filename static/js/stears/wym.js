$(document).ready(function() {
    
    $('.wymeditor').wymeditor();

    $('.wym_submit_button').click(function(){
        var wym = $.wymeditors(0);
        wym.update();

        $.ajax({
            type: "post",
            data: {'content':$('.wym_html_val').val()},
            success: function(responseData, textStatus, jqXHR) {
                alert(responseData);
                $('.wym_html_val').val(responseData);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
    });

    $('.wym_preview_button').click(function(){
        var wym = $.wymeditors(0);
        wym.update();
        var w = window.open();
        var html = $('.wym_html_val').val();
        $(w.document.body).html(html);
    });

});
