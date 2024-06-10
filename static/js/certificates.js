$(function(){

    $('.generate-certificate').click(function(e){
        e.preventDefault();

        let url = $(this).attr('href');
        let practice_id = $(this).attr('practice-id');

        if(url && practice_id)
        {
            $.ajax({
                url: url,
                type: 'POST',
                // responseType: 'arraybuffer',
                data: {
                    action: 'get',
                    practice_id: practice_id
                },
                success: function(response){
                    if(response && response.status)
                    {
                        // console.log(response.data.image_url);
                        // let pdfData = response;
                        // let blob    = new Blob([pdfData], { type: 'image/jpeg' });
                        // let blobURL = URL.createObjectURL(blob);
                        // window.open(response.data.image_url);

                        var link = document.createElement('a');
                        link.href = response.data.image_url;
                        link.download = response.data.image_url;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);

                        alertify.set('notifier','position', 'top-right');
                        alertify.success(response.msg);
                    }
                    else if(response && !response.status)
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.warning(response.msg);
                    }
                    else
                    {
                        alertify.set('notifier','position', 'top-right');
                        alertify.error("Something went wrong");
                    }
                },
                error: function(error){
                    console.log(error);
                }
            })
        }
    });

});