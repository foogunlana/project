$(document).ready(function() {
    function wordCount( val ){
        return 'Characters excluding spaces: '+ val.replace(/\s+/g, '').length.toString()
                +'\nCharacters including spaces: '+val.length
                + '\nWords :'+val.match(/\S+/g).length
                + '\nLines :'+val.split(/\r*\n/).length;
        }


    $('button.wym_submit_button[type="submit"]').click(function(){
        save_or_review = $(this).val();
    });
    
    $('.wymeditor').wymeditor({
                html: '<p>Hello, World!<\/p>',
                postInit: function(wym) {
                    //construct the button's html
                    var html = "<li class='wym_tools_word_count' style='padding-top:3px;padding-left:5px;'>"
                             + "<a name='Word count' title='Word count' href='#'"
                             + " style='background: url(\"/static/images/stears/word_count2.png\") no-repeat;'>"
                             + "Do something"
                             + "</a></li>";

                    //add the button to the tools box
                    $(wym._box)
                    .find(wym._options.toolsSelector + wym._options.toolsListSelector)
                    .append(html);

                    //handle click event
                    $(wym._box)
                    .find('li.wym_tools_word_count a').click(function() {
                        //do something
                        wym.update();
                        word_count = wordCount($('.wym_html_val').val());

                        alert(word_count);
                        // wym.paste('Lorem ipsum dolor sit amet, consectetuer adipiscing elit.');
                        return(false);
                    });
                }
            });

    $('#article_form').submit(function(event){
        var wym = $.wymeditors(0);
        wym.update();
        if(save_or_review === 'review'){
            if(!confirm( "Are you sure you want to post, you won't be able to edit this article without editor priviledges!" )){
                event.preventDefault();
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


