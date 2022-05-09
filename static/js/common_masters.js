function modal_open(s_id) {
    $("#delete").val(s_id);
}
  
$("#upload_btn").click(function(){
    $("#upload").trigger('click')
});

function format_creation() {
// alert("Checkig");
    $.ajax({
        url: '/admin/check_excel_sheet/',
        type: 'POST',
        success: function(data) {
            response = JSON.parse(data)
            console.log(response);
            if(response.created !=1) { // if true (1)
                toastr["error"]("Sheet not present", "Error");
            }
        },
        error: function(error){
            toastr["error"]("Some Error", "Error");
        }
    });
}