
let editTest = () => {
    $('.test-edit').click(function(e){
        e.preventDefault();
        let testID = $(this).attr('test-id');

        if(testID)
        {
            $.ajax({
                url: '/get-test',
                type: 'POST',
                async: false,
                data: {
                    action: 'get',
                    test_id: testID
                },
                success: function(response){
                    if(response)
                    {
                        if(response.status)
                        {
                            let editModal = $('#add-test-modal');

                            $(editModal).find('#test-form-submit').text('Update Test');
                            $(editModal).find('#test-form-submit').attr({
                                'action': 'edit',
                                'test-id': response.data.id
                            });

                            $(editModal).find('#name').val(response.data.name);
                            $(editModal).find('#subject option[value="'+ response.data.subject_id +'"]').prop("selected", true);
                            $(editModal).find('#time').val(response.data.time);
                            $(editModal).find('#marks').val(response.data.marks);

                            let questions = JSON.parse(response.data.questions);
                            $(editModal).find('#selected-question-count').text(questions.length);

                            let selectionForm = $('#question-selection-form');
                            $(selectionForm).find('input').prop('checked', false);
                            for(let i of questions)
                            {
                                $(selectionForm).find('input[value='+ i.question_id +']').prop('checked', true);
                            }

                            $(editModal).modal('show');
                        }
                        else
                        {
                            alertify.set('notifier','position', 'top-right');
                            alertify.error(response.msg);
                        }
                    }
                },
                error: function(error){
                    console.log(error);
                }
            });
        }
        else
        {
            alertify.set('notifier','position', 'top-right');
            alertify.error('Something went wrong, Please try again!');
        }
    });
}

let deleteTest = () => {
    $('.test-delete').click(function(e){
        e.preventDefault();

        let testID = $(this).attr('test-id');

        if(!testID)
        {
            alertify.set('notifier','position', 'top-right');
            alertify.error('Something went wrong, Please try again!');
            return false;
        }

        alertify.confirm('Are you sure, you want to delete this Test?')
                .set('onok', function(closeEvent){
                    if(closeEvent.cancel == false)
                    {
                        $.ajax({
                            url: '/tests',
                            type: 'POST',
                            async: false,
                            data: {
                                action: 'delete',
                                test_id: testID
                            },
                            success: function(response){
                                if(response)
                                {
                                    if(response.status)
                                    {
                                        alertify.set('notifier','position', 'top-right');
                                        alertify.error(response.msg);
                                        setTimeout(() => {
                                            location.reload();
                                        }, 1500);
                                    }
                                    else
                                    {
                                        alertify.set('notifier','position', 'top-right');
                                        alertify.warning(response.msg);
                                    }
                                }
                            },
                            error: function(error){
                                console.log(error);
                            }
                        });
                    }
                })
                .setHeader('')
                .setting({
                    'closable': false,
                    'transition':'zoom',
                    'labels': {
                        ok:'Delete',
                        cancel:'Cancel'
                    }
                }).show();
    });
}


$(function(){

    $('#test-table').DataTable();
    editTest();
    deleteTest();

    $('.page-link').click(function(){
        setTimeout(() => {
            editTest();
            deleteTest();
        }, 500);
    });


    $('#add-test').click(function(e){
        e.preventDefault();
        $('#add-test-modal').attr('hold-value', '0');

        let addModal = $('#add-test-modal');
        $(addModal).find('#test-form-submit').attr('action', 'add');
        $(addModal).find('#test-form-submit').attr('test-id', '');
        $(addModal).find('#test-form-submit').text('Generate Test');
        $(addModal).find('form')[0].reset();
        $(addModal).find('#selected-question-count').text('0');
        $('#question-selection-form')[0].reset();

        $('#add-test-modal').modal('show');
    });


    $('#question-selection-reset').click(function(e){
        e.preventDefault();
        $('#question-selection-form')[0].reset();

    });

    $('#add-test-modal').on('hidden.bs.modal', function(){
        if($(this).attr('hold-value') == '0')
        {
            $(this).find('#test-form-submit').attr('action', 'add');
            $(this).find('#test-form-submit').attr('test-id', '');
            $(this).find('#test-form-submit').text('Generate Test');
        }
    });


    $('#test-form-submit').click(function(e){
        e.preventDefault();
        $(this).closest('.modal').attr('hold-value', '0');

        let form   = $(this).closest('form');
        let action = $(this).attr('action');
        let name        = $(form).find('#name').val()
        let time        = $(form).find('#time').val()
        let marks       = $(form).find('#marks').val()
        let subject_id  = $(form).find('#subject :selected').val()

        if(!name || !time || !marks || marks==0 || !subject_id)
        {
            if(!name)
            {
                $(form).find('#name').addClass('is-invalid');
            }
            if(!time)
            {
                $(form).find('#time').addClass('is-invalid');
            }
            if(!marks || marks==0)
            {
                $(form).find('#marks').addClass('is-invalid');
            }
            if(!subject_id)
            {
                $(form).find('#subject').addClass('is-invalid');
            }

            setTimeout(() => {
                $(form).find('.is-invalid').removeClass('is-invalid');
            }, 2000);

            return false;
        }

    
        const questionList = [];

        $('input.selection-inputs:checkbox:checked').each(function(e){
            questionList.push({
                'question_id': $(this).val(),
                'marks': Number($(this).attr('marks'))
            });
        });

        let formData = {};
        if(action == 'add')
        {
            formData = {
                action: action,
                name: name,
                time: time,
                marks: marks,
                subject_id: subject_id,
                questions: JSON.stringify(questionList)
            }
        }
        else if(action == 'edit')
        {
            formData = {
                action: action,
                test_id: $('#test-form-submit').attr('test-id'),
                name: name,
                time: time,
                marks: marks,
                subject_id: subject_id,
                questions: JSON.stringify(questionList)
            }
        }


        $('#loader').modal('show');
        $.ajax({
            url: '/tests',
            type: 'POST',
            async: false,
            data: formData,
            success: function(response){
                if(response.status)
                {
                    alertify.set('notifier','position', 'top-right');
                    alertify.success(response.msg);
                }
                else
                {
                    alertify.set('notifier','position', 'top-right');
                    alertify.error(response.msg);
                }
            },
            error: function(error){
                console.log(error);
            },
            complete: function(event, xhr, settings) {
                $('#add-test-modal').modal('hide');
                setTimeout(() => {
                    if(xhr == "success")
                    {
                        setTimeout(() => {
                            location.reload();
                        }, 1500);
                    }
                    else
                    {
                        $('#loader').modal('hide');
                    }
                }, 1000);
            }
        });

    });

    $('#subject-filter').on('change', function(){
        let currentSubject = $(this).val();
        let subjectList = $('#question-selection-form').find('.card');

        if(currentSubject)
        {
            for(let i=0; i<subjectList.length; i++)
            {
                if($(subjectList[i]).attr('id') == 'subject-'+currentSubject)
                    $(subjectList[i]).show();
                else
                    $(subjectList[i]).hide();
            }
        }
        else
        {
            for(let i=0; i<subjectList.length; i++)
                $(subjectList[i]).show()
        }
    });


    $('#question-selection-btn').click(function(){
        $('#add-test-modal').attr('hold-value', '1');
        $('#add-test-modal').modal('hide');
        $('#question-selection-panel').modal('show');
    });


    $('#submit-selection').click(function(e){
        e.preventDefault();

        let form = $('#question-selection-form');
    
        let questionList = [];
        let selectedQuestions = $(form).find('input[type="checkbox"]:checked');

        
        let count = 0;
        let marks = 0;

        for(let i=0; i<selectedQuestions.length; i++)
        {

            count += 1;
            marks += Number($(selectedQuestions[i]).attr('marks'));
            questionList.push({
                'question_id': $(selectedQuestions[i]).val(),
                'marks':Number($(selectedQuestions[i]).attr('marks'))
            });
        }


        $('#test-form').find('#selected-question-count').text(count);
        $('#test-form').find('#marks').val(marks);

        $('#question-selection-panel').modal('hide');
        $('#add-test-modal').modal('show');
    });

});