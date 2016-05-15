/**
 * Created by Alex on 5/15/2016.
 */
//My JS fiddle to test this: https://jsfiddle.net/cnge02ha/5/
//var paradigmVar = $("select");//fetch the paradigm selector element

/*paradigmVar.change(function() { //when it changes, display the correct extra div and hide the other ones
		console.log(paradigmVar.val());
    var currentName = paradigmVar.val() + "RS"; //naming scheme: paradigm name then RS
    //want to change the title also - use paradigmVar.find('option:selected').text()
    var toBeDisplayed = $(".radioset[name=" + currentName + "]");
    toBeDisplayed.css("display", "block"); //Need to also toggle disabled or not
    $(".radioset").not(toBeDisplayed).css("display", "none");

			});*/

$(document).ready(function(){
    var paradigmVar = $("#id_paradigm");
        console.log(paradigmVar);
    console.log($(".radioset"));
        paradigmVar.change(function() { //when it changes, display the correct extra div and hide the other ones
            console.log(paradigmVar.val());
        var currentName = paradigmVar.val() + "RS"; //naming scheme: paradigm name then RS
        //want to change the title also - use paradigmVar.find('option:selected').text()
        $(document).prop('title', paradigmVar.find('option:selected').text());
        var toBeDisplayed = $(".radioset[name=" + currentName + "]");
        toBeDisplayed.css("display", "block"); //Need to also toggle disabled or not
        toBeDisplayed.find("[type='radio']").prop('disabled', false);
        $(".radioset").not(toBeDisplayed).css("display", "none");
        $(".radioset").not(toBeDisplayed).find("[type='radio']").prop('disabled',true);

                });
    paradigmVar.trigger('change');//This triggers the above function on load
 });

