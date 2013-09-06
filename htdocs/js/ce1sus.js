function setCBChange(element, contentid) {
	
	element.change(function() {
    	text = this.options[this.selectedIndex].text;
    	div = $('#'+id+' #attributeFormDefinition #editBox');
        if (text == 'File') {
        	div = $('#'+id+' #attributeFormDefinition #editBox');
        	div.html('<div class="row-fluid"><div class="span3"><div style="'
        			+'padding: 5px; text-align:right"><label> Value:</label>'
        			+'</div></div><div class="span9"><input id="valueID" name='
        			+'"value" type="file" /></div></div>');
        } else {
        	div.html('<div class="row-fluid"><div class="span3"><div style="'
        			+'padding: 5px; text-align:right"><label> Value:</label>'
        			+'</div></div><div class="span9"><input id="valueID" name='
        			+'"value" type="text" value="" /></div></div>');
        }
    });
}

function showSelected(identifier){
	$('.collapse').each(function () {
		id = $(this).attr('id');
		if (id == 'collapseItem'+identifier) {
			$(this).collapse('show').delay(300);
		} else {
			$(this).collapse('hide').delay(300);
		}
	});
}

function openAllColapses(except){
	$('.collapse').each(function () {
		//This is just due to the workaround
		if (except != 'None') {
			id = $(this).attr('id');
			if ( id == 'collapseItem'+except) {
				$(this).collapse('show').delay(300);
			}
		} else {
			$(this).collapse('show').delay(300);}
		} 
	);
}

