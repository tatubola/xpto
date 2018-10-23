$('tr:visible').filter(':odd').css({'background-color': '#f2f2f2'});
$('tr:visible').filter(':even').css({'background-color': '#FFF'});


$(".basic-ip-info-detail").click(function(e){
      	var open = $(this).data("open");
      	var ipv4 = $(this).data("ip");
      	var ipv6 = $(this).data("ipv");
      	toggle = true;
      	var html = "";
      	var background = $(this).css("background-color");
    	$("#detail-open-"+open).css('background-color',background);
    	if($("#detail-open-"+open).css("display") === "none"){
    	$.ajax({
		    url: '/core/'+code+'/get-ip-informations-by-click/',
		    data:{
		    	'ipv4' : ipv4,
		    	'ipv6' : ipv6,
		    	'ip_opened' : open
		    },
		    dataType: 'json',
		    success: function(data){

			    if(data.asn_ipv4 && data.asn_ipv6){
			    	toggle = true;
			    	// display block in the detail of ip clicked
			    	$("#detail-open-"+data.ip_opened).css({"display" : "table-row"});
			    	// number asn of ipv4 of tr clicked
			    	$("#ipv4-asn-"+data.ip_opened).html(data.asn_ipv4);
			    	// name asn of ipv4 of tr clicked
			    	$("#ipv4-name-"+data.ip_opened).html(data.ipv4_name);
			    	// number asn of ipv6 of tr clicked
			    	$("#ipv6-asn-"+data.ip_opened).html(data.asn_ipv6);
			    	// name asn of ipv6 of tr clicked
			    	$("#ipv6-name-"+data.ip_opened).html(data.ipv6_name);
			    	// style of detail of ip clicked, border red because of ip is allocated
			    	$("#detail-open-"+open).css({"border-left": "3px solid #d9534f", "border-bottom":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
			    	// style of tr of ip clicked, border red because of ip is allocated
			    	$("#border-"+data.ip_opened).css({"border-left": "3px solid #d9534f", "border-top":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
			    	var ipv4_asn_url = $('#ipv4-detail-paragraph-asn-'+open).find('a').attr('href').replace('0', data.asn_ipv4)
			    	$('#ipv4-detail-paragraph-asn-'+open).find('a').attr('href', ipv4_asn_url)
			    	var ipv6_asn_url = $('#ipv6-detail-paragraph-asn-'+open).find('a').attr('href').replace('0', data.asn_ipv6)
			    	$('#ipv6-detail-paragraph-asn-'+open).find('a').attr('href', ipv6_asn_url)
			    	var ipv4_name_url = $('#ipv4-detail-paragraph-name-'+open).find('a').attr('href').replace('0', data.asn_ipv4)
			    	$('#ipv4-detail-paragraph-name-'+open).find('a').attr('href', ipv4_name_url)
			    	var ipv6_name_url = $('#ipv6-detail-paragraph-name-'+open).find('a').attr('href').replace('0', data.asn_ipv6)
			    	$('#ipv6-detail-paragraph-name-'+open).find('a').attr('href', ipv6_name_url)

			    }else if(data.asn_ipv4){
			    	toggle = true;
			    	// display block in the detail of ip clicked
			    	$("#detail-open-"+data.ip_opened).css({"display" : "table-row"});
			    	// number asn of ipv4 of tr clicked
			    	$("#ipv4-asn-"+data.ip_opened).html(data.asn_ipv4);
			    	// name asn of ipv4 of tr clicked
			    	$("#ipv4-name-"+data.ip_opened).html(data.ipv4_name);
			    	// the ipv6 is free, then the text 'IP no allocated' will appear
			    	html = "<td colspan='4'><center><p style='color:green;'>IP is Free</p></center></td>";
			    	$("#ipv6-detail-"+data.ip_opened).html(html);
			    	// style of detail of ip clicked, border red because of ip is allocated
			    	$("#detail-open-"+open).css({"border" : "1px solid red", "border-top" : "none"});
			    	// style of tr of ip clicked, border red because of ip is allocated
			    	$("#border-"+data.ip_opened).css({"border" : "1px solid red", "border-bottom" : "none"});
			    	$('#ipv4-detail-'+open).find('a').attr('href').replace('0', open)
			    }else if(data.asn_ipv6){
			    	// display block in the detail of ip clicked
			    	$("#detail-open-"+data.ip_opened).css({"display" : "table-row"});
			    	// number asn of ipv6 of tr clicked
			    	$("#ipv6-asn"+data.ip_opened).html(data.asn_ipv6);
			    	// name asn of ipv6 of tr clicked
			    	$("#ipv6-name"+data.ip_opened).html(data.ipv6_name);
			    	// the ipv4 is free, then the text 'IP is Free' will appear
			    	html = "<td colspan='3'><center><p style='color:green;'>IP is Free</p></center></td>";
			    	$("#ipv4-detail-"+data.ip_opened).html(html);
			    	// style of detail of ip clicked, border red because of ip is allocated
			    	$("#detail-open-"+open).css({"border-left": "3px solid #d9534f", "border-bottom":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
			    	// style of tr of ip clicked, border red because of ip is allocated
			    	$("#border-"+data.ip_opened).css({"border-left": "3px solid #d9534f", "border-top":"3px solid #d9534f", "border-right": "3px solid #d9534f"});
			    	$('#ipv6-detail-'+open).find('a').attr('href').replace('0', open)
			    }else{
			    	// display block in the detail of ip clicked
			    	$("#detail-open-"+data.ip_opened).css({"display" : "table-row"});
			    	// the ipv4 and ipv6 are free, then the text 'IP is Free' will appear
			    	html += "<td colspan='7'><center><p style='color:green;'>IPs are Free</p></center></td>";
			    	$("#detail-open-"+data.ip_opened).html(html);
			    	// style of detail of ip clicked, border green because of ip is free
			    	$("#detail-open-"+open).css({"border-left": "3px solid #5cb85c", "border-bottom":"3px solid #5cb85c", "border-right": "3px solid #5cb85c"});
			    	// style of tr of ip clicked, border red because of ip is green
			    	$("#border-"+data.ip_opened).css({"border-left": "3px solid #5cb85c", "border-top":"3px solid #5cb85c", "border-right": "3px solid #5cb85c"});
			    }

		    }

	});
    }else{
    	$("#detail-open-"+open).css({"display" : "none"});
    	$(this).css({"border" : "none"});
    }



});

$("#pesquisar-asn-ips").click(function(){
    var asn = $("#asn").val();
    var i = 0;
    if($("#input-error").is(":visible")){
		$("#input-error").addClass('hidden');
	} else if($("#input-warning").is(":visible")) {
		$("#input-warning").addClass('hidden');
	}
    if(asn !== ""){
      	$.ajax({
	      	url: '/core/'+code+'/get-match-ips-by-asn-search/',
		    data:{
		    	'asn' : asn

		    },
		    dataType: 'json',
		    success: function(data){
				if($("#input-error").is(":visible")) {
					$("#input-error").addClass('hidden');
				}
				$("#input-warning").removeClass('hidden');
		    	if(data.ipv4.length === 0 && data.ipv6.length === 0) {
                    $(".basic-ip-info-detail").css({"display" : "table-row"});
                }
                else {
                    $("#input-warning").addClass('hidden');
		    		$(".more-ip-info-detail").css({"display" : "none"});
		    		$(".basic-ip-info-detail").css({"border" : "none"});
		    		// Function for to open detail of ipv4
		    		search_asn_ip(data);
		    	}
		    }
	    });
    }else{
      	$(".basic-ip-info-detail").css({"display" : "table-row"});
      	$("#input-error").removeClass('hidden');
    }

});

$("#asn").keyup(function(e){
    e.preventDefault();
    var asn = $("#asn").val();
    if(asn == ""){
      	$(".basic-ip-info-detail").css({"display" : "table-row"});
      	$(".more-ip-info-detail").css({"display" : "none"});
      	$(".more-ip-info-detail").css({"border" : "none"});
      	$(".basic-ip-info-detail").css({"border" : "none"});
      	$("#input-warning").addClass('hidden')
      	$("#input-error").addClass('hidden')
    }
    if(e.which == 13){
      	$("#pesquisar-asn-ips").click();
    }
});

//Filter IPs
$("#filter_ips").change(function(){
	$(".more-ip-info-detail").css({"display" : "none"});
	$(".basic-ip-info-detail").css({"border" : "none"});
	var status = $(this).val();
	var type_ip = $('option:selected').data("typeip");
	if(status === "ALL" || status === ""){
		$(".basic-ip-info-detail").css({"display" : "table-row"});
	}else{
		filter_ips(type_ip, status);
	}
	$('tr:visible').filter(':odd').css({'background-color': '#f2f2f2'});
	$('tr:visible').filter(':even').css({'background-color': '#FFF'});
});
//Function search_asn_ip list of ips by asn
function search_asn_ip(data){
	var i = 0;
    $(".basic-ip-info-detail").hide();
    for(i=0; i<data.ipv4.length; i++){
        $(".basic-ip-info-detail").each(function(){
            if($(this).data("ip") == data.ipv4[i]){
                $(this).show();
            }
        });
    }

    for(i=0 ;i<data.ipv6.length; i++){
        $(".basic-ip-info-detail").each(function(){
            if($(this).data("ipv") == data.ipv6[i]){
                $(this).show();
            }
		});
	}
}

//Function filter IPs
function filter_ips(type_ip, status){
	$(".basic-ip-info-detail").css({"display" : "none"});
		$(".status-"+type_ip).each(function(){
			var open = $(this).data("open");
			var stat = $(this).text();
				
			if(stat === status){
				if($("#border-"+open).css("display") === "none"){
					$("#border-"+open).css({"display" : "table-row"});
				}
			}else{
				$("#border-"+open).css({"display" : "none"});
			}
	});
}
