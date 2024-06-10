const updateTestStatics = (attend, total) => {
    let toast       = $('#test-statics');
    let progressBar = $(toast).find('.progress-bar');

    $(progressBar).css({
        'width': Math.ceil((attend*100)/total) +'%'
    });
    $(toast).find('#attended-questions').text(attend);
    $(toast).find('#total-questions').text(total);
}

const addTimeUpEffect = () =>  {
    $('.list-group-item').each(function(e){
        $(this).addClass('disabled');
        $(this).css({
            'opacity': '40%'
        });
    });
    $('#mcq-form').find('input').attr('disabled', true);
    $('#test-statics').find('.toast-header').removeClass('bg-primary').addClass('bg-danger');
}


const updateTimer = (duration) => {
    function updateCountdown() {
        const countdownElement = document.getElementById("coutdown-timer");
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        countdownElement.textContent = `${minutes}m ${seconds}s`;
    
        // Decrement the duration
        duration--;
    
        // Check if the countdown has completed
        if (duration < (duration-10)) {
            addTimeUpEffect();
            countdownElement.textContent = "Time's up!";
            clearInterval(intervalId);
        }
    }
    
    // Call the updateCountdown function every second
    const intervalId = setInterval(updateCountdown, 1000);
}


const submitPractic = (testCookie) => {
    $.ajax({
        url     : '/practice',
        type    : 'POST',
        async   : false,
        data    : {
            action  : 'save-practice',
            data    : testCookie
        },
        success : function(response){
            if(response)
            {
                if(response.status)
                {
                    alertify.set('notifier','position', 'top-right');
                    alertify.success(response.msg);
                    setTimeout(() => {
                        window.history.go(-1);
                    }, 1500);
                }
                else
                {
                    alertify.set('notifier','position', 'top-right');
                    alertify.error(response.msg);
                }
            }
        },
        error   : function(error){
            console.log(error);
        }
    });
};


$(function(){
    var testCookie      = {};
    var totalQuestion   = 0;
    var attendQuestions = 0;
    var testDuration    = Number($('#mcq-form').attr('time'));
    var testID          = Number($('#mcq-form').attr('test-id'));
    var subjectID       = Number($('#mcq-form').attr('subject-id'));
    var testCookie = {
                        'statics' : {
                                        'start_time'    : Math.floor(Date.now() / 1000),
                                        'end_time'      : false,
                                        'test_id'       : testID,
                                        'subject_id'    : subjectID,
                                    },
                        'qna'     : {}
                    }

    var visibleChangeCount = 0;


    // init form input values
    $('.question-card').each(function(e){
        totalQuestion++;

        let question_id = $(this).attr('question-id');

        testCookie['qna'][question_id] = {
            'question_id'   : question_id,
            'option_id'     : false
        };
    });
    $.cookie('test-form-values', JSON.stringify(testCookie), { expires: 1 });

    updateTestStatics(attendQuestions, totalQuestion);
    updateTimer(testDuration*60);
    const testStatics = bootstrap.Toast.getOrCreateInstance($('#test-statics'));
    testStatics.show();



    // cut copy paste
    document.addEventListener('selectstart', (event) => {
        event.preventDefault();
        return false;
    });
    document.addEventListener('cut',  (event) => {
        event.preventDefault();
        return false;
    });
    document.addEventListener('copy',  (event) => {
        event.preventDefault();
        return false;
    });
    document.addEventListener('paste',  (event) => {
        event.preventDefault();
        return false;
    });
    document.addEventListener('drag',  (event) => {
        event.preventDefault();
        return false;
    });
    document.addEventListener('drop',  (event) => {
        event.preventDefault();
        return false;
    });
    document.oncontextmenu = new Function('return false');

    document.addEventListener('visibilitychange', function(){
        visibleChangeCount++;
        let testCookie = JSON.parse($.cookie('test-form-values'));

//        switch(visibleChangeCount)
//        {
//            case 1 : lsjdflsjd
//        }

    });



    $('.list-group-item').click(function(e){
        e.preventDefault();

        let questionCard = $(this).closest('.question-card');
        let question_id  = $(questionCard).attr('question-id');


        $(this).find('input').prop("checked", true);
        let testCookie = JSON.parse($.cookie('test-form-values'));

        testCookie['qna'][question_id].option_id = $(questionCard).find("input[name='option-group-"+ question_id +"']:checked").val();

        attendQuestions = 0;
        for(let [key, value] of Object.entries(testCookie['qna']))
        {
            if(value.option_id !== false)
                attendQuestions++;
        }

        updateTestStatics(attendQuestions, totalQuestion);

        $.cookie('test-form-values', JSON.stringify(testCookie), { expires: 1 });
        
    });

    $('a').click(function(e){
        e.preventDefault();
        let href = $(this).attr('href');
        alertify.confirm('Are you sure, You wand to leave this practice?')
                .set('onok', function(closeEvent){
                    if(closeEvent.cancel == false)
                    {
                        location.href = href;
                    }
                })
                .setHeader('')
                .setting({
                    'closable': false,
                    'transition':'zoom',
                    'labels': {
                        ok:'Submit',
                        cancel:'Cancel'
                    }
                }).show();
    });

    $('#submit-test').click(function(e){
        e.preventDefault();

        let testCookie = JSON.parse($.cookie('test-form-values'));
        testCookie['statics']['end_time'] = Math.floor(Date.now() / 1000);
        
        alertify.confirm('Are you sure?')
                .set('onok', function(closeEvent){
                    if(closeEvent.cancel == false)
                    {
                        submitPractic(JSON.stringify(testCookie));
                    }
                })
                .setHeader('')
                .setting({
                    'closable': false,
                    'transition':'zoom',
                    'labels': {
                        ok:'Submit',
                        cancel:'Cancel'
                    }
                }).show();

    });
});