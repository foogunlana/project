/**
* The catchpaste plugin call automatically the paste dialog when user 
* press Ctrl + V combinaison in editor.
*  
*/
$(document).ready(function(){
    WYMeditor.editor.prototype.sbCatchPaste = function(options) {
      var wym = this;
      var doc = this._doc;
      
      _sbCatchPaste = function(e) {
          e.stopPropagation();
          e.preventDefault();
          wym.exec(WYMeditor.PASTE);
      };
      
      // Unbind des évènements préalablement mis en place (sous IE)
      $(doc.body).unbind('paste').unbind('beforepaste');
      if($.isFunction(doc.body.onpaste)) {
         doc.body.onpaste = function() {};
      }
      if($.isFunction(doc.onbeforepaste)) {
         doc.body.onbeforepaste = function() {};
      }
      

      $(doc.body).bind('keydown', 'Ctrl+V', _sbCatchPaste );
      $(doc.body).bind('keydown', 'Meta+V', _sbCatchPaste );
      $(doc.body).bind('keydown', 'Shift+Insert', _sbCatchPaste );
      
      $(doc.body).bind('paste', _sbCatchPaste );
      $(doc.body).bind('beforepaste', _sbCatchPaste );
  };

  /* Overriding native insert method */
  WYMeditor.editor.prototype._insert = WYMeditor.editor.insert;

  WYMeditor.editor.prototype.insert = function(sData) {
     if(sData.search(new RegExp(this._newLine, "g")) != -1) {
        //split the data, using newlines as the separator
        var aP = sData.split(this._newLine);
        sData = '';
        for(x = aP.length - 1; x >= 0; x--) {
           sData += "<p>" + aP[x] + "</p>";
        }
     }
     this._insert(sData);
  };

});