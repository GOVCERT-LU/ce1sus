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

function generateErrorMessage(response){
  error = new Ce1susException('Message');
  error.code = response.status;
  error.type = "danger";
  error.message = response.statusText;
  
  var message = response.data;
  var bodyStart = message.indexOf('<body') + 5;
  var bodyEnd = message.indexOf('</body>');
  message = message.substring(bodyStart,bodyEnd); 
  bodyStart = message.indexOf('>')+1;
  message = message.substring(bodyStart); 
  //Remove powered tag
  bodyEnd = message.indexOf('<div id="');
  message = message.substring(0,bodyEnd);
  
  error.description = message;

  return error;
}

function getTextOutOfErrorMessage(error){
  var preStart = error.description.indexOf('<p>') +3;
  var preEnd = error.description.indexOf('</p>');
  text = error.description.substring(preStart,preEnd); 
  return text;
}

function handleError(response, messages) {
  code = response.status;
  message = getTextOutOfErrorMessage(generateErrorMessage(response));
  if (code === 500) {
    message = "Internal Error occured, please contact your system administrator";
  }
  if (code === 0) {
    message = "Server is probaly gone offline";
  }

  var message = {"type":"danger","message":code+" - "+message};
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
        return '#000000';
      }
    }
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