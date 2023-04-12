
    var times = document.getElementsByClassName("time");
    for (let i = 0 ; i < times.length;++i) 
    {
        let time = times[i];
        let oringinalTime = time.innerHTML;
        time.innerHTML = new Date(oringinalTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
