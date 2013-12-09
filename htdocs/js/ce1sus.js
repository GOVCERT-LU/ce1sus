function setCBChange(element, contentid) {
	
	element.change(function() {
    	text = this.options[this.selectedIndex].text;
    	div = $('#'+id+' #attributeFormDefinition #editBox');
        if (text == 'File') {
        	div = $('#'+id+' #attributeFormDefinition #editBox');
        	div.html('<div class="form-group">'+
        			  '<label for="inputEmail1" class="col-lg-3 control-label">Value:'+
        		      '</label>'+
        			  '<div class="col-lg-9">'+
        		      '<input class="form-control" id="valueID" name='+
        			  '"value" type="file" /></div></div>');
        } else {
        	div.html('<div class="form-group">'+
      			  '<label for="inputEmail1" class="col-lg-3 control-label">Value:'+
    		      '</label>'+
    			  '<div class="col-lg-9">'+
    		      '<input class="form-control" id="valueID" name='+
    			  '"value" type="text" /></div></div>');
        }
    });
}


function showSelected(identifier){
	$('.panel-collapse').each(function () {
		id = $(this).attr('id');
		if (id == 'collapseItem'+identifier) {
			$(this).collapse('show').delay(300);
		} else {
			$(this).collapse('hide').delay(300);
		}
	});
	$('#collapseItem'+identifier).scrollView();
	activateMenuLi(identifier)
}

function openAllColapses(except){
	$('#leftMenu').find("li").each(function() {
	    $(this).attr('class', '');
	});
	$('.panel-collapse').each(function () {
		//This is just due to the workaround
		if (except != 'None') {
			id = $(this).attr('id');
			if ( id == 'collapseItem'+except) {
				$(this).collapse('show');
				$('#menu'+except+'LI').attr('class', 'active');	
				$(this).scrollView();
			}
		} else {
			$(this).collapse('show')};
			
		} 
	);

	
}

function closeAllColapses(except){
	$('.panel-collapse').each(function () {
		//This is just due to the workaround
		if (except != 'None') {
			id = $(this).attr('id');
			if ( id == 'collapseItem'+except) {
				$(this).collapse('hide');
			}
		} else {
			$(this).collapse('hide')}
		} 
	);
}

function collapseOpenMyClick(except){
	alert('huhu');
}
function collapseCloseMyClick(except){
	alert('huhu');
}

function buttonClick(){
    var formData = new FormData($('#fileuploadForm')[0]);
    var bar = $('#bar');
    var percent = $('#percent');
    var status = $('#status');
    var cb = $('#definitionID');
    request = $.ajax({
        url: '/events/event/attribute/addFile',  //Server script to process data
        type: 'POST',
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false,
        beforeSend: function() {
            status.empty();
            var percentVal = '0%';
            $('#definitionID').parent().append(' <input type="hidden" name="definition" value="'+$("#definitionID option:selected").val()+'" >');
            $('#definitionID').prop('disabled', true);
            
            bar.show();
            percent.show();
            status.show();
            
            bar.width(percentVal)
            percent.html(percentVal);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            var percentVal = percentComplete + '%';
            bar.width(percentVal)
            percent.html(percentVal);
        },
        complete: function(xhr) {
            bar.hide();
            percent.hide();
            status.hide();
            status.html(xhr.responseText);
        }
    });
    // callback handler that will be called on success
    request.done(function (responseText, textStatus, XMLHttpRequest){
        if (responseText.match(/^--OK--/gi)) {
            file = responseText.match(/\*(.*)\*/);
            $("#editBoxHidden").html('<div class="row"><div class="col-xs-3 col-sm-3"><div style="padding: 5px; text-align:right"><label> Value:</label></div></div><div class="col-xs-9 col-sm-9">File Uploaded. Don\'t forget to save.<input id="valueID" name="value" type="hidden" value="'+file[1]+'"/></div></div>');
        } else {
            $("#editBoxHidden").html('<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button><h4 class="alert-heading">An unexpected Error occurred!</h4><p>'+responseText+'<input id="valueID" name="value" type="hidden" value=""/></p></div>');
        }
    });

    // callback handler that will be called on failure
    request.fail(function (responseText, textStatus, XMLHttpRequest){
        $("#editBoxHidden").html('<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button><h4 class="alert-heading">An unexpected Error occurred!</h4><p>'+responseText+'<input id="valueID" name="value" type="hidden" value=""/></p></div>');
    });
}

function enableDisableCB(eventID) {
    checked = $("#eventCheckBox").prop("checked");
    if (checked) {
        $('#parentObjectIDID').prop('disabled', true);
        $('select#parentObjectIDID option').filter(
                function() {
                    this.selected = (this.text == '');
                });
    } else {
        $('#parentObjectIDID').prop('disabled', false);
        $('select#parentObjectIDID option')
                .filter(
                        function() {
                            this.selected = ($(this)
                                    .val() == 'None');
                        });
    }
}

