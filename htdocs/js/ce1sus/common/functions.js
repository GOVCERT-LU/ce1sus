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