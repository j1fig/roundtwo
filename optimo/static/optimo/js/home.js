var Home = function () {
  var _aircrafts;
  var _airport;

  var init = function () {
    _requestDemoAirport();
    console.log(_airport);
  }

  var _requestDemoAirport = function () {
    d3.json('/static/optimo/data/lppt.json', function (error, json) {
      if (error) {
        setTimeout(_requestDemoAirport, 15000);
        return console.warn(error);
      }
      _airport = json;
    });
  }

  var _postAircraft = function (aircrafts) {

  }

  var _post = function (url, data) {
    $.ajax({
      url: url,
      type: "POST",
      data: data,
      success: function(data) {
        console.log(data);
        if (!(data['success'])) {
        }
        else {
        }
      },
      error: function (e) {
        console.log(e);
      }
    });
  }

  return {
    init: init,
  }
}();

Home.init();
