//(function() {
//var webSocket;
$(document).ready(function() {

  $("#status_button").change(function(){
      var st=$("#status_button").prop('checked');
      $.ajax({
        method: 'get',
        url:"/statuschange",
        data:{status:st},
        success: function(res){
          if(st){
            console.log(st) 
            $("#stlamp").addClass('on');
            $("#stlamp").removeClass('off');
          }
          else if(!st){
            $("#stlamp").addClass('off');
            $("#stlamp").removeClass('on');
          }
          console.log("status request done");
        }
      })
  });

  if($("#messages_div").length!=0){
    $.ajax({
        method: 'get',
        url:"/removemsgs",
        success: function(res){
          
          console.log("status request done");
        }
      })
  }

//End doc ready 
});