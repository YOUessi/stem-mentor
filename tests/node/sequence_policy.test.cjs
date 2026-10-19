"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const P=require("../../apps/web/lab/sequence_policy.js");
const hints=["观察相邻两项的差或比","从目标反推需要的量","特殊值能否反证你的猜想"];

test("independent mode stays quiet without help request",()=>{
  const x=P.decide({mode:"INDEPENDENT",stage:"START",helpRequested:false,hints});
  assert.equal(x.action,"WAIT");
  assert.equal(x.hintLevel,0);
  assert.doesNotMatch(x.message,/等差数列的通项|a_n=/);
});
test("logical analysis mode asks for structure instead of giving full method",()=>{
  const x=P.decide({mode:"ANALYZE",stage:"START",helpRequested:true,hints,hintLevel:1});
  assert.equal(x.action,"ASK_STRUCTURE");
  assert.match(x.message,/条件|相邻/);
  assert.equal(x.hintLevel,1);
});
test("stuck guidance changes to goal-backward query",()=>{
  const x=P.decide({mode:"GUIDE",stage:"STUCK",helpRequested:true,hints,hintLevel:1});
  assert.equal(x.action,"ASK_BACKWARD_GOAL");
  assert.match(x.message,/目标/);
});
test("repeated stuck request changes teaching strategy, no endless same question",()=>{
  const x=P.decide({mode:"GUIDE",stage:"STUCK",helpRequested:true,hints,hintLevel:3});
  assert.equal(x.action,"OFFER_ALTERNATIVE");
  assert.match(x.message,/换|另一/);
});
test("calculation stage checks known boundaries, not full solution",()=>{
  const x=P.decide({mode:"GUIDE",stage:"CALCULATION",helpRequested:true,hints,hintLevel:2});
  assert.equal(x.action,"CHECK_BOUNDARY");
  assert.match(x.message,/公比|退化|符号/);
});
test("reflection leads to independent near transfer check",()=>{
  const x=P.decide({mode:"GUIDE",stage:"REFLECTION",helpRequested:true,hints});
  assert.equal(x.action,"ASK_TRANSFER");
  assert.match(x.message,/新题|变式/);
});
test("clamps hint levels and rejects invalid mode/stage safely",()=>{
  const x=P.decide({mode:"WHAT",stage:"OTHER",helpRequested:true,hintLevel:200,hints});
  assert.ok(x.hintLevel<=3);
  assert.equal(x.engine,"RULE_BASED_SIMULATION");
  assert.ok(x.message);
});
