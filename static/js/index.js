
//(function() {

$(document).ready(function() {

  var QUEEN, clearResizeScroll, conf, getRandomInt, insertI, lol;

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

  QUEEN = ['Is this the real life?', 'Is this just fantasy?', 'Caught in a landslide', 'No escape from reality.', 'Open your eyes',
  'Look up to the skies and see', 'I\'m just a poor boy, I need no sympathy', 'Because I\'m easy come, easy go', 'Little high, little low',
  'Anyway the wind blows doesn\'t really matter to me, to me.', 'Mama, just killed a man', 'Put a gun against his head',
  'Pulled my trigger, now he\'s dead.', 'Mama, life had just begun', 'But now I\'ve gone and thrown it all away.', 'Mama, ooh',
  'Didn\'t mean to make you cry', 'If I\'m not back again this time tomorrow', 'Carry on, carry on as if nothing really matters.',
  'Too late, my time has come', 'Sent shivers down my spine', 'Body\'s aching all the time.', 'Goodbye, everybody, I\'ve got to go',
  'Gotta leave you all behind and face the truth.', 'Mama, ooh (anyway the wind blows)', 'I don\'t wanna die',
  'I sometimes wish I\'d never been born at all.', 'I see a little silhouetto of a man', 'Scaramouche, Scaramouche, will you do the Fandango?',
  'Thunderbolt and lightning', 'Very, very frightening me.', '(Galileo) Galileo.', '(Galileo) Galileo', 'Galileo Figaro', 'Magnifico.',
  'I\'m just a poor boy, nobody loves me.', 'He\'s just a poor boy from a poor family', 'Spare him his life from this monstrosity.',
  'Easy come, easy go, will you let me go?', 'Bismillah! No, we will not let you go. (Let him go!)',
  'Bismillah! We will not let you go. (Let him go!)', 'Bismillah! We will not let you go. (Let me go!)',
  'Will not let you go. (Let me go!)', 'Never, never let you go', 'Never let me go, oh.', 'No, no, no, no, no, no, no.',
  'Oh, mama mia, mama mia (Mama mia, let me go.)', 'Beelzebub has a devil put aside for me, for me, for me.',
  'So you think you can stone me and spit in my eye?', 'So you think you can love me and leave me to die?',
  'Oh, baby, can\'t do this to me, baby', 'Just gotta get out, just gotta get right outta here.', '(Oh, yeah, oh yeah)',
  'Nothing really matters', 'Anyone can see', 'Nothing really matters', 'Nothing really matters to me.', 'Anyway the wind blows.']

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

  // var webSocket;
  $(".groups").click(function() {
    var groupId = $(".grp").text();
    console.log(groupId);
    webSocket.send(groupId);
    webSocket.onmessage = function (evt) {
    alert(evt);
    };
  });

$(window).on('beforeunload', function(){
    webSocket.close();
});

//////////////////////////////////////////////////////

// var ws_scheme = "ws://"


// var inbox = new ReconnectingWebSocket(ws_scheme + location.host + "/receive");
// var outbox = new ReconnectingWebSocket(ws_scheme + location.host + "/submit");

// inbox.onmessage = function(message) {
//   var data = JSON.parse(message.data);
//   receiveI(data);
// //   $("#chat-text").append("<div class='panel panel-default'><div class='panel-heading'>" + $('<span/>').text(data.handle).html() + "</div><div class='panel-body'>" + $('<span/>').text(data.text).html() + "</div></div>");
// //   $("#chat-text").stop().animate({
// //     scrollTop: $('#chat-text')[0].scrollHeight
// //   }, 800);
// // };

// inbox.onclose = function(){
//     console.log('inbox closed');
//     this.inbox = new WebSocket(inbox.url);

// };

// outbox.onclose = function(){
//     console.log('outbox closed');
//     this.outbox = new WebSocket(outbox.url);
// };

// $(".send").on("click", function(event) {
//   event.preventDefault();
//   //var handle = $("#input-handle")[0].value;
//   var handle = "sara"
//   var text   = $("#text")[0].value;
//   outbox.send(JSON.stringify({ handle: handle, text: text }));
//   $("#text")[0].value = "";
// });

//////////////////////////////////////

   insertI = function() {
    var innerText, otvet, friend_name;
    innerText = $.trim($("#text").val());
    friend_name = $('#fr-username').html()
    if (innerText !== "") {
      $(".messages").append("<li class=\"i\"><div class=\"head\"><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span><span class=\"name\"> Me</span></div><div class=\"message\">" + innerText + "</div></li>");
      clearResizeScroll();
      var message ={'msg':innerText,'name':friend_name}
      msg=JSON.stringify(message)
      console.log(msg)
      webSocket.send(msg)
    }
    //when receive message
    receiveI =function(received_msg){
   //   received_msg="tets"
      
      return otvet = setInterval(function() {
        $(".messages").append("<li class=\"friend\"><div class=\"head\"><span class=\"name\">" + $('#fr-username').html() + "</span><span class=\"time\">" + (new Date().getHours()) + ":" + (new Date().getMinutes()) + " AM, Today</span></div><div class=\"message\">" + received_msg + "</div></li>");
        clearResizeScroll();
      return clearInterval(otvet);
      }, getRandomInt(2500, 500));
    }
  };
  //doc ready
 

// $(".groups").click(function())



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

    var webSocket;
    $(function(){
      webSocket= new WebSocket("ws://localhost:7070/ws");
    });



    // $(".send").click(function() {
    //   friend_name=$("div[id='fr-username']").text();

    //   console.log(friend_name);
    //   return insertI();
    // });
//   $("a[name=friend_name]").click(function(){
//   // todo make frind name appear in chat room
//   friend_name=$("a[name='friend_name']").attr('id');
//   console.log("friend_name");
// });

//End doc ready 
  });

