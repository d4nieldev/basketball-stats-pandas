$(document).ready(function(){
    $("table thead tr:last-child").remove();

    $("table tbody tr").each(function(){
        const id = $(this).find("th").text()
        const link = "https://www.basketball-reference.com/players/"+ id[0] +"/"+ id +".html"
        $(this).find("td:nth-child(2)").html("<a href='"+link+"'>"+$(this).find('td:nth-child(2)').text()+"</a>")
    })
    $("table tbody tr th").remove();
    $("table thead tr th:first-child").remove();

})