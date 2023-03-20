function refresh() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/refresh", false);
    xhttp.send();
    postMessage(xhttp.responseText);
  
    setTimeout("refresh()",1000);
  }
  
  refresh();
  
  