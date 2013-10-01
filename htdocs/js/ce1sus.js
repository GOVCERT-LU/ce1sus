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


