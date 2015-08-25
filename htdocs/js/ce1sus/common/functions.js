/**
 * 
 */

function Ce1susException(message) {
  this.name = "Ce1susException";
  this.type = "danger";
  this.message= message;
}
Ce1susException.prototype = new Error();
Ce1susException.prototype.constructor = Ce1susException;

function Ce1susRestException(message, type) {
  this.name = "Ce1susException";
  this.type = type;
  this.message= message;
}
Ce1susRestException.prototype = new Ce1susException();
Ce1susRestException.prototype.constructor = Ce1susRestException;

function extractBodyFromHTML(text){
  var message = text;
  var bodyStart = message.indexOf('<body') + 5;
  var bodyEnd = message.indexOf('</body>');
  message = message.substring(bodyStart,bodyEnd); 
  bodyStart = message.indexOf('>')+1;
  message = message.substring(bodyStart); 
  //Remove powered tag
  bodyEnd = message.indexOf('<div id="');
  message = message.substring(0,bodyEnd);
  return message;
}

function generateErrorMessage(response){
  error = new Ce1susException('Message');
  error.code = response.status;
  error.type = "danger";
  error.message = response.statusText;
  var message = response.data;
  error.description = extractBodyFromHTML(message);
  return error;
}

function getTextOutOfErrorMessage(error){
  var preStart = error.description.indexOf('<p>') +3;
  var preEnd = error.description.indexOf('</p>');
  text = error.description.substring(preStart,preEnd); 
  return text;
}

function handleError(response, messages) {
  var code = response.status;
  var message = getTextOutOfErrorMessage(generateErrorMessage(response));
  if (code === 500) {
    message = "Internal Error occured, please contact your system administrator";
  }
  if (code === 0) {
    message = "Server is probaly gone offline";
  }

  message = {"type":"danger","message":code+" - "+message};
  messages.setMessage(message);
  return true;
}

function generateAPIKey(){
  var random = Math.floor(Math.random()*11);
  var shaObj = new jsSHA(random+"Foobar", "TEXT");
  var hash = shaObj.getHash("SHA-1", "HEX");
  return hash;
}

function getLocals(routeSegment){
  //workaround
  var lenght = routeSegment.chain.length;
  if (lenght > 0) {
    return routeSegment.chain[lenght-1].locals;
  } else {
    return {};
  }
}

function getTlpColor(tlptext) {
  if (tlptext=='Amber'){
    return '#FFBF00';
  } else {
    if (tlptext=='Green'){
      return '#66B032';
    } else {
      if (tlptext=='Red'){
        return '#ff0000';
      } else {
        return '#FFFFFF';
      }
    }
  }
}

function limitStr(string, timLength){
  var length = 30;
  if (timLength){
    length = timLength;
  }
  if (string.length > length) {
    var trimmedString = string.substring(0, length);
    return trimmedString + '...';
  } else {
    return string;
  }
  
}

function calculatePageNumber(i, currentPage, paginationRange, totalPages) {
  var halfWay = Math.ceil(paginationRange/2);
  if (i === paginationRange) {
    return totalPages;
  } else if (i === 1) {
    return i;
  } else if (paginationRange < totalPages) {
    if (totalPages - halfWay < currentPage) {
      return totalPages - paginationRange + i;
    } else if (halfWay < currentPage) {
      return currentPage - halfWay + i;
    } else {
      return i;
    }
  } else {
    return i;
  }
}

function generatePagesArray(currentPage, collectionLength, rowsPerPage, paginationRange) {
  var pages = [];
  var totalPages = collectionLength;//Math.ceil(collectionLength / rowsPerPage);
  var halfWay = Math.ceil(paginationRange / 2);
  var position;
  if (currentPage <= halfWay) {
    position = 'start';
  } else if (totalPages - halfWay < currentPage) {
    position = 'end';
  } else {
    position = 'middle';
  }
  var ellipsesNeeded = paginationRange < totalPages;
  var i = 1;
  while (i <= totalPages && i <= paginationRange) {
    var pageNumber = calculatePageNumber(i, currentPage, paginationRange, totalPages);
    var openingEllipsesNeeded = (i === 2 && (position === 'middle' || position === 'end'));
    var closingEllipsesNeeded = (i === paginationRange - 1 && (position === 'middle' || position === 'start'));
    if (ellipsesNeeded && (openingEllipsesNeeded || closingEllipsesNeeded)) {
      pages.push('...');
    } else {
      pages.push(pageNumber);
    }
    i ++;
  }
  return pages;
}

function getUnvalidated(object){
  return false;
}

function getProposal(object){
  return true;
}

function disableButton(item) {
  if (item.cybox_std){
    return item.cybox_std;
  } else {
    return false;
  }
}

function setModified(item) {
  if (item) {
    if (typeof(item.modified_set) == 'undefined') {
      var d1 = new Date();
      
      item.modified_on = d1.toUTCString();
      item.modified_set = true;
    }
  }
  
}