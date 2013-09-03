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