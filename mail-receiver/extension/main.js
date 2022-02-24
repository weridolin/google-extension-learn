// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var port = null;
var numTabs = 0
var getKeys = function(obj){
   var keys = [];
   for(var key in obj){
      keys.push(key);
   }
   return keys;
}

function killNativeApp(appName){
  console.log("kill native application")
}


function appendMessage(text) {
  document.getElementById('response').innerHTML += "<p>" + text + "</p>";
}


function updateUiState() {
  if (port) {
    document.getElementById('connect-button').style.display = 'none';
    document.getElementById('input-text').style.display = 'block';
    document.getElementById('send-message-button').style.display = 'block';
  } else {
    document.getElementById('connect-button').style.display = 'block';
    document.getElementById('input-text').style.display = 'none';
    document.getElementById('send-message-button').style.display = 'none';
  }
}

function sendNativeMessage(message) {
  // message = {"text": message};
  // console.log("send message >>>",message)
  port.postMessage(message);
  // appendMessage("Sent message: <b>" + JSON.stringify(message) + "</b>");
}

function onNativeMessage(message) {
  // appendMessage("Received message: <b>" + JSON.stringify(message) + "</b>");

  console.log("get message",message)
}

function onDisconnected() {
  // appendMessage("Failed to connect: " + chrome.runtime.lastError.message);
  port = null;;
  // killNativeApp()
  console.log(">>>> disconnect from native app")
}

function connect() {
  var hostName = "mail.helper";
  console.log(">>",hostName)
  // appendMessage("Connecting to native messaging host <b>" + hostName + "</b>")
  port = chrome.runtime.connectNative(hostName); //回去查找注册表中的  com.google.chrome.example.echo项目
  port.onMessage.addListener(onNativeMessage);
  port.onDisconnect.addListener(onDisconnected);
  // chrome.runtime.onStartup.addListener(
  //   function (){
  //     console.log(">>>>start up")
  //   }
  // )
  sendNativeMessage({
    "type":"ping",
    "data":{}
  })
  // sendNativeMessage("close")
  // updateUiState();
}

function handleMessage(msg){
  try {
    msg = JSON.parse(msg)
    if (port){
      console.log(">>> send message to native app",msg)
      sendNativeMessage(msg)
    }else{
      console.log(">>> cannot connect to native app...")
    }
  } catch (error) {
    console.log(">>> get a invalid format msg",msg,error)
  }
}
killNativeApp("c4")
connect()

chrome.runtime.onConnect.addListener(function(port) {
  // console.assert(port.name === "knockknock");
  port.onMessage.addListener(function(msg) {
    console.log("get message from popup >>> ",msg)
    sendNativeMessage(msg)
  });
  
});