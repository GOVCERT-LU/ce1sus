$.fn.scrollView = function () {
    return this.each(function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top
        }, 1000);
    });
}

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
        data: serializedData,
        timeout: 10000
    });

    // callback handler that will be called on success
    request.done(function (responseText, textStatus, XMLHttpRequest){
    	if (responseText.match(/^--OK--/gi)) {
    		if (modalID) {
    			$("#"+modalID).modal('hide');
    		}
    		//refrehshPage & container if needed
    		if (doRefresh) {
            	loadContent(refreshContainer,refreshUrl);
            }
    	} else {
    		if (responseText.match(/^<!--PostError-->/gi)) {
    			resultText= responseText;
    		} else {
	    		resultText = '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
	    		resultText += '<h4 class="alert-heading">An expected Error occurred!</h4><p>'
	    		resultText += responseText;
	    		resultText += '</p></div>';
    		} 
    		if (modalID) {
    			$("#"+modalID+"body").html(resultText);
    		} else {
    			$("#"+refreshContainer+"").html(resultText);
    		}
    	}
    });

    // callback handler that will be called on failure
    request.fail(function (responseText, textStatus, XMLHttpRequest){
		resultText = '<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
		resultText += '<h4 class="alert-heading">There was an error making the AJAX request</h4><p>'
		resultText += responseText;
		resultText += '</p></div>';
    	if (modalID) {
    		$('#'+modalID+'body').html(resultText);
    	} else {

    		$('#'+contentid+'Errors').html(resultText);
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

function loadContent(contentid, url) {
	if ((contentid) && (url)) {
	$("#"+contentid).html('<img src="/img/ajax-loader.gif" alt="loading"/> ');
	  //load Content
	$.ajax({
	    url: url,
	    timeout: 3000, // sets timeout to 3 seconds,
	    success: function(response){
	    	if(response.match(/^(<HTML>)|(<html>)/)) {
	    		$("#main").html(response);
	    	} else {
	    		$("#"+contentid).html(response);
	    	}
	    },
	    error: function(response, type, message){
	    	$("#"+contentid).html('<div class="alert alert-block alert-danger fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button><h4 class="alert-heading">'+type+'</h4><p>'+message+'</p></div>');
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
    	$("#"+tabID).append($('<li class="active" id="'
    			+tabID+pk
    			+'LI">'
    			+'<a href="#" src="'+url+'" onclick="loadTabLi(this.id, true)" id="'+tabID+pk+'">' 
    			+ 'Event '+pk+
    		    '&nbsp;<button class="close" title="Remove this Tab" '
    			+'type="button" onclick="closeTab(\''+tabID+'\',\''
    			+tabID+pk+'LI\');">×</button>' +
    		    '</a></li>'));
	}
    //load Content
    loadContent(id, url);
}

function loadTabFromPaginator(pk, id, url, tabid) {
	//Not done yet
	//TODO: jojo do ass nach fill
	loadTab(url,tabid);
}

function closeTab(tabulatorID,tabToCloseID) {
	
	$('#'+tabToCloseID).find("a").each(function() {
		//normalerweis get et just een
		$(this).attr('onclick','').unbind('click');
	});
	
	$('#'+tabToCloseID).remove();
	
	//goback to first tab
	$('#'+tabulatorID).find("a").each(function() {
		    //loadfirst tab
			url = $(this).attr('src');
			loadTab(url, this.id);
            return false;
        });
}

function activateLi(id){
	  //deactivateActiveOne
	  $('#'+id+'LI').parent().find("li").each(function() {
	    $(this).attr('class', '');
	  });
	  //activate tab
	  $('#'+id+'LI').attr('class', 'active');	
}

function loadTab(url, id) {
	activateLi(id);
	parentName = $('#'+id+'LI').parent().attr('id');
	loadContent(parentName+'TabContent',url);
}

function findAndLoadActiveLi(id,contentID){
	$('#'+id).find("li").each(function() {
        var className = $(this).attr('class');
        if (className == 'active') {
            $(this).find("a").each(function() {
            	url = $(this).attr('src');
            	loadContent(contentID,url);
            });
        }
    })
}

function loadToolbarLi(id,contentID, reload){
	activateLi(id);
	url = $('#'+id).attr('src');
	loadContent(contentID,url);
}

function loadTabLi(id, reload){
	parentName = $('#'+id+'LI').parent().attr('id');
	loadToolbarLi(id,parentName+'TabContent');
}

function showPaginatorModal(title, contentUrl, postUrl, refresh, 
							refreshContentID, refreshContentUrl ) {
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
		    	$('#paginatorModalbody').html('<div class="alert alert-error">'
		    			+'There was an error making the AJAX request</div>');
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
		$('#paginatorModalFooter').html('<input class="btn btn-primary" value="'
				+'Save changes" type="submit"><button class="btn" data-'
				+'dismiss="modal">Close</button>');
	} else {
		$('#paginatorModalFooter').html('<button class="btn" data-dismiss="'
				+'modal">Close</button>');
	}
}

function genericDialogCall(url, refreshContainer, refreshUrl, refreshContent, doCloseTab, tabID, tabToClose){
	$.ajax({
	    url: url,
	    error: function(response){
	    	if(response.match(/^(<HTML>)|(<html>)/)) {
	    		$("#main").html(response);
	    	} else {
	    		alert(response.responseText);
	    	}
	    },
	    success: function(response){
	    	if(response.match(/^(<HTML>)|(<html>)/)) {
	    		$("#main").html(response);
	    	} else {
	    		if (response.match(/^--OK--/gi)) {
	    			//do refresh
	    			if (refreshContent) {
	    				loadContent(refreshContainer,refreshUrl);
	    			} else {
	    				if (doCloseTab) {
	    					closeTab(tabID, tabToClose);
	    				}
	    			}
	    		} else {
	    			alert('An error occured:\n'+response);
	    		}
	    	}
	    },
	    timeout: 3000 // sets timeout to 3 seconds
    });
}

function dialogCall(url, refreshContainer, refreshUrl){
	genericDialogCall(url, refreshContainer, refreshUrl, true, false, '','');
}

function dialogCloseTabCall(url, tabID, tabToClose){
	genericDialogCall(url, '', '', false, true, tabID, tabToClose);
}

function activateMenuLi(id){
	  //deactivateActiveOne
	  $('#'+id).parent().find("li").each(function() {
	    $(this).attr('class', '');
	  });
	  //activate tab
	  $('#'+id).attr('class', 'active');	
}

