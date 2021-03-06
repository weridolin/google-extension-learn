
var native_port = null; //communicate with native app
var popup_port = null //communicate with popup menu
function killNativeApp(appName){
  console.log("kill native application")
}

function sendNativeMessage(message) {
  if (message.type!="ping"){
    console.log("send message to native app",message)
  }
  native_port.postMessage(message);
}

function onNativeMessage(message) {
  try {
    _ = JSON.stringify(message)
    console.log('get message from native app',message)
    if (message.type=="query"){
      console.log("send message to popup")
      popup_port.postMessage(message)
    }
  } catch (error) {
    console.log("get a invalid format message",message)
  }
}

function onDisconnected() {
  // appendMessage("Failed to connect: " + chrome.runtime.lastError.message);
  native_port = null;;
  // killNativeApp()
  console.log(">>> disconnect from native app")
}

function connect() {
  var hostName = "mail.helper";
  native_port = chrome.runtime.connectNative(hostName); //回去查找注册表中的 mail.helper项目
  native_port.onMessage.addListener(onNativeMessage);
  native_port.onDisconnect.addListener(onDisconnected);

  // start ping native app per 1s
  setInterval(function() {
    // console.log(">>>> send ping")
    sendNativeMessage({
      "type":"ping",
      "data":{}
    })
  }, 1000);
 
}

function handleMessage(msg){
  try {
    msg = JSON.parse(msg)
    if (port){
      console.log(">>> send message to native app",msg)
      return sendNativeMessage(msg)
    }else{
      console.log(">>> cannot connect to native app...")
    }
  } catch (error) {
    console.log(">>> get a invalid format msg",msg,error)
  }
}

connect()

chrome.runtime.onConnect.addListener(function(port) {
  // console.assert(port.name === "knockknock");
  popup_port = port
  // console.log('a new connect',port.name)
  popup_port.onMessage.addListener(function(msg) {
    console.log("get message from popup >>> ",msg)
    sendNativeMessage(msg)
  });
  
});

// chrome.processes.onCreated.addListener(
//   function(){
//     console.log(">>> google browser is created")
//   }
// )

// chrome.processes.onExited.addListener(
//   function(){
//     console.log(">>> google browser is exit")
//   }
// )

