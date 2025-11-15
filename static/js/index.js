 
  const rate = 300
  let time = rate


  const counter_div = document.getElementById("counter")

  counter_div.innerText = `Refresh in ${Math.floor(time/60)}m ${time%60}s`

  setInterval(()=>{time--; if (time<0){time = rate; update()}; counter_div.innerText = `Refresh ${Math.floor(time/60)}m ${time%60}s`; },1000)



 
  const fullURL = window.location.protocol + '//' + window.location.host;

  let chart = document.getElementById("chart");

function createBar(item) {
    const div = document.createElement('div');
    div.style.width = '2.25%';
    div.style.height = '90%';
    div.style.background = `rgb(${item["rgb"][0]}, ${item["rgb"][1]}, ${item["rgb"][2]})`;
    div.style.borderRadius = '0.7vh';
    div.style.marginLeft = '0.5%';
    div.onmouseover = (e) => showTooltip(e.target, `${item["time"]} - ${item["uptime"]*100}%`);
    div.onmouseout = hideTooltip;
    
    return div;
}


async function loadInitial() {

    try {
      fetch(`${fullURL}/api/hourinfo`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
          for (let group in _data){
            chart.appendChild(createElementFromHTML(`<div style="width: 100%; position: relative; margin-bottom: 3vh;"> 
              <div style="margin: 4vh; margin-left: 5%;">${group}</div> 
            </div>`
            ))
            groupel = chart.lastElementChild;
            for (let el in _data[group]){
              groupel.appendChild(createElementFromHTML(`
                <div style="position: relative; width: 92.5%; height: 5vh; margin: 2vh; "> 
                  <div  class="service-grid"> 
                    <div class="service-uptime"><p style="transform: translateY(-50%);" >10%</p></div> 
                    <div class="service-name"><p>ServiceName</p></div> 
                    <div class="uptimebar"></div> 
                  </div>
                  <div style="display: none;" class="shimmer-container"><div class="shimmer-overlay"></div></div>

                </div>`));  
              groupel.lastElementChild.children[0].children[0].lastElementChild.innerText = `${_data[group][el][0]["uptime"]}%`
              groupel.lastElementChild.children[0].children[1].lastElementChild.innerText = el
              groupel.lastElementChild.children[0].children[0].style.background = `rgb(${_data[group][el][0]["rgb"][0]},${_data[group][el][0]["rgb"][1]},${_data[group][el][0]["rgb"][2]})`
              let bar = groupel.lastElementChild.children[0].lastElementChild;
              for (let i = _data[group][el].length - 1; i > 0; i--){
                  bar.appendChild(createBar(_data[group][el][i]));
              }
            //  _data[el].forEach(item => chart.lastChild.appendChild(createBar(item)));

            }
          }
        })
        
        
    } catch (err) {
        console.error('Initial load failed:', err);
    }
}

async function update() {

    try {
      fetch(`${fullURL}/api/updhourinfo`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
          
          let k = 0;
          for (let group in _data){
            let j=1;
            for (let el in _data[group]){
              chart.children[k].children[j].children[0].style.display = "none";
              chart.children[k].children[j].children[1].style.display = "block";
              chart.children[k].children[j].children[0].children[0].lastElementChild.innerText = `${_data[group][el][0]["uptime"]}%`
              chart.children[k].children[j].children[0].children[1].lastElementChild.innerText = el
              chart.children[k].children[j].children[0].children[0].style.background = `rgb(${_data[group][el][0]["rgb"][0]},${_data[group][el][0]["rgb"][1]},${_data[group][el][0]["rgb"][2]})`
              let bar = chart.children[k].children[j].children[0].lastElementChild;
              for (let i = 0; i < _data[group][el].length-1; i++){
                  bar.children[0].remove()
              }
              for (let i=_data[group][el].length-1; i>0;i--){
                  bar.appendChild(createBar(_data[group][el][i]));
              }
              let c_j = j
              let c_k = k
              setTimeout( ()=>{
                
                chart.children[c_k].children[c_j].children[0].style.display = "grid";
                chart.children[c_k].children[c_j].children[1].style.display = "none";
              },250)
              j++;
            }
            k++;
          }
        })
        
        
    } catch (err) {
        console.error('Initial load failed:', err);
    }
}

loadInitial();

function createElementFromHTML(htmlString) {
  var div = document.createElement('div');
  div.innerHTML = htmlString.trim();
  return div.firstChild;
}




 
function showTooltip(element, text) {
  var tooltip = document.createElement('div');
  tooltip.innerHTML = text;
  tooltip.classList.add('js-tooltiptext');
  document.body.appendChild(tooltip);

  element.onmousemove = function(e) {
    tooltip.style.top = (e.pageY + 10) + 'px';
    tooltip.style.left = (e.pageX) + 'px';
  };

  requestAnimationFrame(() => {
    tooltip.classList.add('visible');
  });
}

function hideTooltip() {
  var tooltips = document.querySelectorAll('.js-tooltiptext');
  tooltips.forEach(function(tooltip) {
    tooltip.classList.remove('visible');
    setTimeout(() => tooltip.remove(), 250);
  });
}



