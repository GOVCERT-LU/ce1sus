function formEvent(element,event, uri, contentid, doRefresh,refreshContainer,refreshUrl) {
	
	genericFormSubmit(element,event, null,contentid, uri, doRefresh,refreshContainer,refreshUrl);
}

function formSubmit(formElement,event, modalID, uri, doRefresh,refreshContainer,refreshUrl) {
	genericFormSubmit(formElement,event, modalID, null, uri, doRefresh,refreshContainer,refreshUrl);
}

function genericFormSubmit(formElement,event, modalID, contentid, uri, doRefresh,refreshContainer,refreshUrl) {
	
	
	// setup some local variables
    form = $(formElement);
    // let's select and cache all the fields
    inputs = form.find("input, select, button, textarea");
    // serialize the data in the form
    serializedData = form.serialize();
    
    //magic to get the button value
    name = event.originalEvent.explicitOriginalTarget.name;
    if (name) {
    	value = event.originalEvent.explicitOriginalTarget.value;
    	serializedData += '&'+name+'='+value;
    }

    // let's disable the inputs for the duration of the ajax request
    inputs.prop("disabled", true);
    
 // fire off the request 
    request = $.ajax({
        url: uri,
        type: "post",
        data: serializedData
    });

    // callback handler that will be called on success
    request.done(function (responseText, textStatus, XMLHttpRequest){
    	if (responseText.match(/^--OK--/gi)) {
    		if (modalID) {
    			$("#"+modalID).modal("hide");
    		}
    		//refrehshPage & container if needed
    		if (doRefresh) {
            	loadContent(refreshContainer,refreshUrl);
            }
    	} else {
    		if (modalID) {
    			$("#"+modalID+"body").html(responseText);
    		} else {
    			$("#"+refreshContainer+"").html(responseText);
    		}
    	}
    });

    // callback handler that will be called on failure
    request.fail(function (responseText, textStatus, XMLHttpRequest){
    	if (modalID) {
    		$('#'+modalID+'body').html('<div class="alert alert-error">There was an error making the AJAX request<br/>'+responseText+'</div>');
    	} else {
    		$('#'+contentid+'Errors').html('<div class="alert alert-error">There was an error making the AJAX request<br/>'+responseText+'</div>');
    	}
    });
    // callback handler that will be called regardless
    // if the request failed or succeeded
    request.always(function () {
        // reenable the inputs
        inputs.prop("disabled", false);
    });
    // prevent default posting of form
    event.preventDefault();
    
    
    
}


function setCBChange(element, contentid) {
	
	element.change(function() {
    	text = this.options[this.selectedIndex].text;
    	div = $('#'+id+' #attributeFormDefinition #editBox');
        if (text == 'File') {
        	div = $('#'+id+' #attributeFormDefinition #editBox');
        	div.html('<div class="row-fluid"><div class="span3"><div style="padding: 5px; text-align:right"><label> Value:</label></div></div><div class="span9"><input id="valueID" name="value" type="file" /></div></div>');
        } else {
        	div.html('<div class="row-fluid"><div class="span3"><div style="padding: 5px; text-align:right"><label> Value:</label></div></div><div class="span9"><input id="valueID" name="value" type="text" value="" /></div></div>');
        }
    });
}

function loadContent(contentid, url) {
	if ((contentid) && (url)) {
	$("#"+contentid).html('<img src="/img/ajax-loader.gif" alt="loading"/> ');
	  //load Content
	$("#"+contentid).load(url, "", 
	          function (responseText, textStatus, XMLHttpRequest) {
	      if(textStatus == 'error') {
	            $("#"+contentid).html('<div class="alert alert-error">'+responseText+'</div>'+responseText);
	      }
	  });
	}
}

function loadNewTab(pk, id, url) {
	//getTabID
	tabID = id.replace("TabContent","");
	//deactivate Tabs
	//deactivateActiveOne
	$('#'+tabID).find("li").each(function() {
            $(this).attr('class', '');
        });
	//check if element exists
	if ($('#'+tabID+pk+'LI').length) {
		$('#'+tabID+pk+'LI').attr('class', 'active');
	} else {
    	//createTab
    	$("#"+tabID).append($('<li class="active" id="'+tabID+pk+'LI"><a href="#" onclick="getPaging(\''+url+'\',this.id)" id="'+tabID+pk+'">' +
    			'Event '+pk+
    		    '&nbsp;<button class="close" title="Remove this Tab" type="button" onclick="closeTab(\''+tabID+'\',\''+tabID+pk+'LI\');">×</button>' +
    		    '</a></li>'));
	}
    //load Content
    
    loadContent(id, url);
}

function loadTab(pk, id, url, tabid) {
	getPaging(url,tabid);
}

function closeTab(tabulatorID,tabToCloseID) {
	
	$('#'+tabToCloseID).find("a").each(function() {
		//normalerweis get et just een
		$(this).attr('onclick','').unbind('click');
	});
	
	$('#'+tabToCloseID).remove();
	
	//goback to first tab
	$('#'+tabulatorID).find("a").each(function() {
            script = $(this).attr("onclick");
            
            //extract url from function
            url = script.match(/getPaging\('(.*)',this\.id\)/);
            getPaging(url[1],this.id);
            return false;
        });
}

function getPaging(url,id) {
	  //deactivateActiveOne
	  parentName = $('#'+id+'LI').parent().attr('id');
	  $('#'+parentName).find("li").each(function() {
	    $(this).attr('class', '');
	  });
	  
	  //activate tab
	  $('#'+id+'LI').attr('class', 'active');
	  
	  
	  loadContent(parentName+'TabContent',url);
	  //load Content
	}

function getContent(url,id,contentID) {
	  //deactivateActiveOne
	  
	  $('#'+id+'LI').parent().find("li").each(function() {
	    $(this).attr('class', '');
	  });
	  
	  //activate tab
	  $('#'+id+'LI').attr('class', 'active');
	  //load Content
	  loadContent(contentID,url);
	  
	}

function showPaginatorModal(title, contentUrl, postUrl, refresh, refreshContentID, refreshContentUrl ) {
	$('#paginatorModal').modal('show');
	loadContent('paginatorModalbody',contentUrl);
	$('#paginatorModalLabel').html(title);
	if (postUrl) {
		$("#paginatorModalForm").unbind('submit');
		$("#paginatorModalForm").submit(function(event){
			
			
			// setup some local variables
		    form = $('#paginatorModalForm');
		    // let's select and cache all the fields
		    inputs = form.find("input, select, button, textarea");
		    // serialize the data in the form
		    serializedData = form.serialize();
		    
		    //magic to get the button value
		    name = event.originalEvent.explicitOriginalTarget.name;
		    if (name) {
		    	value = event.originalEvent.explicitOriginalTarget.value;
		    	serializedData += '&'+name+'='+value;
		    }

		    // let's disable the inputs for the duration of the ajax request
		    inputs.prop("disabled", true);
		    
		 // fire off the request 
		    request = $.ajax({
		        url: postUrl,
		        type: "post",
		        data: serializedData
		    });

		    // callback handler that will be called on success
		    request.done(function (responseText, textStatus, XMLHttpRequest){
		    	if (responseText.match(/^--OK--/gi)) {
		    		$('#paginatorModal').modal("hide");
		    		//refrehshPage & container if needed
		    		if (refresh) {
		            	loadContent(refreshContentID,refreshContentUrl);
		            }
		    	} else {
		    		$("#paginatorModalbody").html(responseText);
		    	}
		    });

		    // callback handler that will be called on failure
		    request.fail(function (responseText, textStatus, XMLHttpRequest){
		    	$('#paginatorModalbody').html('<div class="alert alert-error">There was an error making the AJAX request</div>');
		    });
		    // callback handler that will be called regardless
		    // if the request failed or succeeded
		    request.always(function () {
		        // reenable the inputs
		        inputs.prop("disabled", false);
		    });
		    // prevent default posting of form
		    event.preventDefault();
		});
		$('#paginatorModalFooter').html('<input class="btn btn-primary" value="Save changes" type="submit"><button class="btn" data-dismiss="modal">Close</button>');
	} else {
		$('#paginatorModalFooter').html('<button class="btn" data-dismiss="modal">Close</button>');
	}
}
