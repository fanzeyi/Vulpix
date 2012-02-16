$(document).ready(function () {
    $('#lang_select > a.btn').click(function () {
        var lang = $(this).prop('id'); 
        $("#lang_select > a.btn").removeClass('btn-success'); 
        $(this).addClass('btn-success'); 
        $("input[name='lang']").val(lang); 
        return false; 
    }); 
}); 
