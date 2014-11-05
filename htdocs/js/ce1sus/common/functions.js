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

function handleError(response, messages) {
  code = response.status;
  message = response.statusText;
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