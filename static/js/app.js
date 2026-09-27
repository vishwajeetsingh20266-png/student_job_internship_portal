
const themeBtn = document.getElementById("themeBtn");
if(themeBtn){
  themeBtn.addEventListener("click",()=>{
    document.body.classList.toggle("light");
    localStorage.setItem("careerflow-theme",document.body.classList.contains("light")?"light":"dark");
  });
  if(localStorage.getItem("careerflow-theme")==="light") document.body.classList.add("light");
}
setTimeout(()=>document.querySelectorAll(".flash").forEach(x=>x.remove()),4000);
