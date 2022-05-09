$("select#sem").change(function(){
		alert("Subject Searching!!");
		var d = $('#dept').val();
		var s = $('#sem').val();
		var dat = {dept: d, sem: s};	
		$.ajax({
			url: '/quiz/getsubjects/',
			data: dat,
			type: 'POST',
			success: function(response){
				console.log(response);
				var subjects = JSON.parse(response);
				// console.log(data)
				$('#sub').empty().append('<option selected="selected" value="" disabled>Select</option>')
				for (var i = 0; i < subjects.length; i++) {
            		$('#sub').append($("<option></option>").attr("value", subjects[i]).text(subjects[i])); 
        		}
				// var subjects = JSON.parse(response.sub);
				// console.log(data)
				
			},
			error: function(error){
				console.log(error);
			}
		});
	});
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();
 if(dd<10){
        dd='0'+dd
    } 
    if(mm<10){
        mm='0'+mm
    } 

today = yyyy+'-'+mm+'-'+dd;
document.getElementById("quiz_date").setAttribute("min", today);
// $(function(){
	
// 	$('button').click(function(){
// 		var user = $('#inputUsername').val();
// 		var pass = $('#inputPassword').val();
// 		$.ajax({
// 			url: '/signUpUser',
// 			data: $('form').serialize(),
// 			type: 'POST',
// 			success: function(response){
// 				console.log(response);
// 			},
// 			error: function(error){
// 				console.log(error);
// 			}
// 		});
// 	});
// });