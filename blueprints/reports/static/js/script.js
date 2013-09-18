$('form').submit(function(){
    $('body').addClass("loading");
});
function filter(phrase, table){
    var words = phrase.toLowerCase().split(" ");
    var ele;
    for (var r = 1; r < table.rows.length; r++){
        ele = table.rows[r].innerHTML.replace(/<[^>]+>/g,"");
        var displayStyle = 'none';
        for (var i = 0; i < words.length; i++) {
            if (ele.toLowerCase().indexOf(words[i])>=0){
                displayStyle = '';
            }else {
                displayStyle = 'none';
                break;
            }
        }
        table.rows[r].style.display = displayStyle;
    }
}
$(function() {
    $('#filter_report').keyup(function(){
        var phrase = $(this).val();
        $('.result_table').each(function(){
            filter(phrase, $(this).get(0));
        });
        $('#result_table').each(function(){
            filter(phrase, $(this).get(0));
        });
    });
});