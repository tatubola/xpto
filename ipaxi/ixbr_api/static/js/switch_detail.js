$('tr:visible').filter(':odd').css({'background-color': '#f2f2f2'});
$('tr:visible').filter(':even').css({'background-color': '#FFF'});

$(".port-box").click(function(e){
    var clicked_element = $(e.target);
    if(clicked_element.hasClass('no_display')) {
      return;
    }

    var codigo = $(this).data("codigo");
    var status = $(this).data("status");
    var background = $(this).css("background-color");
    $('#port-information-opened-'+codigo).css('background-color',background);
    if($("#port-information-opened-"+codigo).css("display") == "none"){

      	$("#port-information-opened-"+codigo).css({"display" : "table-row"});
      	if(status !== 'CUSTOMER' && status !== 'AVAILABLE'){
      		$(this).css({"border-left": "3px solid #d9534f", "border-top":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
      		$("#port-information-opened-"+codigo).css({"border-left": "3px solid #d9534f", "border-bottom":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
      	}
      	if(status === 'CUSTOMER'){
      		$(this).css({"border-left": "3px solid #428bca", "border-top":"3px solid #428bca", "border-right": "3px solid #428bca"});
      		$("#port-information-opened-"+codigo).css({"border-left": "3px solid #428bca", "border-bottom":"3px solid #428bca", "border-right": "3px solid #428bca"});
          $.ajax({
            url: '/core/get-tags-by-port/',
            data: { 'port_pk' : codigo, 'ix': ix  },
            dataType: 'json',
            success: function(data){
              var html = "";
              for(var asn in data) {
                  html += asn+": "+data[asn]+"&nbsp;";
              }
              $("#get-tags-"+codigo).html(html);
            }
          });
          e.stopPropagation();
          $.ajax({
            url: '/core/get-lag-port/',
            data: { 'port_pk' : codigo },
            dataType: 'json',
            success: function(data){
              if(data['ports'][0] !== null){
                html = "LAG: { "+data['ports']+" }";
                $("#is-lag-"+codigo).html(html);
              }
            }
          });
          e.stopPropagation();
      	}
    }else{
      	$("#port-information-opened-"+codigo).css({"display" : "none"});
      	$(this).css({"border" : "none"});
      	$("#port-information-opened-"+codigo).css({"border" : "none"});
    }

});
/*
  Function to delete switch_module, called by switch_module_detail.html
  args: module -> switch module representation
        module_key -> switch module pk
*/
function delete_module(module, module_key){

    var confirmed = confirm("Do you want to remove this switch module?:: " + module +"?");
    if(confirmed){
        $.ajax({
            url: '/core/remove-switch-module/',
            data: {
                'pk': module_key,
            },
            dataType: 'json',
        }).done(function(){
            alert("Switch Module removed");
            location.reload(true);
        });
    }
}
