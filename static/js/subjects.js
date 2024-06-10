let deleteSubject = (subjectId) => {
    
    $.ajax({
        url: '/subjects',
        type: 'POST',
        async: false,
        // headers: {
        //     'X-CSRFToken': csrf_token.value
        // },
        data: {
            action: 'delete',
            subject_id: subjectId
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

                if(response.data.redirect)
                {
                    setTimeout(() => {
                        window.location.href = response.data.redirect;
                    }, 3000);
                }
            }
        },
        error: function(error){
            console.log(error);
        }
    });
}



$(function(){

    $('#add-subject').click(function(e){
        e.preventDefault();

        $('#add-subject-modal').modal('show');
    });


    $('#subject-form-submit').click(function(e){
        e.preventDefault();

        // let form        = $(this).closest('form');
        let form        = document.getElementById('subject-form');
        let csrf_token  = $(form).find('#csrf_token').val();
        let formData    = new FormData(form);
        
        formData.append('action', 'add');

        $('#loader').modal('show');
        $.ajax({
            url: '/subjects',
            type: 'POST',
            async: false,
            data: formData,
            cache: false,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            // headers: {
            //     'X-CSRFToken': csrf_token
            // },
            success: function(response){
                $('#loader').modal('hide');
                if(response)
                {
                    $('#add-subject-modal').modal('hide');
                    if(!response.status)
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.error(response.msg);
                    }
                    else
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.success(response.msg);

                    }

                    if(response.data.redirect)
                    {
                        setTimeout(() => {
                            window.location.href = response.data.redirect;
                        }, 3000);
                    }
                }
            },
            error: function(error){
                $('#loader').modal('hide');
                console.log(error);
            }
        });
    });


    $('.delete-subject').click(function(e){
        e.preventDefault();

        let subjectCard = $(this).closest('.language-option');
        let subjectName = $(subjectCard).find('.subject-name').text().trim();
        let subjectId   = Number($(subjectCard).attr('subject-id'));

        alertify.confirm('Are you sure, you want to delete this '+ subjectName +' Subject?')
                // .set('onok', deleteSubject(subjectId))
                .set('onok', function(closeEvent){
                    if(closeEvent.cancel == false)
                    {
                        deleteSubject(subjectId)
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

    $('.edit-subject').click(function(e){
        e.preventDefault();
        let subjectCard     = $(this).closest('.language-option');
        let subjectImgSrc   = $(subjectCard).find('.subject-logo').attr('src');
        let subjectName     = $(subjectCard).find('.subject-name').text().trim();
        let subjectId       = Number($(subjectCard).attr('subject-id'));

        let editModal = $('#edit-subject-modal');
        
        $(editModal).find('#name').val(subjectName);
        $(editModal).find('#subject-id').val(subjectId);
        $(editModal).find('.subject-img').attr('src', subjectImgSrc);

        $('#edit-subject-modal').modal('show');
    });


    $('#subject-edit-form-submit').click(function(e){
        e.preventDefault();
        
        let subjectCard = $(this).closest('.language-option');
        let subjectName = $(subjectCard).find('.subject-name').text().trim();
        let subjectId   = Number($(subjectCard).attr('subject-id'));

        let form        = document.getElementById('subject-edit-form');
        let formData    = new FormData(form);

        formData.append('action', 'edit');

        $('#loader').modal('show');
        $.ajax({
            url: '/subjects',
            type: 'POST',
            async: false,
            data: formData,
            cache: false,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            // headers: {
            //     'X-CSRFToken': csrf_token.value
            // },
            success: function(response){
                $('#loader').modal('hide');
                if(response)
                {
                    $('#edit-subject-modal').modal('hide');
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

                    if(response.data.redirect)
                    {
                        setTimeout(() => {
                            window.location.href = response.data.redirect;
                        }, 3000);
                    }
                }
            },
            error: function(error){
                $('#loader').modal('hide');
                console.log(error);
            }
        });
    });

    

});