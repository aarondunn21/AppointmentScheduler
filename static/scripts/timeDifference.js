
    var times = document.getElementsByClassName("timeDifference");
    for (let i = 0 ; i < times.length;++i) 
    {
        let time = times[i];
        let oringinalTime = Date.parse(time.innerHTML);

        let totalSeconds = Math.ceil((oringinalTime - Date.now()) / 1000)

        var seconds = parseInt(totalSeconds, 10);

        var days = Math.floor(seconds / (3600*24));
        seconds  -= days*3600*24;
        var hrs   = Math.floor(seconds / 3600);
        seconds  -= hrs*3600;
        var mnts = Math.floor(seconds / 60);
        seconds  -= mnts*60;

        if(totalSeconds < 0){
            time.innerHTML = "Now";
        }
        else{
            time.innerHTML = `${days} days and ${hrs} hours`;
        }
        //calc days until future appointment
    }
    
