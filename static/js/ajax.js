//
// As mentioned at http://en.wikipedia.org/wiki/XMLHttpRequest
//
if( !window.XMLHttpRequest ) XMLHttpRequest = function()
{
  try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
  try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
  throw new Error("Could not find an XMLHttpRequest alternative.")
};

var method = { POST:'POST', GET:'GET'};

//
// Makes an AJAX request to a local server function w/ optional arguments
//
// m:submit form method POST or GET
// functionName: the name of the server's AJAX function to call
// opt_argv: an Array of arguments for the AJAX function
//

function Request(m, function_name, opt_argv) {

    if (!opt_argv)
    opt_argv = new Array();

    // Find if the last arg is a callback function; save it
    var callback = null;
    var len = opt_argv.length;
    if (len > 0 && typeof opt_argv[len-1] == 'function') {
        callback = opt_argv[len-1];
        opt_argv.length--;
    }
    var async = (callback != null);
    
    // See http://en.wikipedia.org/wiki/XMLHttpRequest to make this cross-browser compatible
    var req = new XMLHttpRequest();
    var body = "";
    if(m == method.POST)
    {
        // Build an Array of parameters, w/ function_name being the first parameter
        var params = new Array(function_name);
        for (var i = 0; i < opt_argv.length; i++) {
        params.push(opt_argv[i]);
        }
        body = JSON.stringify(params);

        // Create an XMLHttpRequest 'POST' request w/ an optional callback handler
        req.open('POST', '/rpc', async);

        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req.setRequestHeader("Content-length", body.length);
        req.setRequestHeader("Connection", "close");
    }
    else if(m == method.GET)
    {
        // Encode the arguments in to a URI
        var query = 'action=' + encodeURIComponent(function_name);
        for (var i = 0; i < opt_argv.length; i++) {
          var key = 'arg' + i;
          var val = JSON.stringify(opt_argv[i]);
          query += '&' + key + '=' + encodeURIComponent(val);
        }
        query += '&time=' + new Date().getTime(); // IE cache workaround

        // Create a 'GET' request w/ an optional callback handler
        req.open('GET', '/rpc?' + query, async);
    }
    if (async) {
        req.onreadystatechange = function() {
            if(req.readyState == 4 && req.status == 200) {
                var response = null;
                try {
                    response = JSON.parse(req.responseText);
                } catch (e) {
                    response = req.responseText;
                }
                callback(response);
                $('#msg').delay(300).fadeOut();
            }
        }
    }
    $('#msg').show();
  // Make the actual request
    if(m == method.POST)
        req.send(body);
    else if(m == method.GET)
        req.send(null);
}


// Adds a stub function that will pass the arguments to the AJAX call
function InstallFunction(m, obj, functionName) {
  obj[functionName] = function() { Request(m, functionName, arguments); }
}

server = {};
InstallFunction(method.POST, server, "item");
InstallFunction(method.POST, server, "reserve");
InstallFunction(method.POST, server, "cancelReserved");
InstallFunction(method.POST, server, "todo");
InstallFunction(method.POST, server, "customer");
InstallFunction(method.POST, server, "removeTask");
InstallFunction(method.POST, server, "clearFinishedTasks");
InstallFunction(method.GET, server, "getItems");
InstallFunction(method.GET, server, "getReserved");
InstallFunction(method.GET, server, "getReservedInfo");
InstallFunction(method.GET, server, "getCustomerReservedRecords");
InstallFunction(method.GET, server, "getCustomerCount");
InstallFunction(method.GET, server, "getCustomer");
InstallFunction(method.GET, server, "queryCustomerActivities");
InstallFunction(method.GET, server, "queryItemInfo");
InstallFunction(method.GET, server, "queryTasks");
InstallFunction(method.GET, server, "queryBirthdays");
InstallFunction(method.GET, server, "bindWorkspace");