(async function () {
  var topic = 'webeye01';

  class MQTT {
    async init(topic) {
      var self = this;
      this.topic = topic;
      this.cb = function (msg) { console.log("recv:", msg); }
      this.mqtt = new webduino.module.mqttClient();
      await this.mqtt.connect();
      await this.mqtt.onMessage(topic + '/state', async (msg) => {
        self.cb(msg);
      });
      return this;
    }
    onMsg(cb) {
      this.cb = cb;
    }
    pub(name, msg) {
      this.mqtt.send({ topic: this.topic + name, message: msg });
    }
  }

  class Btn {
    constructor(eleClass) {
      this.cb = function () {}
      this.btn = document.getElementsByClassName(eleClass)[0];
      var self = this;
      this.btn.addEventListener("click", function (e) {
        self.cb(self.refObj,e);
      });
    }
    onClick(self,cb) {
      this.cb = cb;
      this.refObj = self;
      return this;
    }

    color(c){
      this.btn.style.color = c;
    }
  }

  class UI {
    constructor(devId) {
      var self = this;
      this.devId = devId;
      this.display = document.getElementsByClassName('btn-show')[0];
      this.createButton();
      this.createFolderModel();
      this.createCronModel();
      this.info = {}
    }

    createButton(){
      this.btnCam = new Btn('btn-cam').onClick(this,this.btn_cam);
      this.btnCron = new Btn('btn-cron').onClick(this,this.btn_cron);
      this.btnFolder = new Btn('btn-folder').onClick(this,this.btn_folder);
    }


    createCronModel(){
      var self = this;
      self.cron_modal = document.getElementById("cron-modal");

      document.getElementById("cron-close")
        .addEventListener("click", function (e) {
          self.cron_modal.close();
        });      
    }


    createFolderModel(){
      var self = this;
      self.folder_modal = document.getElementById("folder-modal");
      document.getElementById("folderURL")
        .addEventListener("focus", function (e) {
          folderURL.value = '';
        });
      document.getElementById("folder-set")
        .addEventListener("click", function (e) {
          var data = folderURL.value.split('folders/');
          var folderId = data[1];
          self.show("資料夾更新中...");
          self.mqtt.pub('/folderId', folderId);
          folderURL.style['display']='none'
          self.folder_modal.close();
        });
      document.getElementById("folder-open")
        .addEventListener("click", function (e) {
          window.open(folderURL.value,'_blank');
        });
      document.getElementById("folder-close")
        .addEventListener("click", function (e) {
          folderURL.style['display']='none'
          self.folder_modal.close();
        });
    }

    async connect() {
      this.mqtt = await new MQTT().init(this.devId);
      this.mqttpub_info("");
      var self = this;
      this.mqtt.onMsg(function (msg) {
        var cmd = 'mqttsub_';
        var data = '';
        if (msg.indexOf(' ') > 0) {
          cmd += msg.substring(0, msg.indexOf(' '));
          data = msg.substring(msg.indexOf(' ') + 1);
        } else {
          cmd += msg;
        }
        self[cmd](data);
      });
    }

    setInfo(info){
      info = info.replaceAll('True','true');
      info = info.replaceAll('False','false');
      info = info.replaceAll("'",'"');
      this.info = JSON.parse(info);
      folderURL.value = "https://drive.google.com/drive/u/0/folders/"+this.info['folderId'];
      this.btnCam.color('white');

      cronEnable.checked = info['enableCron'];
      this.btnCron.color( cronEnable.checked ? 'green':'red');      

      this.btnFolder.color('white');
    }

    getInfo(){
      return this.info;
    }

    btn_cam(self,e){
      self.mqtt.pub('/snapshot', "");
    }

    btn_cron(self,e){
      self.cron_modal.showModal();
    }

    btn_folder(self,e){
      self.folder_modal.showModal();
      folderURL.style['display']=''
    }

    mqttpub_info(data){
      this.mqtt.pub('/info', data);
    }

    mqttpub_sendTime(data){
      this.mqtt.pub('/sendTime', data);
    }

    mqttpub_enableCron(data){
      this.mqtt.pub('/enableCron', data);
    }

    mqttpub_scriptURL(data){
      this.mqtt.pub('/scriptURL', data);
    }

    mqttpub_reboot(data){
      this.mqtt.pub('/reboot', data);
    }

    mqttsub_reboot(data) {
      this.show("WebEye 重新開機...");
    }

    mqttsub_ready(info) {
      this.setInfo(info);
      this.show("WebEye Pro 上線");
    }

    mqttsub_info(info) {
      this.setInfo(info);
      this.show("更新 WebEye Pro 設定資訊");
      console.log("info:",this.getInfo());
    }

    mqttsub_setOK(info) {
      var self = this;
      if(info=='folderId'){
        self.show("資料夾更新完成");
        setTimeout(function(){
          self.show("");
        },2000);
      }
    }

    mqttsub_ping(data) {
      this.show("連線中...");
    }

    mqttsub_pong(data) {
      this.show("連線完成");
    }

    mqttsub_waiting(data) {
      this.show("WebEye Pro 拍照中...");
    }

    mqttsub_uploading(data) {
      this.show("照片讀取中...");
    }

    mqttsub_upload(data) {
      var self = this;
      var url = data;
      this.show("照片讀取中...");
      fetch(url)
        .then(function (response) {
          return response.json();
        })
        .then(function (resp) {
          self.show(resp['name']);
          gimg.src = 'https://drive.google.com/uc?export=view&id=' + resp['id']
        });
    }

    show(text) {
      this.display.innerHTML = text;
    }
  }

  var ui = new UI('webeye01');
  await ui.connect();
}());