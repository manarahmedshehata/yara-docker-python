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

  // insertI = function() {
  //   var innerText, otvet;
  //   innerText = $.trim($("#text").val());
  //   if (innerText !== "") {
  //     $(".messages").append("<li class=\"i\"><div class=\"head\"><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span><span class=\"name\"> Me</span></div><div class=\"message\">" + innerText + "</div></li>");
  //     clearResizeScroll();
  //     return otvet = setInterval(function() {
  //       $(".messages").append("<li class=\"friend\"><div class=\"head\"><span class=\"name\">" + $('#fr-username').html() + "</span><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span></div><div class=\"message\">" + QUEEN[getRandomInt(0, QUEEN.length - 1)] + "</div></li>");
  //       clearResizeScroll();
  //       return clearInterval(otvet);
  //     }, getRandomInt(2500, 500));
  //   }
  // };
   my_name = $("#stlamp").text()
   insertI = function() {
    var innerText, otvet, friend_name;
    innerText = $.trim($("#text").val());
    friend_name = $('#fr-username').html();
    
    //console.log(m)
    if (innerText !== "") {
      // $(".messages").append("<li class=\"i\"><div class=\"head\"><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span><span class=\"name\"> Me</span></div><div class=\"message\">" + innerText + "</div></li>");
      // clearResizeScroll();
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
      }, getRandomInt(2500, 500));
    };
  //doc ready
 





//End main function 
//}).call(this);

// var webSocket;
// $(function(){
//   webSocket= new WebSocket("ws://localhost:8888/ws");
// });

    //var friend_name;
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
      //friend_name=$("div[id='fr-username']").text();

      //console.log(friend_name);
      return insertI();
    });
//   $("a[name=friend_name]").click(function(){
//   // todo make frind name appear in chat room
//   friend_name=$("a[name='friend_name']").attr('id');
//   console.log("friend_name");
// });
//End doc ready 
  });