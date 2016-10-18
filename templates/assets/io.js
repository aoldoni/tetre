function saveTextAsFile()
{
    var json = {};

    jQuery("textarea").each(function( index ) {
        json[$( this ).attr("id")] = $( this ).val()
    });

    var content = JSON.stringify(json);
    var textToSaveAsBlob = new Blob([content], {type:"text/plain"});
    var textToSaveAsURL = window.URL.createObjectURL(textToSaveAsBlob);
    var fileNameToSaveAs = "evaluations.json";
 
    var downloadLink = document.createElement("a");
    downloadLink.download = fileNameToSaveAs;
    downloadLink.innerHTML = "Download File";
    downloadLink.href = textToSaveAsURL;
    downloadLink.onclick = destroyClickedElement;
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
 
    downloadLink.click();
}
 
function destroyClickedElement(event)
{
    document.body.removeChild(event.target);
}
 
function readText(elm)
{
    var fileToLoad = ""; 

    if (elm.files && elm.files[0]) {
        fileToLoad = elm.files[0];
        console.log("Loading file...");

        var fileReader = new FileReader();

        fileReader.onload = function(fileLoadedEvent) 
        {
            if (confirm('Are you sure you want to load? Loading a new JSON file will overwrite all current work.')) {
                var textFromFileLoaded = fileLoadedEvent.target.result;

                var result = jQuery.parseJSON(textFromFileLoaded);
                jQuery.each(result, function(k, v) {
                    jQuery("#" + k).val(v);
                });

                console.log("Loaded.");
            }
            else
            {
                console.log("Loading cancelled.");
            }
        };

        fileReader.readAsText(fileToLoad, "UTF-8");
    }
}