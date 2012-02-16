$(document).ready(function () {
    var related_list = new Array(); 
    function add_related_problem() {
        var val = $("#related_problem").val(); 
        if(val.search("^-?\\d+$") == 0) {
            if($.inArray(val, related_list) != -1) {
                return false; 
            }
            $.get('/api/problem/get/' + val, null, function(text) {
                $('#related_problem_list').append('<li class="related"><a href="/problem/' + val + '" target="_blank">' + text + '</a><a class="close" data-dismiss="alert" value="' + val + '" href="#"><i class="icon-remove-sign"></i></a></li>'); 
                $('form.new_note').append('<input id="related_' + val + '" type="hidden" name="link_problem[]" value="' + val + '" />'); 
                related_list.push(val); 
                $('#related_problem').val(''); 
                $('#related_problem').prop('disabled', false); 
                $('#related_problem_submit').removeClass('disabled'); 
                $('.related .close').click(function () {
                    var pid = $(this).attr('value');
                    var index = related_list.indexOf(val); 
                    related_list.splice(index, 1); 
                    $('#related_' + pid).remove(); 
                }); 
            }); 
            $('#related_problem_submit').addClass('disabled'); 
            $('#related_problem').prop('disabled', true); 
        }
    }
    $('form').ajaxError(function() {
        $('#related_problem_submit').removeClass('disabled'); 
        $('#related_problem').prop('disabled', false); 
    }); 
    $('.disabled').click(function() {
        return false; 
    }); 
    $('#related_problem').keypress(function (e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        if(code == 13) {
            add_related_problem(); 
            return false; 
        }
    }); 
    $("#related_problem_submit").click(function () {
        add_related_problem(); 
        return false; 
    }); 
}); 
