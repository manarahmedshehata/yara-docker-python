  var webSocket;
$(document).ready(function() {

  var clearResizeScroll, conf, getRandomInt, insertI, lol;

  conf = {
    cursorcolor: "#696c75",
    cursorwidth: "4px",
    cursorborder: "none"
  };

  lol = {
    cursorcolor: "#cdd2d6",
    cursorwidth: "4px",
    cursorborder: "none"
  };
  getRandomInt = function(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  };

  clearResizeScroll = function() {
    $("#text").val("");
    $(".messages").getNiceScroll(0).resize();
    return $(".messages").getNiceScroll(0).doScrollTop(999999, 999);
  };


   my_name = $("#stlamp").text()
   insertI = function() {
    var innerText, otvet, friend_name;
    innerText = $.trim($("#text").val());
    friend_name = $('#fr-username').html();


    if (innerText !== "") {

      var message ={'msg':innerText,'fname':friend_name,'myname':my_name}
      msg=JSON.stringify(message)
      console.log(msg)
      webSocket.send(msg)
    }};
    //when receive message
    receiveI =function(friendn,sms){
      received_msg=sms
      console.log("hiiiiiiiiiiiiiiiiiiiiii")
      return otvet = setInterval(function() {
        if(friendn != my_name){
          $(".messages").append("<li class=\"i\"><div class=\"head\"><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span><span class=\"name\"> Me</span></div><div class=\"message\">" + received_msg + "</div></li>");
        }

      else{
        $(".messages").append("<li class=\"friend\"><div class=\"head\"><span class=\"name\">" + $('#fr-username').html() + "</span><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span></div><div class=\"message\">" + received_msg + "</div></li>");
      }
        clearResizeScroll();
      return clearInterval(otvet);
      }, getRandomInt(250, 50));
    };
  //doc ready
    $(".list-pages").niceScroll(conf);
    $(".messages").niceScroll(lol);
    $("#text").keypress(function(e) {
      if (e.keyCode === 13) {
        insertI();
        return false;
      }
    });


    $(function(){
      webSocket= new WebSocket("ws://localhost:7070/ws");
      webSocket.onmessage = function(e){
            console.log("tessssssssssssssst")
            console.log(e.data)
            var data=JSON.parse(e.data)
            receiveI(data['name'],data['msg'])
    }
    });

    $(".send").click(function() {



      return insertI();
    });

  });
