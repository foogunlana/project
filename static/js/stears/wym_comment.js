
var default_entry = '<p> Please enter your comment here...</p>';

$(document).ready(function() {
    $('.wymeditor.comment_editor').wymeditor({
                html: default_entry,
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

    $('#comment_form').submit(function(event){
        var wym = $.wymeditors(1);
        wym.update();
        var comment = $('#comment_form').find('.wym_html_val').val();

        if((comment===default_entry)||(comment.length < 20)){
            event.preventDefault();
            alert('You have not entered a long enough comment');
            return false;
        }

        $.ajax({
            type: "post",
            url:$('#comment_form').find('button[type=submit]').data('url'),
            data: {
                'comment':comment,
            },
            success: function(responseData, textStatus, jqXHR) {
                if(responseData === "reload"){
                    location.reload();
                }else{
                    alert(responseData);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
            }
        });
        return false;
    });
});


