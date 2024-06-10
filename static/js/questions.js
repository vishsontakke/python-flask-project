let deleteQuestion = (question_id) => {
    
    $('#loader').modal('show');
    $.ajax({
        url: '/questions',
        type: 'POST',
        async: false,
        // headers: {
        //     'X-CSRFToken': csrf_token.value
        // },
        data: {
            action: 'delete',
            question_id: question_id
        },
        success: function(response){
            $('#loader').modal('hide');
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
            $('#loader').modal('hide');
            console.log(error);
        }
    });
}


let editQuestion = () => {
    $('.question-edit').click(function(){
        let questionId = $(this).attr('question-id');

        if(questionId)
        {
            $.ajax({
                url: '/get-question',
                type: 'POST',
                async: false,
                data: {
                    action: 'get',
                    question_id: questionId
                },
                success: function(response){
                    if(response)
                    {
                        if(response.status)
                        {
                            let editModal = $('#add-question-modal');

                            $(editModal).find('#add-questionLabel').text('Update Question');
                            $(editModal).find('#question-form-submit').text('Update');
                            $(editModal).find('#question-form-submit').attr('action-name', 'edit');
                            $(editModal).find('#question-form-submit').attr('question-id', response.data.question.id);

                            $(editModal).find('#subject_id').find('option[value="'+response.data.question.subject_id+'"]').prop('selected', true);
                            $(editModal).find('#level').find('option[value="'+response.data.question.level+'"]').prop('selected', true);
                            $(editModal).find('#marks').val(response.data.question.marks);
                            $(editModal).find('#question').summernote('code', response.data.question.value);

                            if(response.data.options != false)
                            {
                                for(let i=0; i<response.data.options.length; i++)
                                {
                                    $(editModal).find('#options'+(i+1)).summernote('code', response.data.options[i].value);
                                    $(editModal).find('#options'+(i+1)).attr('option-id', response.data.options[i].id);
                                    if(response.data.options[i].is_correct == 1)
                                    {
                                        $(editModal).find('input[value="option-'+(i+1)+'"]').prop("checked", true);
                                    }
                                }
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
    });
}


let confirmDeleteQuestion = () => {
    $('.question-delete').click(function(e){
        e.preventDefault();

        let question_id = $(this).attr('question-id');

        if(!question_id)
            return false;

        alertify.confirm('Are you sure, you want to delete this question?')
                .set('onok', function(closeEvent){
                    if(closeEvent.cancel == false)
                    {
                        deleteQuestion(question_id)
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

    $('#question').summernote({
        inheritPlaceholder: true,
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'paragraph']],
            // ['insert', ['picture']],
        ]
    });
    $('#options1, #options2, #options3, #options4').summernote({
        // minHeight: null,
        // maxHeight: null,
        // focus: true,
        // styleWithSpan: false,
        inheritPlaceholder: true,
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul', 'ol', 'paragraph']],
            // ['insert', ['picture']],
        ]
        // codemirror: {
        //     theme: 'sandstone'
        //   }
        // callbacks: {
        //     onBlur: function (e) {
        //         var p = e.target.parentNode.parentNode
        //         if (!(e.relatedTarget && $.contains(p, e.relatedTarget))) {
        //             $(this).parent().children('.note-editor').children('.note-toolbar').css("display", "none");
        //         }
        //     },
        //     onFocus: function (e) {
        //         $(this).parent().children('.note-editor').children('.note-toolbar').css("display", "block");
        //   }
        // }
    });

    $('#question-table').DataTable();

    // add edit funciton
    editQuestion();

    // delete function
    confirmDeleteQuestion();

    // re-bind edit and delet btn
    $('.page-link').click(function(e){
        editQuestion();
        confirmDeleteQuestion();
    });


    $('#add-question').click(function(e){
        e.preventDefault();

        $('#add-question-modal').modal('show');

    });


    $('#add-question-modal').on('hidden.bs.modal', function(){
        let editModal = $('#add-question-modal');
        $(editModal).find('form')[0].reset();
        $(editModal).find('#add-questionLabel').text('New Question');
        $(editModal).find('#question-form-submit').text('Save');
        $(editModal).find('#question-form-submit').attr('action-name', 'add');
        $(editModal).find('#question-form-submit').attr('question-id', '');
        $(editModal).find('#question').summernote('code', '');
        $(editModal).find('#options1').summernote('code', '');
        $(editModal).find('#options1').attr('option-id', '');
        $(editModal).find('#options2').summernote('code', '');
        $(editModal).find('#options2').attr('option-id', '');
        $(editModal).find('#options3').summernote('code', '');
        $(editModal).find('#options3').attr('option-id', '');
        $(editModal).find('#options4').summernote('code', '');
        $(editModal).find('#options4').attr('option-id', '');
    })


    $('#question-form-submit').click(function(e){
        e.preventDefault();
        e.stopPropagation();

        let form = $(this).closest('form');

        let action          = $(form).find('#question-form-submit').attr('action-name');
        let subject_id      = $(form).find('#subject_id').val();
        let level           = $(form).find('#level').val();
        let marks           = $(form).find('#marks').val();
        let question        = $(form).find('#question').val();
        let correctOption   = $(form).find('input[name="options"]:checked').val();
        let option1         = $(form).find('#options1').val();
        let option2         = $(form).find('#options2').val();
        let option3         = $(form).find('#options3').val();
        let option4         = $(form).find('#options4').val();

        if(
            !subject_id || !level || !marks || Number(marks) < 1 || Number(marks) > 10 ||
            !question || !correctOption || !option1 ||
            !option2 || !option3 || !option4
        )
        {
            if(!subject_id)
            {
                $(form).find('#subject_id').addClass('is-invalid');
            }
            if(!level)
            {
                $(form).find('#level').addClass('is-invalid');
            }
            if(!marks || Number(marks) < 1 || Number(marks) > 10)
            {
                $(form).find('#marks').addClass('is-invalid');
                $('.marks-help-text').text('Marks should be between 1 and 10');     
                $('.marks-help-text').css({
                    'color':'red'
                });
                $('.marks-help-text').show();
            }
            if(!question)
            {
                $(form).find('#question').parent().find('.note-frame').css({
                    'border': '1px solid red'
                });
            }
            if(!option1)
            {
                $(form).find('#options1').parent().find('.note-frame').css({
                    'border': '1px solid red'
                });
            }
            if(!option2)
            {
                $(form).find('#options2').parent().find('.note-frame').css({
                    'border': '1px solid red'
                });
            }
            if(!option3)
            {
                $(form).find('#options3').parent().find('.note-frame').css({
                    'border': '1px solid red'
                });
            }
            if(!option4)
            {
                $(form).find('#options4').parent().find('.note-frame').css({
                    'border': '1px solid red'
                });
            }

            if(!correctOption)
            {
                $(form).find('#options-help-text').removeClass('text-muted');
                $(form).find('#options-help-text').css({
                    'font-size': '1.2rem',
                    'color': 'red'
                });
            }


            setTimeout(() => {
                $(form).find('.is-invalid').removeClass('is-invalid');
                $(form).find('#question').parent().find('.note-frame').css({'border': ''});
                $(form).find('#options1').parent().find('.note-frame').css({'border': ''});
                $(form).find('#options2').parent().find('.note-frame').css({'border': ''});
                $(form).find('#options3').parent().find('.note-frame').css({'border': ''});
                $(form).find('#options4').parent().find('.note-frame').css({'border': ''});
                $(form).find('#options-help-text').addClass('text-muted');
                $(form).find('#options-help-text').css({
                    'font-size': '',
                    'color': ''
                });
                $('.marks-help-text').text('');     
                $('.marks-help-text').css({
                    'color':''
                });
                $('.marks-help-text').hide();
            }, 3000);

            return false;
        }



        if(action == 'add')
        {
            let options = JSON.stringify({
                'option_1' : {
                    'value' : option1,
                    'is_correct' : correctOption == 'option-1' ? 1 : 0
                },
                'option_2' : {
                    'value' : option2,
                    'is_correct' : correctOption == 'option-2' ? 1 : 0
                },
                'option_3' : {
                    'value' : option3,
                    'is_correct' : correctOption == 'option-3' ? 1 : 0
                },
                'option_4' : {
                    'value' : option4,
                    'is_correct' : correctOption == 'option-4' ? 1 : 0
                },
            });

            formData = {
                action: 'add',
                subject_id: subject_id,
                level: level,
                marks: marks,
                question: question,
                options: options
            }
        }
        else if(action == 'edit')
        {
            let question_id = $(form).find('#question-form-submit').attr('question-id');
            let options = JSON.stringify({
                'option_1' : {
                    'id' : $(form).find('#options1').attr('option-id'),
                    'value' : option1,
                    'is_correct' : correctOption == 'option-1' ? 1 : 0
                },
                'option_2' : {
                    'id' : $(form).find('#options2').attr('option-id'),
                    'value' : option2,
                    'is_correct' : correctOption == 'option-2' ? 1 : 0
                },
                'option_3' : {
                    'id' : $(form).find('#options3').attr('option-id'),
                    'value' : option3,
                    'is_correct' : correctOption == 'option-3' ? 1 : 0
                },
                'option_4' : {
                    'id' : $(form).find('#options4').attr('option-id'),
                    'value' : option4,
                    'is_correct' : correctOption == 'option-4' ? 1 : 0
                },
            });
            formData = {
                action: 'edit',
                question_id: question_id,
                subject_id: subject_id,
                level: level,
                marks: marks,
                question: question,
                options: options
            }
        }

        // $('#loader').modal('show');
        $.ajax({
            url: '/questions',
            type: 'POST',
            async: false,
            data: formData,
            success: function(response){
                // $('#loader').modal('hide');
                if(response)
                {
                    if(response.status)
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.success(response.msg);
                        setTimeout(() => {
                            location.reload();
                        }, 1500);
                    }
                    else
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.error(response.msg);
                    }
                }
            },
            error: function(error){
                // $('#loader').modal('hide');
                console.log(error);
            }
        });

    });

})