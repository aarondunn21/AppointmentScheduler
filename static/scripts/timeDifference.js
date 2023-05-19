
    var times = document.getElementsByClassName("timeDifference");
    for (let i = 0 ; i < times.length;++i) 
    {
        let time = times[i];
        let oringinalTime = Date.parse(time.innerHTML);
        let nowTime = Date.now();
        time.innerHTML = Math.ceil((oringinalTime - Date.now()) / (1000 * 3600 * 24)) 
        //calc days until future appointment
    }
    
