var port = chrome.runtime.connect();
var state = 0 // 1 start  0 stop

port.onMessage.addListener(function(msg) {
  console.log("get message from background js >>>",msg)
  if (msg.type=="query"){
    // check if is already execute
    if (msg.data.context.state==1){
      state = 1
      update(state=1)
      document.querySelector('#host').value= msg.data.config.mail_server
      document.querySelector("#mail_count").value=msg.data.config.count
      document.querySelector("#mail_interval").value=msg.data.config.interval
    }else{
      state = 0
      update(state=0)
    }
  }
});

//每次打开查询是否已经运行
if (port){
  res = port.postMessage({
    "type":"query",
    "data":{
      "key":"state",
    }
  })
}

function update(state){
  if(state == 0){
    document.querySelector('#start').innerText="启动"
    document.querySelector("#start").style.background="#1c87c9"
  }else{
    document.querySelector('#start').innerText="停止"
    document.querySelector("#start").style.background="#c91c1c"
  }
}

function checkInputIsValid(){

  mail_host = document.querySelector('#host').value
  mail_count = document.querySelector('#mail_count').value
  mail_pwd = document.querySelector('#mail_pwd').value
  mail_interval = document.querySelector('#mail_interval').value  
  // mail_protocol = document.querySelector('#mail_interval').value 
  
  var reg = /^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$/;
  if(! reg.test(mail_count)){
    alert("邮箱格式不正确");
  }else {
  if (port){
    port.postMessage({
      "type":"setting",
      "data":{
        "host":mail_host,
        "count":mail_count,
        "pwd":mail_pwd,
        "interval":mail_interval
      }
    })
    alert("提交配置成功!")
  }
}
}

function submitSettings(){
  console.log(">>>>> submit settings",state)
  if (state==1){
    console.log(">>> please stop running first before submit settings！")
    alert("请先停止运行!")
    return
  }else{
    checkInputIsValid()
  }
  
}

function startSubmit(){
  console.log(">>>>> start receiving")
  if (state==0){
    if (port){
      port.postMessage({
        "type":"start",
        "data":{}
      })}
      state = 1
      update(state=1)
    }else{
      state = 0 
      update(state=0)
      if (port){
        port.postMessage({
          "type":"stop",
          "data":{}
        })
      }
      
  }
}
document.querySelector('#submit').addEventListener(
  'click', submitSettings);
document.querySelector('#start').addEventListener(
  'click', startSubmit);