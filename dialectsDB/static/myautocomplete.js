/**
 * Created by Alex on 5/11/2015.
 */
 function split( val ) {
      return val.split( /,\s*/ );
    }
    function extractLast( term ) {
      return split( term ).pop();
    }
    function singleAutocomplete(element){
        $(element).autocomplete({
            source: $(element).attr('acsource').split(",")
                });
                console.log($(element).attr('acsource').split(","));
    }
    function multiAutocomplete(element){
        src = $(element).attr('acsource').split(","); //taken from the attributes, added by the widget
        $(element).bind( "keydown", function( event ) {
      // don't navigate away from the field on tab when selecting an item
        if ( event.keyCode === $.ui.keyCode.TAB &&
            $( this ).autocomplete( "instance" ).menu.active ) {
          event.preventDefault();
        }
      })
      .autocomplete({
        minLength: 0,
        source: function( request, response ) {
          // delegate back to autocomplete, but extract the last term
          response( $.ui.autocomplete.filter(
           src , extractLast( request.term ) ) );
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function( event, ui ) {
          var terms = split( this.value );
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push( ui.item.value );
          // add placeholder to get the comma-and-space at the end
          terms.push( "" );
          this.value = terms.join( ", " );
          return false;
        }
      });
    }

    function enableAutoComplete(row)
    {
        singleAutocomplete($(".acwidget",row)); //based on calss, adds single autocompletes
        multiAutocomplete($(".acwidgetmulti",row));//based on class, adds multiautocompletes
    }
    $(function() { //'#searchform tbody tr'
        $(".acwidget").each(function(index, element){
            singleAutocomplete(element);
        });
        $(".acwidgetmulti").each(function(index, element){
            multiAutocomplete(element);
        });

    });