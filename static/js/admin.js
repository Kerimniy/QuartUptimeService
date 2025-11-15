const protocol = window.location.protocol;
  const host = window.location.host;
  const fullURL = window.location.protocol + '//' + window.location.host;
  const finput = document.getElementById("finput")
  const chart = document.getElementById("monitorchart")
  const createGrid = document.getElementById("createGrid")
  const finputbutton = document.getElementById("finputbutton")
  const serversettings = document.getElementById("serversettings")
  const h1title = document.getElementById("h1title")

  function chengeServerSettings(){
    let res = {"title": serversettings.children[5].lastElementChild.value,"md": serversettings.children[6].lastElementChild.value}
    if (finput.files.length>0){
      
      let fdata = new FormData()
      fdata.append("file",finput.files[0])

      fetch(`${fullURL}/api/setimage`, {method: 'POST', body: fdata,})
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.text();
        })
        .then(_data =>{
          }
        )
    }
    fetch(`${fullURL}/api/changeserverinfo`, {method: 'POST',headers: {'Content-Type': 'application/json'},  body: JSON.stringify(res),})
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.text();
        })
        .then(_data =>{
         if (_data=="200"){
          document.title=`${res["title"]} Admin Panel`
          h1title.innerText = `${res["title"]} Admin Panel`
         }
        }
    )


  }

  function imitatefinput(){
    finput.click()
  }

  function setfilename(){
    finputbutton.innerText = finput.files[0].name
  }

  async function loadInitial() {

    try {
      fetch(`${fullURL}/api/getmonitors`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
            let i=0
          for (let el in _data){
            
            let monitor = createElementFromHTML(`
            
            <div class="monitorsettingsgrid" data-idx=${_data[el]["index"]}>
                <div style="text-align: center;">Url</div>
                <div style="text-align: center;">Name</div>
                <div style="text-align: center;">Group</div>
                <div style="text-align: center;">Interval</div>
                <div style="text-align: center;">Timeout</div>
                <div style="text-align: center;">Allow Redirect</div>
                <div></div>
                <div></div>
                
                <div><textarea class="textinput">${_data[el]["url"]}</textarea></div>
                <div><textarea class="textinput">${el}</textarea></div>
                <div><textarea class="textinput">${_data[el]["group"]}</textarea></div>
                <div><input class="textinput" style="min-height: 55%; margin-right: 2vw;" type="number" value=${_data[el]["interval"]}></div>
                <div><input class="textinput" style="min-height: 55%;" type="number" value=${_data[el]["timeout"]}></div>

                <div><label style="cursor: pointer;position: relative; top: 25%; left: 0%; transform: translate(-50%,-50%);" for="toggle${i}" >
                    <input type="checkbox" name="toggle" id="toggle${i}" class="checkbox">
                        <div class="togglebuttonBg">
                            <div class="togglebuttonSl"></div>
                        </div>
                    </label>   
                </div>

                <div><button class="buttonSettings" onclick="show('changeMonitor', ${i+1});">Change</button></div>
                <div><button class="buttonSettings" onclick="show('deleteMonitor', ${i+1});">Delete</button></div>


            </div>
            
            `)

            chart.appendChild(monitor)

            document.getElementById(`toggle${i}`).checked = _data[el]["allow_redirect"]

            i++;
          }
        })
        
            
        } catch (err) {
            console.error('Initial load failed:', err);
        }

    }

    function createMonitor(i){
        let res = { 
        "url": createGrid.children[7].lastElementChild.value,
        "name": createGrid.children[8].lastElementChild.value,
        "group": createGrid.children[9].lastElementChild.value,
        "interval": createGrid.children[10].lastElementChild.value, 
        "timeout": createGrid.children[11].lastElementChild.value,
        "redirect": createGrid.children[12].lastElementChild.firstElementChild.checked 
        } 

        fetch(`${fullURL}/api/createMonitor`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(res),})
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
         chart.innerHTML=`<h2 style="margin-left: 10vw;">Monitor Settings</h2>`;

          let i=0
          for (let el in _data){
            
            let monitor = createElementFromHTML(`
            
            <div class="monitorsettingsgrid" data-idx=${_data[el]["index"]}>
                <div style="text-align: center;">Url</div>
                <div style="text-align: center;">Name</div>
                <div style="text-align: center;">Group</div>
                <div style="text-align: center;">Interval</div>
                <div style="text-align: center;">Timeout</div>
                <div style="text-align: center;">Allow Redirect</div>
                <div></div>
                <div></div>
                
                <div><textarea class="textinput">${_data[el]["url"]}</textarea></div>
                <div><textarea class="textinput">${el}</textarea></div>
                <div><textarea class="textinput">${_data[el]["group"]}</textarea></div>
                <div><input class="textinput" style="min-height: 55%; margin-right: 2vw;" type="number" value=${_data[el]["interval"]}></div>
                <div><input class="textinput" style="min-height: 55%;" type="number" value=${_data[el]["timeout"]}></div>

                <div><label style="cursor: pointer;position: relative; top: 25%; left: 0%; transform: translate(-50%,-50%);" for="toggle${i}" >
                    <input type="checkbox" name="toggle" id="toggle${i}" class="checkbox">
                        <div class="togglebuttonBg">
                            <div class="togglebuttonSl"></div>
                        </div>
                    </label>   
                </div>

                <div><button class="buttonSettings" onclick="show('changeMonitor', ${i+1});">Change</button></div>
                <div><button class="buttonSettings" onclick="show('deleteMonitor', ${i+1});">Delete</button></div>


            </div>
            
            `)
            chart.appendChild(monitor)

            document.getElementById(`toggle${i}`).checked = _data[el]["allow_redirect"]

            i++;
          }
        })
      }

    function changeMonitor(i){
        let res = { 
        "idx": chart.children[i].dataset.idx, 
        "url": chart.children[i].children[8].lastElementChild.value,
        "name": chart.children[i].children[9].lastElementChild.value,
        "group": chart.children[i].children[10].lastElementChild.value,
        "interval": chart.children[i].children[11].lastElementChild.value, 
        "timeout": chart.children[i].children[12].lastElementChild.value,
        "redirect": chart.children[i].children[13].lastElementChild.firstElementChild.checked 
        } 

        fetch(`${fullURL}/api/changemonitor`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(res),})
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
         chart.innerHTML=`<h2 style="margin-left: 10vw;">Monitor Settings</h2>`;

          let i=0
          for (let el in _data){
            
            let monitor = createElementFromHTML(`
            
            <div class="monitorsettingsgrid" data-idx=${_data[el]["index"]}>
                <div style="text-align: center;">Url</div>
                <div style="text-align: center;">Name</div>
                <div style="text-align: center;">Group</div>
                <div style="text-align: center;">Interval</div>
                <div style="text-align: center;">Timeout</div>
                <div style="text-align: center;">Allow Redirect</div>
                <div></div>
                <div></div>
                
                <div><textarea class="textinput">${_data[el]["url"]}</textarea></div>
                <div><textarea class="textinput">${el}</textarea></div>
                <div><textarea class="textinput">${_data[el]["group"]}</textarea></div>
                <div><input class="textinput" style="min-height: 55%; margin-right: 2vw;" type="number" value=${_data[el]["interval"]}></div>
                <div><input class="textinput" style="min-height: 55%;" type="number" value=${_data[el]["timeout"]}></div>

                <div><label style="cursor: pointer;position: relative; top: 25%; left: 0%; transform: translate(-50%,-50%);" for="toggle${i}" >
                    <input type="checkbox" name="toggle" id="toggle${i}" class="checkbox">
                        <div class="togglebuttonBg">
                            <div class="togglebuttonSl"></div>
                        </div>
                    </label>   
                </div>

                <div><button class="buttonSettings" onclick="show('changeMonitor', ${i+1});">Change</button></div>
                <div><button class="buttonSettings" onclick="show('deleteMonitor', ${i+1});">Delete</button></div>


            </div>
            
            `)
            chart.appendChild(monitor)

            document.getElementById(`toggle${i}`).checked = _data[el]["allow_redirect"]

            i++;
          }
        })
        
    }

    function deleteMonitor(i){
        res = {"idx": chart.children[i].dataset.idx}
        window.location
        fetch(`${fullURL}/api/deletemonitor`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(res),})
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(_data =>{
         chart.innerHTML=`<h2 style="margin-left: 10vw;">Monitor Settings</h2>`;

          let i=0
          for (let el in _data){
            
            let monitor = createElementFromHTML(`
            
            <div class="monitorsettingsgrid" data-idx=${_data[el]["index"]}>
                <div style="text-align: center;">Url</div>
                <div style="text-align: center;">Name</div>
                <div style="text-align: center;">Group</div>
                <div style="text-align: center;">Interval</div>
                <div style="text-align: center;">Timeout</div>
                <div style="text-align: center;">Allow Redirect</div>
                <div></div>
                <div></div>
                
                <div><textarea class="textinput">${_data[el]["url"]}</textarea></div>
                <div><textarea class="textinput">${el}</textarea></div>
                <div><textarea class="textinput">${_data[el]["group"]}</textarea></div>
                <div><input class="textinput" style="min-height: 55%; margin-right: 2vw;" type="number" value=${_data[el]["interval"]}></div>
                <div><input class="textinput" style="min-height: 55%;" type="number" value=${_data[el]["timeout"]}></div>

                <div><label style="cursor: pointer;position: relative; top: 25%; left: 0%; transform: translate(-50%,-50%);" for="toggle${i}" >
                    <input type="checkbox" name="toggle" id="toggle${i}" class="checkbox">
                        <div class="togglebuttonBg">
                            <div class="togglebuttonSl"></div>
                        </div>
                    </label>   
                </div>

                <div><button class="buttonSettings" onclick="show('changeMonitor', ${i+1});">Change</button></div>
                <div><button class="buttonSettings" onclick="show('deleteMonitor', ${i+1});">Delete</button></div>


            </div>
            
            `)
            chart.appendChild(monitor)

            document.getElementById(`toggle${i}`).checked = _data[el]["allow_redirect"]

            i++;
          }
        })
        
    }

    function show(f,i){
      let div = createElementFromHTML(`<div style="position: fixed; inset: 0; width: 100vw; height: 100vh;">

  <div style="position: absolute; width: 30vw; height: 15vh; padding: 4vh 2vw; top: 50%; left: 50%; transform: translate(-50%, -50%); border-radius: 2vh; z-index: 50; background-color: rgb(61, 61, 61); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2vh;">
    <p style="margin: 0; font-size: 2vh; color: white;">Are you sure?</p>
    <div style="display: flex; margin-top: 2vh; justify-content: center; gap: 5vw; width: 100%;">
      <button class="buttonSettings" style="height: 3em; width: 40%; font-size: 1.5vh; border-radius: 1vh;" onclick="${f}(${i}); hide(this)">Yes</button>
      <button class="buttonSettings" style="height: 3em; width: 40%; font-size: 1.5vh; border-radius: 1vh;" onclick="hide(this)">No</button>
    </div>
  </div>

  <div style="position: fixed; inset: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.7); z-index: 0;"></div>

</div>`)

      div.style.opacity = 0
      div.style.transition = 'opacity 0.15s ease'
      document.body.appendChild(div)
      
      setTimeout(function() {document.body.lastElementChild.style.opacity = 1;}, 50)
      
    }

    function hide(_this){
      let seconds = 0.15; let el = _this.parentElement.parentElement.parentElement;  el.style.transition = 'opacity '+seconds+'s ease'; el.style.opacity = 0; setTimeout(function() {el.remove();}, seconds*1000);
    }

    function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
    }