$(document).ready(function() {
$('#start_time').datetimepicker({
    onClose: function(dateText, inst) {
        var endDateTextBox = $('#end_time');
        if (endDateTextBox.val() != '') {
            var testStartDate = new Date(dateText);
            var testEndDate = new Date(endDateTextBox.val());
            if (testStartDate > testEndDate)
                endDateTextBox.val(dateText);
        }
        else {
            endDateTextBox.val(dateText);
        }
    },
    onSelect: function (selectedDateTime){
        var start = $(this).datetimepicker('getDate');
        $('#end_time').datetimepicker('option', 'minDate', new Date(start.getTime()));
    }
});
$('#end_time').datetimepicker({
    onClose: function(dateText, inst) {
        var startDateTextBox = $('#start_time');
        if (startDateTextBox.val() != '') {
            var testStartDate = new Date(startDateTextBox.val());
            var testEndDate = new Date(dateText);
            if (testStartDate > testEndDate)
                startDateTextBox.val(dateText);
        }
        else {
            startDateTextBox.val(dateText);
        }
    },
    onSelect: function (selectedDateTime){
        var end = $(this).datetimepicker('getDate');
        $('#start_time').datetimepicker('option', 'maxDate', new Date(end.getTime()) );
    }
});
}); 
