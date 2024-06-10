$(function(){
    $('.start-test').click(function(e){
        e.preventDefault();
        
        let card = $(this).closest('.card');
        let details = $(card).find('.details');

        let title = $(details).attr('name');
        let id = Number($(details).attr('id'));
        let time = Number($(details).attr('time'));
        let marks = Number($(details).attr('marks'));
        let question_count = Number($(details).attr('question-length'));
        
        let modal = $('#confirmationDialog');
        $(modal).find('#confirmationDialogLabel').text(title);
        $(modal).find('#test-marks').text(marks+' Marks');
        $(modal).find('#test-time').text(time+' min.');
        $(modal).find('#test-q-count').text(question_count+' Qustions');

        $(modal).find('form').attr('action', '/practice');
        $(modal).find('form').find('input[name="test_id"]').val(id);

        $(modal).modal('show');

    });


});