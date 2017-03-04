
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
          //console.log()
          console.log(st)
          console.log(jQuery.type(st))
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


//End doc ready 
  });