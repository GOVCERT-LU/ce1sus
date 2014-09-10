function setCBChange(element, contentid) {

    element.change(function() {
    var text = this.options[this.selectedIndex].text;
    var div = $('#'+id+' #attributeFormDefinition #editBox');
    if (text === 'File') {
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
        var id = $(this).attr('id');
        if (id === 'collapseItem'+identifier) {
            $(this).collapse('show');
        } else {
            $(this).collapse('hide');
        }
    });
    $('#collapseItem'+identifier).scrollView();
    activateMenuLi(identifier);
}

function openAllColapses(except){
    $('#leftMenu').find("li").each(function() {
        $(this).attr('class', 'active');
    });
    $('.panel-collapse').each(function () {
        //This is just due to the workaround
        if (except !== 'None') {
            var id = $(this).attr('id');
            if ( id === 'collapseItem'+except) {
                $(this).collapse('show');
                $('#menu'+except+'LI').attr('class', 'active');
                $(this).scrollView();
            }
        } else {
            $(this).collapse('show');
        }
        });
}

function closeAllColapses(except){
    $('.panel-collapse').each(function () {
        //This is just due to the workaround
        if (except !== 'None') {
            var id = $(this).attr('id');
            if ( id === 'collapseItem'+except) {
                $(this).collapse('hide');
            }
        } else {
            $(this).collapse('hide');
            }
        }
    );
}

function enableDisableCB(eventID, hasValues) {
    if (hasValues) {
        var checked = $("#eventCheckBox").prop("checked");
        if (checked) {
            $('#parent_object_idID').prop('disabled', true);
            $('select#parent_object_idID option').filter(
                    function() {
                        this.selected = (this.text === '');
                    });
        } else {
            $('#parent_object_idID').prop('disabled', false);
            $('select#parent_object_idID option')
                    .filter(
                            function() {
                                this.selected = ($(this)
                                        .val() === 'None');
                            });
        }
    } else {
        alert('No objects can be assigned.');
        $("#eventCheckBox").prop('checked', true);
        
    }
}


function searchFormSubmit(formElement, event, uri, contentid, refreshContainer) {
    // setup some local variables
    var form = $(formElement);
    // let's select and cache all the fields
    var inputs = form.find("input, select, button, textarea");
    // serialize the data in the form
    var serializedData = form.serialize();

    // magic to get the button value
    var name = event.originalEvent.explicitOriginalTarget.name;
    if (name) {
        var value = event.originalEvent.explicitOriginalTarget.value;
        serializedData += '&' + name + '=' + value;
    }

    // let's disable the inputs for the duration of the ajax request
    inputs.prop("disabled", true);

    // fire off the request
    var request = $.ajax({
        url : uri,
        type : "post",
        data : serializedData,
     timeout: 600000 //10 Min
    });
    $("#searchAni").html('Searching <img src="/img/ajax-loader.gif" alt="loading"/> ');
    // callback handler that will be called on success
    request.done(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/^<!--OK--/gi)) {
            $("#" + refreshContainer + "").html(message);
        } else {
            if (responseText.match(/^<!--PostError-->/gi)) {
                var resultText = createErrorsMsg(null, responseText);
            } else {
                var resultText = responseText;
            }
            $("#" + refreshContainer + "").html(resultText);
        }
    });

    // callback handler that will be called on failure
    request.fail(function(response, textStatus, XMLHttpRequest) {
        var message = getResponseConent(response);
        $('#' + contentid + 'Errors').html(message);
    });
    // callback handler that will be called regardless
    // if the request failed or succeeded
    request.always(function() {
        $("#searchAni").html('');
        // reenable the inputs
        inputs.prop("disabled", false);
    });
    // prevent default posting of form
    event.preventDefault();

}

function loadAttributesProcess(element, formID, containerID, eventID, objectID, attributeID, enabled) {
    //clear container
    $('#'+containerID).html('');
    if (element === null){
        var value = $('#'+formID+' input#definitionID:last').val();
        if (enabled) {
            loadContent(containerID,'/events/event/attribute/render_handler_edit/'+value+'/'+eventID+'/'+objectID+'/'+attributeID);
        } else {
            loadContent(containerID,'/events/event/attribute/render_handler_view/'+eventID+'/'+attributeID);
        }

    } else {
        value = $(element).val();
        if (value) {
            loadContent(containerID,'/events/event/attribute/render_handler_input/'+$(element).val()+'/'+eventID+'/'+objectID);
        } else {
            $('#'+formID+' #'+containerID).html('<div class="row"><div class="col-xs-3 col-sm-3"><div style="padding: 5px; text-align:right"><label></label></div></div><div class="col-xs-9 col-sm-9"><div id="editBox"><div id="editBoxHidden">Please select something</div></div></div></div>');
        }
    }
}

function showPaginatorModal(id, title, contentUrl, postUrl, refresh,
        refreshContentID, refreshContentUrl) {
    $('#' + id).modal('show');
    loadContent('' + id + 'body', contentUrl);
    $('#' + id + 'Label').html(title);
    if (postUrl) {
        $("#" + id + "Form").unbind('submit');
        $("#" + id + "Form").submit(function(event) {
            formSubmit(this,event,id , postUrl,refresh,refreshContentID,refreshContentUrl);
        });
        $('#' + id + 'Footer')
                .html(
                        '<input class="btn btn-primary" value="'
                                + 'Save changes" type="submit"><button class="btn btn-default" data-'
                                + 'dismiss="modal">Close</button>');
    }
}

function removeInputField(id) {
    $('#'+id).remove();
}

function dialogCloseTabCallValidated(url, tabID, tabToClose) {
    genericDialogCall(url, 'unValiEv', '/admin/validation/unvalidated', true, true, tabID, tabToClose);
}

function add_event(formElement, event, uri, containerid){
	var form = $(formElement);
    var inputs = form.find("input, select, button, textarea");
    var formData = new FormData(form[0]);
    //disable the inputs
    inputs.prop("disabled", true);
    var request = $.ajax({
        url : uri,
        type : "POST",
        data : formData,
        contentType: false,
        processData: false,
        //timeout: 30000 //3secs
    });
    request.fail(function(response, textStatus, XMLHttpRequest) {
    	  
        var message = getResponseConent(response);
        $('#' + containerid + 'Errors').html(message);
    });
    request.error(request.fail);
    request.done(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/<!--OK--/gi)) {
        	//clear form
        	loadContent(containerid,"/events/event/add_event");
        	//extract id
        	matches = message.match(/<!--OK--><!--EventView--><!--(\d{1,},.*)-->/);
        	
        	if (matches && matches.length == 2) {
        		//open sive nav
        		split = matches[1].split(',');
        		eventId = split[0];
        		title = split[1];
        		loadNewSideNavTab(eventId, 'eventsTabTabContent', '/events/event/view/'+eventId, true, 'Event #'+eventId+' - '+title);
        	} else {
        		loadSideNav("RecentEvents", false);
        	}
            
        } else {
            if (message.match(/<!--Error-->/gi)) {
                form.prepend(message);
            } else {
                if (message.match(/<!--PostError-->/gi)) {
                    //post errors are mainly validations issues
                    var resultText = message;
                    
                } else {
                    var resultText = createErrorsMsg(null, message);
                }
                $("#"+containerid).html(resultText);

            }
        }
    });

    request.always(function() {
        // reenable the inputs
        inputs.prop("disabled", false);
    });
    // prevent default posting of form
    event.preventDefault();
}

function inforUnpublished(modalID, eventID) {
	var show = $('#Overview'+eventID+'Hidden  input#publishedID:first').val();
	if (show == 1) {
      if(confirm("Modifications on event will unpublish it. Don't forget to republish.")) {
    	  // unpublish event
    	  var request = $.post("/events/event/unpublish", { event_id: eventID });

    	    request.fail(function(response, textStatus, XMLHttpRequest) {
    	        var messages = getErrorTextMessage(response)
    	        alert(messages[1]);
    	    });
    	    request.error(request.fail);
    	    request.done(function(responseText, textStatus, XMLHttpRequest) {
    	        var message = getResonseTextContent(responseText);
    	        if (message.match(/<!--OK--/gi)) {
    	        	//clear form
    	            //reload events view if successfull
    	      	  loadContent('Overview'+eventID+'Hidden','/events/event/event/'+eventID);
    	      	  $('#'+modalID).modal('show');
    	        }
    	    });

      } 
	} else {
		$('#'+modalID).modal('show');
	}
}

function generic_single_post(url, params, contentID, contentURL){
	var request = $.post(url, params);
    request.fail(function(response, textStatus, XMLHttpRequest) {
        var messages = getErrorTextMessage(response)
        alert(messages[1]);
    });
    request.error(request.fail);
    request.done(function(responseText, textStatus, XMLHttpRequest) {
        var message = getResonseTextContent(responseText);
        if (message.match(/<!--OK--/gi)) {
        	//clear form
            //reload events view if successfull
        	if (contentID && contentURL){
        		loadContent(contentID,contentURL);
        	}
        } else {
        	message = getErrorTextMessage(responseText)
        	if (message) {
        		alert('Error: '+$("<p>").html(message).text());
        	} else {
        		alert('Error: Could send POST request');
        	}
        	
        }
    });
}

function publish(eventID) {
	generic_single_post("/events/event/publish", { event_id: eventID },'Overview'+eventID+'Hidden','/events/event/event/'+eventID);
}

function activateUser(userID){
	generic_single_post("/admin/users/activate", { user_id: userID },'UserRightContent','/admin/users/right_content/'+userID);
}

function resentMail(userID){
	generic_single_post("/admin/users/resend_mail", { user_id: userID },null,null);
}
