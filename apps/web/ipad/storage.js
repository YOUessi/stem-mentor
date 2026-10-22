"use strict";
/* Local IndexedDB vector-ink persistence. Never sends strokes to the backend. */
(function(root){
 const DB_NAME="stem-mentor-synthetic-ink-v1",STORE="documents",VERSION=1;
 let dbPromise=null;
 const key=(studentId,sessionId)=>"demo:"+studentId+":"+sessionId;
 function database(){
  if(dbPromise)return dbPromise;
  if(!root.indexedDB)return Promise.reject(Error("当前浏览器不支持 IndexedDB"));
  dbPromise=new Promise((resolve,reject)=>{
    const req=indexedDB.open(DB_NAME,VERSION);
    req.onupgradeneeded=()=>{
      const db=req.result;
      if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:"key"});
    };
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error||Error("无法打开本地笔迹存储"));
    req.onblocked=()=>reject(Error("本地存储正被其他标签页占用"));
  });
  dbPromise.catch(()=>{dbPromise=null});
  return dbPromise;
 }
 async function getRaw(identifier){
  const db=await database();
  return new Promise((resolve,reject)=>{
    const transaction=db.transaction(STORE,"readonly");
    const request=transaction.objectStore(STORE).get(identifier);
    request.onsuccess=()=>resolve(request.result?.data||null);
    request.onerror=()=>reject(request.error||Error("本地笔迹读取失败"));
  });
 }
 async function save(doc){
  root.MentorInkCore.validateDocument(doc,doc.studentId,doc.sessionId);
  const db=await database();
  const identifier=key(doc.studentId,doc.sessionId);
  // Atomic structured-clone write. No network request, no backend write.
  const payload=JSON.parse(JSON.stringify(doc));
  await new Promise((resolve,reject)=>{
    const transaction=db.transaction(STORE,"readwrite");
    const request=transaction.objectStore(STORE).put({key:identifier,
      data:payload,storedAt:new Date().toISOString()});
    transaction.oncomplete=resolve;
    transaction.onabort=()=>reject(transaction.error||Error("保存事务中止"));
    transaction.onerror=()=>reject(transaction.error||Error("保存笔迹失败"));
    request.onerror=()=>reject(request.error||Error("无法写入本地数据库"));
  });
  return true;
 }
 async function load(studentId,sessionId){
   const raw=await getRaw(key(studentId,sessionId));
   if(!raw)return null;
   return root.MentorInkCore.validateDocument(raw,studentId,sessionId);
 }
 root.MentorInkStore=Object.freeze({save,load,key,DB_NAME});
})(window);
