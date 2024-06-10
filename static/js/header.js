$(function(){
    $('#navbarNav .link-item').hover(function(){
        $(this).css({
            // "background-color":"#dbd8d8",
            "background-color":"#0d94ef",
            "border-radius": "7px"
        });
        $(this).find('a').css({
            "color":"white"
        });
    }, function(){
        $(this).css({
            "background-color":"",
            "border-radius": ""
        });
        $(this).find('a').css({
            "color":""
        });
    });
});