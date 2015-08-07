

$(document).ready(function() {
    function wordCount( val ){
        return 'Characters excluding spaces: '+ val.replace(/\s+/g, '').length.toString()
                +'\nCharacters including spaces: '+val.length
                + '\nWords :'+val.match(/\S+/g).length;
        }

    function clean_article_content(sData) {
     if(sData.search(new RegExp(new_line, "g")) != -1) {
        //split the data, using newlines as the separator
        // console.log(new_line);
        var aP = sData.split(new_line);
        sData = '';
        for(x = aP.length - 1; x >= 0; x--) {
           sData += "<p>" + aP[x] + "</p>";
        }
     }
     return sData;}

    $('button.wym_submit_button[type="submit"]').click(function(){
        save_or_review = $(this).val();
    });
    
    $('.wymeditor.article_editor').wymeditor({
        html: $('textarea.wymeditor').val(),
        postInit: function(wym) {
            // $(wym._doc.body).click( function() {
                //wym.sbCatchPaste();
            // });
            //construct the button's html
            var html = "<li class='wym_tools_word_count' style='padding-top:3px;padding-left:5px;'>"
                     + "<a name='Word count' title='Word count' href='#'"
                     + " style='background: url(\"/static/images/stears/word_count2.png\") no-repeat;'>"
                     + "Do something"
                     + "</a></li>";

            //add the button to box
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

    $('.wym_preview_button').click(function(){
        $('a[name="Preview"]').click();
    });

    $('#article_form').submit(function(event){
        var headline = $('#id_headline').val();
        var content = $('.wym_html_val').val();

        if(headline.length < 5){
            event.preventDefault();
            alert('Please enter a valid headline!');
            return false;
        }

        if(content.length < 20){
            event.preventDefault();
            alert('Who is going to want to read an article that short? ;)');
            return false;
        }

        var wym = $.wymeditors(0);
        wym.update();
        if(save_or_review === 'review'){
            var tag_count = -1;
            $('.tag_button').each(function(){
                tag_count+=1;
            });
            if(!$('#article_summary').hasClass('updated')){
                alert('Please add a summary');
                return false;
            }
            if($('#article_photo_link').data('link')==='N'){
                alert('You must add a photo to submit your editor. Ask you editor about uploading photos to the WEAL');
                return false;
            }
            if(tag_count < 3){
                alert('Please add at least 3 tags');
                event.preventDefault();
                $('#keyword_area').show();
                $('#id_tags').focus();
                return false;
            }else{
                if(confirm('Do you wish to add any more tags first?')){
                    $('#keyword_area').show();
                    $('#id_tags').focus();
                    save_or_review = 'save';
                    return false;
                }else{
                    if(!confirm( "Are you sure you want to post, you won't be able to continue editing this article without editor priviledges!" )){
                        event.preventDefault();
                        return false;
                    }
                }
            }
        }
        $('button.wym_submit_button[type="submit"]').hide();
        $.ajax({
            type: "post",
            data: {
                'headline':$('#id_headline').val(),
                'content':content,
                'article_id':$('#id_article_id').val(),
                'nse_headlines':$('#id_nse_headlines').val(),
                'categories':$('#id_categories').val(),
                'save_or_review':save_or_review,
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    msg = JSON.parse(responseData);
                    if(msg.success){
                        alert("Your article has been saved");
                        $('.wym_html_val').val(msg.article);
                        $('#ajax_article_content').html(msg.article);
                        $('#hidden_article_form').hide();
                        $('button.wym_submit_button[type="submit"]').show();
                    }else{
                        var keys = Object.keys(msg.errors);
                        message = '';
                        for(i = 0; i < keys.length; i++){
                            message += '('+ keys[i] + ')' + ': ' + msg.errors[keys[i]] + '\n';
                        }
                        alert(message);
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
    });
    
    $('#ajax_article_content').find('.hidden-s').html('<em>Stears</em>');
    $('iframe').css('height','500px');
});


