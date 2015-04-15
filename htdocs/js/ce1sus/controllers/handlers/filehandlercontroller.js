/**
 * 
 */

/**
 * 
 */

app.controller("attrfileController", function($scope, $timeout, $log) {
  function converToRestFile(file) {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
      // Great success! All the File APIs are supported.
      if (file) {
          var data;
          $timeout(function() {
            var fileReader = new FileReader();
            fileReader.readAsDataURL(file);
            fileReader.onload = function(e) {
              $timeout(function() {
                //I am only interested in the base 64 encodings
                file.data =  e.target.result.split(",")[1];
              });
            };
          });
      } else {
        alert('Error No file provided');
      }
    } else {
      alert('The File APIs are not fully supported in this browser.');
    }
  }

  
  $scope.setFileValue = function(files){
    var file = files[0];
    
    converToRestFile(file);
    $scope.attribute.value = {};
    //TODO: find a way to send this without data.data
    $scope.attribute.value.data = file;
    $scope.attribute.value.name = file.name;
  };
});

app.controller("reffileController", function($scope, $timeout, $log) {
  function converToRestFile(file) {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
      // Great success! All the File APIs are supported.
      if (file) {
          var data;
          $timeout(function() {
            var fileReader = new FileReader();
            fileReader.readAsDataURL(file);
            fileReader.onload = function(e) {
              $timeout(function() {
                //I am only interested in the base 64 encodings
                file.data =  e.target.result.split(",")[1];
              });
            };
          });
      } else {
        alert('Error No file provided');
      }
    } else {
      alert('The File APIs are not fully supported in this browser.');
    }
  }

  
  $scope.setFileValue = function(files){
    var file = files[0];
    
    converToRestFile(file);
    $scope.resource.value = {};
    //TODO: find a way to send this without data.data
    $scope.resource.value.data = file;
    $scope.resource.value.name = file.name;
  };
});