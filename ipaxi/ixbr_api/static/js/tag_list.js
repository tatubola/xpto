$('document').ready(function() {
	display_selected_tags();

	function display_selected_tags(){
		if($(".custom-select").val() == "all"){
			$(".filter-status").empty();
			$(".filter-status").append("all")
			$(".AVAILABLE-status").show();
			$(".PRODUCTION-status").show();
			$(".ALLOCATED-status").show();
		} else if ($(".custom-select").val() == "available"){
			$(".filter-status").empty();
			$(".filter-status").append("only available")
			$(".AVAILABLE-status").show();
			$(".PRODUCTION-status").hide();
			$(".ALLOCATED-status").hide();
		} else if ($(".custom-select").val() == "production"){
			$(".filter-status").empty();
			$(".filter-status").append("only production")
			$(".AVAILABLE-status").hide();
			$(".PRODUCTION-status").show();
			$(".ALLOCATED-status").hide();
		} else if ($(".custom-select").val() == "allocated"){
			$(".filter-status").empty();
			$(".filter-status").append("only allocated")
			$(".AVAILABLE-status").hide();
			$(".PRODUCTION-status").hide();
			$(".ALLOCATED-status").show();
		}

		/**************************
		**** Stripped color tr ****
		**************************/
		$('tr:visible').filter(':odd').css({'background-color': '#f2f2f2'});
		$('tr:visible').filter(':even').css({'background-color': '#FFF'});
	}
	toggle = false;

	/*********************************
	*** AJAX request by search ASN ***
	*********************************/
	$("#search-btn").click(function(e) {
		location.hash = "";

		if($("#input-error").is(":visible")){
			$("#input-error").addClass('hidden');
		} else if($("#input-warning").is(":visible")) {
			$("#input-warning").addClass('hidden');
		}

		var value_asn = $("#asn-search-tag").val();
		if (value_asn.length) {
		  	$.ajax({
			    url: '/core/'+code+'/get-match-tags-by-asn-search/',
			    data: {
			      'asn': value_asn,
			    },
			    dataType: 'json', 
			    success: function (data) {
			      	if (data.tag) {
			      		$(".main-info").css({"border" : "none"});
					    $(".custom-select").val("filter")
						$(".filter-status").empty();
						$(".filter-status").append("only filtered")
						$(".main-info").hide()
						$(".more-info").hide()
					    $(".append-element").empty();
					    for(var i = 0; i < data.tag.length; i++){
						    $("#tag" + data.tag[i] + "-name").append("<span class='append-element'>"+data.organization+"</span></a>");
							$("#tag" + data.tag[i] + "-asn").append("<span class='append-element'>"+data.asn+"</span>");
						    toggle = true;
						    $(".tag-"+data.tag[i]+"-main-info").show()
						}
					} else {
						if($("#input-error").is(":visible")) {
							$("#input-error").addClass('hidden');
						}
						$("#input-warning").removeClass('hidden');
					}
					toggle = false;
		    	}
		  	});
		  	value_asn = '';
		} else {
			$("#input-error").removeClass('hidden');
		}
		e.stopPropagation();
	});

	/***********************************
	*** AJAX request by click action ***
	***********************************/
	$("tr").click(function(e) {
		var value_tag = $(this).data("tag");;
		var tag_uuid = $(this).data("id");
		var status_tag = $(this).data("status");
        var display = $("#display-"+tag_uuid).css("display");
        if(display === "none"){
        	$.ajax({
				url: '/core/'+code+'/get-tag-informations-by-click/',
				data: {
				  'tag': tag_uuid,
				},
				dataType: 'json',
				success: function (data) {
					if (data.asn) {
						$("#display-"+tag_uuid).css({"display" : "table-row"});
						color_border(tag_uuid, display);
						$("#tag" + value_tag+ "-name").html("<span class='append-element'>"+data.organization+"</span>");
						$("#tag" + value_tag + "-asn").html("<span class='append-element'>"+data.asn+"</span>");
				    	$("#asn-url-"+tag_uuid).attr('href', '/core/as/'+data.asn+"/");
				    	$("#name-url-"+tag_uuid).attr('href', '/core/ix/'+code+'/'+data.asn+'/');
					}else{
						alert("Tag was not associated with any service!")
					}
				}
			});
        }if(display === "table-row"){
        	color_border(tag_uuid, display);
        	$("#display-"+tag_uuid).css({"display" : "none"});
        }
		value_asn = '';
	});

	/**************************************************************
	****** Function to change color of border at event click ******
	**************************************************************/
	function color_border(tag_uuid, display){
		if(display === 'none'){
			$("#main-info-"+tag_uuid).css({"border" : "1px solid red", "border-bottom" : "none"});
			$("#display-"+tag_uuid).css({"border" : "1px solid red", "border-top" : "none"});
		}if(display === "table-row"){
			$("#main-info-"+tag_uuid).css({"border" : "none"});
			$("#display-"+tag_uuid).css({"border" : "none"});
		}
	}

	/*********************************************
	*** Function to search if ENTER is pressed ***
	*********************************************/
    $("#asn-search-tag").keydown(function(event) {
		if (event.keyCode == 13) {
			$("#search-btn").click();
		}
	})

	/*********************************
	** Function to filter by status **
	*********************************/
	$(".custom-select").change(function(){
		$(".more-info").hide()
		$(".main-info").css("border", "none");
		$("#asn-search-tag").val("");
		display_selected_tags();
	});

	$('#asn-search-tag').keyup(function(){
		var value = $(this).val();
		if(value == ''){
			$(".main-info").show();
			$(".more-info").hide();
			$(".main-info").css({"border" : "none"});
		}
	})

});
