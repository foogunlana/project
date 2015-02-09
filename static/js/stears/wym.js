$(document).ready(function() {
    
    $('.wymeditor').wymeditor();

    $('#article_form').submit(function(event){
        var wym = $.wymeditors(0);
        var save_or_review = $(this).attr('value');
        wym.update();
        if(save_or_review === 'review'){
            if(!confirm( "Are you sure you want to post" )){
            event.preventDefault();
            console.log('prevent');
            return false;
            }
        }

        $.ajax({
            type: "post",
            data: {
                'headline':$('#id_headline').val(),
                'content':$('.wym_html_val').val(),
                'article_id':$('#id_article_id').val(),
                'nse_headlines':$('#id_nse_headlines').val(),
                'categories':$('#id_categories').val(),
                'save_or_review':save_or_review,
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    alert(responseData);
                    $('.wym_html_val').val(responseData);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
    });

    $('.wym_preview_button').click(function(){
        $('a[name="Preview"]').click();
    });

});
