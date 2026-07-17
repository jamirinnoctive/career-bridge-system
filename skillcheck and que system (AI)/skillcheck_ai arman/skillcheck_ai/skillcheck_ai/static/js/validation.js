
function validateReg(){
 let n=document.getElementById("name").value;
 if(n.length<3){ alert("Name too short"); return false;}
 return true;
}
